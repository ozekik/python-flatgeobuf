from io import BufferedIOBase
from typing import AsyncGenerator, Union

from geojson import FeatureCollection

from flatgeobuf.generic import HeaderMetaFn
from flatgeobuf.geojson.feature import IGeoJsonFeature
from flatgeobuf.geojson.featurecollection import deserialize as fc_deserialize
from flatgeobuf.geojson.featurecollection import deserialize_http as fc_deserialize_http
from flatgeobuf.geojson.featurecollection import (
    deserialize_stream as fc_deserialize_stream,
)
from flatgeobuf.geojson.reader import (
    AsyncHTTPReader,  # noqa: F401
    HTTPReader,  # noqa: F401
    Reader,  # noqa: F401
    load,  # noqa: F401
    load_http,  # noqa: F401
    load_http_async,  # noqa: F401
)
from flatgeobuf.packedrtree import Rect


def deserialize(
    input: Union[BufferedIOBase, str, AsyncGenerator[IGeoJsonFeature, None]],
    rect: Rect | None = None,
    header_meta_fn: HeaderMetaFn | None = None,
) -> Union[FeatureCollection, AsyncGenerator[IGeoJsonFeature, None]]:
    if isinstance(input, BufferedIOBase):
        return fc_deserialize(input, header_meta_fn)
    elif isinstance(input, str):
        return fc_deserialize_http(input, rect, header_meta_fn)
    else:
        return fc_deserialize_stream(input, header_meta_fn)
