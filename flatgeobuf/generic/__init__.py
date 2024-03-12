from __future__ import annotations

from asyncio import StreamReader
from io import BufferedIOBase
from typing import AsyncGenerator, List, Union

from flatgeobuf.FlatGeobuf.ColumnType import ColumnType
from flatgeobuf.FlatGeobuf.GeometryType import GeometryType
from flatgeobuf.generic.feature import BaseFeature
from flatgeobuf.generic.featurecollection import HeaderMetaFn  # noqa: F401
from flatgeobuf.generic.featurecollection import FromFeatureFn
from flatgeobuf.generic.featurecollection import deserialize as deserialize_buffer
from flatgeobuf.generic.featurecollection import deserialize_http, deserialize_stream
from flatgeobuf.packedrtree import Rect


def deserialize(
    input: Union[BufferedIOBase, StreamReader, str],
    from_feature: FromFeatureFn,
    rect: Rect | None = None,
) -> Union[List[BaseFeature], AsyncGenerator[BaseFeature, None]]:
    if isinstance(input, BufferedIOBase):
        return deserialize_buffer(input, from_feature)
    elif isinstance(input, StreamReader):
        return deserialize_stream(input, from_feature)
    else:
        return deserialize_http(input, rect, from_feature)


__all__ = [
    "GeometryType",
    "ColumnType",
    "deserialize",
    # "serialize"
]
