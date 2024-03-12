from __future__ import annotations

from asyncio import StreamReader
from io import BufferedIOBase
from typing import AsyncGenerator, Generator

from geojson import Feature

from flatgeobuf.bbox_filter import BBoxFilter
from flatgeobuf.generic import HeaderMetaFn
from flatgeobuf.generic.featurecollection import deserialize as generic_deserialize
from flatgeobuf.generic.featurecollection import (
    deserialize_http as generic_deserialize_http,
)

# from flatgeobuf.generic.featurecollection import (
#     deserialize_stream as generic_deserialize_stream,
# )
from flatgeobuf.geojson.feature import from_feature
from flatgeobuf.packedrtree import Rect


def deserialize(
    data: BufferedIOBase,
    rect: Rect | None = None,
    header_meta_fn: HeaderMetaFn | None = None,
) -> Generator[Feature, None, None]:
    """Deserialize a FlatGeobuf byte stream to a GeoJSON FeatureCollection."""

    if rect:
        bbox_filter = BBoxFilter(rect)
        for feature in generic_deserialize(data, rect, from_feature, header_meta_fn):
            if bbox_filter.has_intersection(feature):
                yield feature
    else:
        for feature in generic_deserialize(data, rect, from_feature, header_meta_fn):
            yield feature


async def deserialize_stream(
    stream: StreamReader, header_meta_fn: HeaderMetaFn | None = None
) -> AsyncGenerator[Feature, None]:
    """Deserialize a FlatGeobuf async byte stream to a GeoJSON FeatureCollection."""

    raise NotImplementedError()
    # return generic_deserialize_stream(stream, from_feature, header_meta_fn)


async def deserialize_http(
    url: str, rect: Rect | None = None, header_meta_fn: HeaderMetaFn | None = None
) -> AsyncGenerator[Feature, None]:
    """Deserialize a FlatGeobuf HTTP resource to a GeoJSON FeatureCollection."""

    if rect:
        bbox_filter = BBoxFilter(rect)
        async for feature in generic_deserialize_http(
            url, rect, from_feature, header_meta_fn
        ):
            if bbox_filter.has_intersection(feature):
                yield feature
    else:
        async for feature in generic_deserialize_http(
            url, rect, from_feature, header_meta_fn
        ):
            yield feature
