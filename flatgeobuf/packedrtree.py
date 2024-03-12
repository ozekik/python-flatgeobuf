from __future__ import annotations

import math
from logging import getLogger
from typing import Annotated, AsyncGenerator, List, Tuple, Union

from .config import Config

logger = getLogger(__name__)

NODE_ITEM_BYTE_LEN: int = 8 * 4 + 8

DEFAULT_NODE_SIZE = 16

Rect = Union[Tuple[float, float, float, float], Annotated[list[float], 4]]
SearchResult = Tuple[int, int, Union[int, None]]


def calc_tree_size(num_items: int, node_size: int) -> int:
    node_size = min(max(int(node_size), 2), 65535)
    n = num_items
    num_nodes = n
    while n != 1:
        n = math.ceil(n / node_size)
        num_nodes += n
    return num_nodes * NODE_ITEM_BYTE_LEN


def generate_level_bounds(num_items: int, node_size: int) -> List[Tuple[int, int]]:
    if node_size < 2:
        raise ValueError("Node size must be at least 2")
    if num_items == 0:
        raise ValueError("Number of items must be greater than 0")

    n = num_items
    num_nodes = n
    level_num_nodes = [n]
    while n != 1:
        n = math.ceil(n / node_size)
        num_nodes += n
        level_num_nodes.append(n)

    level_offsets = []
    n = num_nodes
    for size in level_num_nodes:
        level_offsets.append(n - size)
        n -= size

    level_bounds = []
    for i in range(len(level_num_nodes)):
        level_bounds.append((level_offsets[i], level_offsets[i] + level_num_nodes[i]))
    return level_bounds


async def stream_search(
    num_items: int, node_size: int, rect: Rect, read_node
) -> AsyncGenerator[SearchResult, None]:
    class NodeRange:
        def __init__(self, nodes: Tuple[int, int], level: int):
            self._level = level
            self.nodes = nodes

        def level(self) -> int:
            return self._level

        def start_node_idx(self) -> int:
            return self.nodes[0]

        def end_node_idx(self) -> int:
            return self.nodes[1]

        def extend_end_node_idx(self, new_idx: int):
            assert new_idx > self.nodes[1]
            self.nodes = (self.nodes[0], new_idx)

        def __str__(self) -> str:
            return f"[NodeRange level: {self._level}, nodes: {self.nodes[0]}-{self.nodes[1]}]"

    min_x, min_y, max_x, max_y = rect
    level_bounds = generate_level_bounds(num_items, node_size)
    first_leaf_node_idx = level_bounds[0][0]

    root_node_range = NodeRange((0, 1), len(level_bounds) - 1)

    queue = [root_node_range]

    while queue:
        node_range = queue.pop(0)

        logger.debug(f"popped node: {node_range}, queue_length: {len(queue)}")

        node_range_start_idx = node_range.start_node_idx()
        is_leaf_node = node_range_start_idx >= first_leaf_node_idx

        # find the end index of the node
        _node_range_end_idx = node_range.end_node_idx()
        level_bound = level_bounds[node_range.level()][1]
        node_idx = min(_node_range_end_idx + node_size, level_bound)
        if is_leaf_node and node_idx < level_bound:
            # We can infer the length of *this* feature by getting the start of the *next*
            # feature, so we get an extra node.
            # This approach doesn't work for the final node in the index,
            # but in that case we know that the feature runs to the end of the FGB file and
            # could make an open ended range request to get "the rest of the data".
            node_range_end_idx = node_idx + 1
        else:
            node_range_end_idx = node_idx

        num_nodes_in_range = node_range_end_idx - node_range_start_idx

        buffer = await read_node(
            node_range_start_idx * NODE_ITEM_BYTE_LEN,
            num_nodes_in_range * NODE_ITEM_BYTE_LEN,
        )

        data_view = memoryview(buffer)

        for node_idx in range(node_range_start_idx, node_range_end_idx):
            node_idx_in_data_view = node_idx - node_range_start_idx
            data_view_byte_start = node_idx_in_data_view * NODE_ITEM_BYTE_LEN

            # TODO: Enforce little endian
            if (
                max_x
                < data_view[data_view_byte_start : data_view_byte_start + 8].cast("d")[
                    0
                ]
            ):
                continue
            if (
                max_y
                < data_view[data_view_byte_start + 8 : data_view_byte_start + 16].cast(
                    "d"
                )[0]
            ):
                continue
            if (
                min_x
                > data_view[data_view_byte_start + 16 : data_view_byte_start + 24].cast(
                    "d"
                )[0]
            ):
                continue
            if (
                min_y
                > data_view[data_view_byte_start + 24 : data_view_byte_start + 32].cast(
                    "d"
                )[0]
            ):
                continue

            offset = data_view[
                data_view_byte_start + 32 : data_view_byte_start + 40
            ].cast("q")[0]

            if is_leaf_node:
                feature_byte_offset = offset
                feature_length = None
                if node_idx < num_items - 1:
                    next_pos = (node_idx_in_data_view + 1) * NODE_ITEM_BYTE_LEN
                    next_offset = data_view[next_pos + 32 : next_pos + 40].cast("q")[0]
                    feature_length = next_offset - feature_byte_offset
                feature_idx = node_idx - first_leaf_node_idx
                yield (feature_byte_offset, feature_idx, feature_length)
                continue

            first_child_node_idx = offset

            extra_request_threshold_nodes = (
                Config.global_instance.extra_request_threshold() // NODE_ITEM_BYTE_LEN
            )

            nearest_node_range = queue[-1] if queue else None
            if (
                nearest_node_range
                and nearest_node_range.level() == node_range.level() - 1
                and first_child_node_idx
                < nearest_node_range.end_node_idx() + extra_request_threshold_nodes
            ):
                nearest_node_range.extend_end_node_idx(first_child_node_idx)
                continue

            new_node_range = NodeRange(
                (first_child_node_idx, first_child_node_idx + 1), node_range.level() - 1
            )

            if (
                nearest_node_range
                and nearest_node_range.level() == new_node_range.level()
            ):
                logger.info(
                    f"Same level, but too far away. Pushing new request for node_idx: {first_child_node_idx} rather than merging with distant {nearest_node_range}"
                )
            else:
                logger.info(
                    f"Pushing new level for {new_node_range} onto queue with nearest_node_range: {nearest_node_range} since there's not already a range for this level."
                )

            queue.append(new_node_range)
