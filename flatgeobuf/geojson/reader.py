from __future__ import annotations

import asyncio
from io import BufferedIOBase

from geojson import FeatureCollection

from flatgeobuf.generic import HeaderMetaFn
from flatgeobuf.geojson.featurecollection import deserialize, deserialize_http
from flatgeobuf.packedrtree import Rect


def load(file: BufferedIOBase, *, bbox: Rect | None = None) -> FeatureCollection:
    reader = Reader(file, bbox=bbox)
    features = list(reader)
    return FeatureCollection(features)


def load_http(url: str, *, bbox: Rect | None = None) -> FeatureCollection:
    reader = HTTPReader(url, bbox=bbox)
    features = list(reader)
    return FeatureCollection(features)


async def load_http_async(url: str, *, bbox: Rect | None = None) -> FeatureCollection:
    reader = AsyncHTTPReader(url, bbox=bbox)
    features = [feature async for feature in reader]
    return FeatureCollection(features)


class Reader:
    def __init__(
        self,
        file: BufferedIOBase,
        *,
        bbox: Rect | None = None,
        header_meta_fn: HeaderMetaFn | None = None,
    ):
        self.file = file
        self.rect = bbox
        self.header_meta_fn = header_meta_fn

    def __iter__(self):
        for feature in deserialize(self.file, self.rect):
            yield feature


class AsyncHTTPReader:
    def __init__(
        self,
        url: str,
        *,
        bbox: Rect | None = None,
        header_meta_fn: HeaderMetaFn | None = None,
    ):
        self.url = url
        self.rect = bbox
        self.header_meta_fn = header_meta_fn

    async def __aiter__(self):
        async for feature in deserialize_http(self.url, self.rect):
            yield feature


class HTTPReader:
    def __init__(
        self,
        url: str,
        *,
        bbox: Rect | None = None,
        header_meta_fn: HeaderMetaFn | None = None,
    ):
        self.url = url
        self.rect = bbox
        self.header_meta_fn = header_meta_fn

    def __iter__(self):
        loop = asyncio.new_event_loop()
        features = deserialize_http(self.url, self.rect)
        while True:
            try:
                yield loop.run_until_complete(features.__anext__())
            except StopAsyncIteration:
                break
