from __future__ import annotations

from logging import getLogger
from typing import Any, AsyncGenerator, List, Tuple

from flatgeobuf.config import Config
from flatgeobuf.constants import SIZE_PREFIX_LEN, magicbytes
from flatgeobuf.FlatGeobuf.Feature import Feature
from flatgeobuf.header_meta import HeaderMeta, from_byte_buffer
from flatgeobuf.http_range_client import BufferedHttpRangeClient
from flatgeobuf.packedrtree import (
    DEFAULT_NODE_SIZE,
    NODE_ITEM_BYTE_LEN,
    Rect,
    calc_tree_size,
    stream_search,
)

logger = getLogger(__name__)


async def merge_promises(
    promises: List[AsyncGenerator[Feature, Any]]
) -> AsyncGenerator[Feature, None]:
    for promise in promises:
        async for feature in promise:
            yield feature


class HttpReader:
    def __init__(
        self,
        header_client: BufferedHttpRangeClient,
        header: HeaderMeta,
        header_length: int,
        index_length: int,
    ):
        self.header_client = header_client
        self.header = header
        self.header_length = header_length
        self.index_length = index_length

    # Fetch the header, preparing the reader to read Feature data.
    # and potentially some opportunistic fetching of the index.
    @staticmethod
    async def open(url: str) -> HttpReader:
        # In reality, the header is probably less than half this size, but
        # better to overshoot and fetch an extra kb rather than have to issue
        # a second request.
        assumed_header_length = 2024

        header_client = BufferedHttpRangeClient(url)

        # Immediately following the header is the optional spatial index, we deliberately fetch
        # a small part of that to skip subsequent requests.
        def assumed_index_length() -> int:
            # The actual branching factor will be in the header, but since we
            # don't have the header yet, we just guess. The consequence of
            # getting this wrong isn't terminal, it only means we may be
            # fetching slightly more than we need or that we need to make an
            # extra request later.
            assumed_branching_factor = DEFAULT_NODE_SIZE

            # NOTE: each layer is exponentially larger
            prefetched_layers = 3

            result = 0
            for i in range(prefetched_layers):
                layer_width = assumed_branching_factor**i * NODE_ITEM_BYTE_LEN
                result += layer_width
            return result

        min_req_length = assumed_header_length + assumed_index_length()
        logger.debug(
            f"fetching header. min_req_length: {min_req_length} (assumed_header_length: {assumed_header_length}, assumed_index_length: {assumed_index_length()})",
        )

        bytes = await header_client.get_range(0, 8, min_req_length, "header")
        if not bytes[:3] == magicbytes[:3]:
            logger.error(f"bytes: {bytes} != {magicbytes}")
            raise ValueError("Not a FlatGeobuf file")
        logger.debug("magic bytes look good")

        bytes = await header_client.get_range(8, 4, min_req_length, "header")
        header_length = int.from_bytes(bytes, "little")
        HEADER_MAX_BUFFER_SIZE = 1048576 * 10
        if header_length > HEADER_MAX_BUFFER_SIZE or header_length < 8:
            # minimum size check avoids panic in FlatBuffers header decoding
            raise ValueError("Invalid header size")
        logger.debug(f"header_length: {header_length}")

        bytes = await header_client.get_range(
            12, header_length, min_req_length, "header"
        )
        bb = bytearray(bytes)  # bb = flatbuffers.ByteBuffer(bytes)
        header = from_byte_buffer(bb)

        index_length = calc_tree_size(header.features_count, header.index_node_size)

        logger.debug("completed: opening http reader")

        return HttpReader(header_client, header, header_length, index_length)

    async def select_bbox(self, rect: Rect) -> AsyncGenerator[Feature, None]:
        # Read R-Tree index and build filter for features within bbox
        length_before_tree = self.length_before_tree()

        buffered_client = self.header_client

        async def read_node(offset_into_tree: int, size: int) -> bytes:
            min_req_length = 0
            return await buffered_client.get_range(
                length_before_tree + offset_into_tree,
                size,
                min_req_length,
                "index",
            )

        batches: List[List[Tuple[int, int]]] = []
        current_batch: List[Tuple[int, int]] = []

        async for search_result in stream_search(
            self.header.features_count,
            self.header.index_node_size,
            rect,
            read_node,
        ):
            feature_offset, _, feature_length = search_result
            if not feature_length:
                logger.info("final feature")
                # Normally we get the feature length by subtracting between
                # adjacent nodes from the index, which we can't do for the
                # _very_ last feature in a dataset.
                #
                # We could *guess* the size, but we'd risk overshooting the length,
                # which will cause some webservers to return HTTP 416: Unsatisfiable range
                #
                # So instead we fetch only the final features byte length, stored in the
                # first 4 bytes.
                feature_length = 4

            if not current_batch:
                current_batch.append((feature_offset, feature_length))
                continue

            prev_feature = current_batch[-1]
            gap = feature_offset - (prev_feature[0] + prev_feature[1])

            if gap > Config.global_instance.extra_request_threshold():
                logger.info(
                    f"Pushing new feature batch, since gap {gap} was too large",
                )
                batches.append(current_batch)
                current_batch = []

            current_batch.append((feature_offset, feature_length))

        self.header_client.log_usage("header+index")

        if current_batch:
            batches.append(current_batch)

        promises: List[AsyncGenerator[Feature, Any]] = [
            self.read_feature_batch(batch) for batch in batches
        ]

        # Fetch all batches concurrently, yielding features as they become
        # available, meaning the results may be intermixed.
        async for promise in merge_promises(promises):
            yield promise

    def length_before_tree(self) -> int:
        # FGB Layout is: [magicbytes (fixed), headerLength (i32), header (variable), Tree (variable), Features (variable)]
        return len(magicbytes) + SIZE_PREFIX_LEN + self.header_length

    def length_before_features(self) -> int:
        return self.length_before_tree() + self.index_length

    def build_feature_client(self) -> BufferedHttpRangeClient:
        return BufferedHttpRangeClient(self.header_client.http_client)

    async def read_feature_batch(
        self, batch: List[Tuple[int, int]]
    ) -> AsyncGenerator[Feature, None]:
        first_feature_offset = batch[0][0]
        last_feature_offset, last_feature_length = batch[-1]

        batch_start = first_feature_offset
        batch_end = last_feature_offset + last_feature_length
        batch_size = batch_end - batch_start

        # A new feature client is needed for each batch to own the underlying buffer as features are yielded.
        feature_client = self.build_feature_client()

        min_feature_req_length = batch_size
        for feature_offset, _ in batch:
            yield await self.read_feature(
                feature_client,
                feature_offset,
                min_feature_req_length,
            )
            # Only set min_feature_req_length for the first request.
            #
            # This should only affect a batch that contains the final feature, otherwise
            # we've calculated `batch_size` to get all the data we need for the batch.
            # For the very final feature in a dataset, we don't know it's length, so we
            # will end up executing an extra request for that batch.
            min_feature_req_length = 0
        feature_client.log_usage("feature")

    async def read_feature(
        self,
        feature_client: BufferedHttpRangeClient,
        feature_offset: int,
        min_feature_req_length: int,
    ) -> Feature:
        offset = feature_offset + self.length_before_features()

        bytes = await feature_client.get_range(
            offset,
            4,
            min_feature_req_length,
            "feature length",
        )
        feature_length = int.from_bytes(bytes, "little")

        byte_buffer = await feature_client.get_range(
            offset + 4,
            feature_length,
            min_feature_req_length,
            "feature data",
        )
        bytes = bytearray(byte_buffer)
        bytes_aligned = bytearray(feature_length + SIZE_PREFIX_LEN)
        bytes_aligned[SIZE_PREFIX_LEN:] = bytes
        bb = bytearray(bytes_aligned)
        bb = bb[SIZE_PREFIX_LEN:]
        return Feature.GetRootAsFeature(bb)
