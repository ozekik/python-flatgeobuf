from __future__ import annotations

from asyncio import StreamReader
from io import BufferedIOBase
from logging import getLogger
from typing import Any, AsyncGenerator, Callable, Generator, Optional, Union

from flatgeobuf.file_reader import FileReader
from flatgeobuf.FlatGeobuf.Feature import Feature
from flatgeobuf.generic.feature import BaseFeature
from flatgeobuf.header_meta import HeaderMeta
from flatgeobuf.http_reader import HttpReader
from flatgeobuf.packedrtree import Rect

logger = getLogger(__name__)

FromFeatureFn = Callable[[Feature, HeaderMeta], BaseFeature]
ReadFn = Callable[[int, str], Union[bytes, bytearray]]
HeaderMetaFn = Callable[[HeaderMeta], None]


# def deserialize(
#     data: BufferedIOBase,
#     from_feature: FromFeatureFn,
#     header_meta_fn: HeaderMetaFn | None = None,
# ) -> List[BaseFeature]:
#     """Deserialize a FlatGeobuf byte stream to a list of BaseFeature."""

#     if not data.read(3) == magicbytes[:3]:
#         raise ValueError("Not a FlatGeobuf file")

#     bb = data
#     bb.seek(len(magicbytes))
#     header_length = int.from_bytes(bb.read(4), "little")
#     bb.seek(len(magicbytes) + SIZE_PREFIX_LEN)

#     header_bytes = bb.read(header_length)
#     header_meta = from_byte_buffer(header_bytes)

#     logger.debug(f"header_meta: {header_meta}")

#     if header_meta_fn:
#         header_meta_fn(header_meta)

#     offset = len(magicbytes) + SIZE_PREFIX_LEN + header_length
#     index_node_size = header_meta.index_node_size
#     features_count = header_meta.features_count

#     if index_node_size > 0:
#         offset += calc_tree_size(features_count, index_node_size)

#     features = []

#     # Get the buffer size
#     bb.seek(0, os.SEEK_END)
#     buffer_size = bb.tell()
#     logger.debug(f"offset: {offset}, buffer_size: {buffer_size}")

#     while offset < buffer_size:
#         bb.seek(offset)
#         feature_length = int.from_bytes(bb.read(4), "little")

#         bb.seek(offset + SIZE_PREFIX_LEN)
#         feature_bytes = bb.read(feature_length)
#         feature = Feature.GetRootAsFeature(feature_bytes)
#         features.append(from_feature(feature, header_meta))

#         offset += SIZE_PREFIX_LEN + feature_length

#     return features


def deserialize(
    data: BufferedIOBase,
    rect: Rect | None,
    from_feature: FromFeatureFn,
    header_meta_fn: HeaderMetaFn | None = None,
) -> Generator[Any, None, None]:
    """Deserialize a FlatGeobuf byte stream to a list of BaseFeature."""

    reader = FileReader.load(data)

    logger.debug("opened reader")

    if header_meta_fn:
        header_meta_fn(reader.header)

    if not rect:
        rect = [-float("inf"), -float("inf"), float("inf"), float("inf")]

    for feature in reader.select_bbox(rect):
        yield from_feature(feature, reader.header)


async def deserialize_stream(
    stream: StreamReader,
    from_feature: FromFeatureFn,
    header_meta_fn: HeaderMetaFn | None = None,
) -> AsyncGenerator[Any, None]:
    """Deserialize a FlatGeobuf async byte stream to a list of BaseFeature."""

    raise NotImplementedError()
    # reader = slice(stream)

    # async def read(size: int, purpose: str) -> bytes:
    #     return await reader.slice(size)

    # bytes_data = bytes(await read(8, "magic bytes"))
    # if not all(bytes_data[:3] == magicbytes[:3]):
    #     raise ValueError("Not a FlatGeobuf file")

    # bytes_data = bytes(await read(4, "header length"))
    # bb = flatbuffers.ByteBuffer(bytes_data)

    # header_length = bb.readUint32(0)
    # bytes_data = bytes(await read(header_length, "header data"))
    # bb = flatbuffers.ByteBuffer(bytes_data)

    # header_meta = from_byte_buffer(bb)
    # if header_meta_fn:
    #     header_meta_fn(header_meta)

    # index_node_size = header_meta.index_node_size
    # features_count = header_meta.features_count
    # if index_node_size > 0:
    #     tree_size = calc_tree_size(features_count, index_node_size)
    #     await read(tree_size, "entire index, w/o rect")

    # feature = None
    # while feature := await read_feature(read, header_meta, from_feature):
    #     yield feature


async def deserialize_http(
    url: str,
    rect: Rect | None,
    from_feature: FromFeatureFn,
    header_meta_fn: HeaderMetaFn | None = None,
) -> AsyncGenerator[Any, None]:
    """Deserialize a FlatGeobuf HTTP resource to a list of BaseFeature."""

    reader = await HttpReader.open(url)

    logger.debug("opened reader")

    if header_meta_fn:
        header_meta_fn(reader.header)

    if not rect:
        rect = [-float("inf"), -float("inf"), float("inf"), float("inf")]

    async for feature in reader.select_bbox(rect):
        yield from_feature(feature, reader.header)


async def read_feature(
    read: ReadFn, header_meta: HeaderMeta, from_feature: FromFeatureFn
) -> Optional[BaseFeature]:
    raise NotImplementedError()

    # bytes = bytes(await read(4, "feature length"))
    # if len(bytes) == 0:
    #     return None
    # bb = flatbuffers.ByteBuffer(bytes)
    # feature_length = bb.readUint32(0)
    # bytes = bytes(await read(feature_length, "feature data"))
    # bytes_aligned = bytes(feature_length + 4)
    # bytes_aligned[4:] = bytes
    # bb = flatbuffers.ByteBuffer(bytes_aligned)
    # bb.seek(SIZE_PREFIX_LEN)
    # feature = Feature.GetRootAsFeature(bb)

    # return from_feature(feature, header_meta)
