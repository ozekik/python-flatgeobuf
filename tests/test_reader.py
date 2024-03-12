from unittest import IsolatedAsyncioTestCase, TestCase

import geojson

from flatgeobuf.geojson.reader import (
    AsyncHTTPReader,
    HTTPReader,
    Reader,
    http_load,
    http_load_async,
    load,
)

FGB_URL = "https://raw.githubusercontent.com/flatgeobuf/flatgeobuf/master/test/data/countries.fgb"


class TestAsyncReader(IsolatedAsyncioTestCase):
    def setUp(self):
        with open("tests/data/countries.geojson", "r") as f:
            self.COUNTRIES_GEOJSON = geojson.load(f)

    async def test_http_load_async(self):
        result = await http_load_async(FGB_URL)
        self.assertDictEqual(result, self.COUNTRIES_GEOJSON)

    async def test_http_load_async_bbox(self):
        bbox = (-26.5699, 63.1191, -12.1087, 67.0137)
        result = await http_load_async(FGB_URL, bbox=bbox)
        ids = [feat.properties["id"] for feat in result.features]
        self.assertListEqual(ids, ["RUS", "ISL", "GRL"])

    async def test_async_http_reader(self):
        url = "https://raw.githubusercontent.com/flatgeobuf/flatgeobuf/master/test/data/countries.fgb"
        reader = AsyncHTTPReader(url)
        features = []
        async for feature in reader:
            features.append(feature)
        self.assertListEqual(features, self.COUNTRIES_GEOJSON.features)

        bbox = (-26.5699, 63.1191, -12.1087, 67.0137)
        reader = AsyncHTTPReader(FGB_URL, bbox=bbox)
        features = []
        async for feature in reader:
            features.append(feature)
        ids = [feat.properties["id"] for feat in features]
        self.assertListEqual(ids, ["RUS", "ISL", "GRL"])


class TestReader(TestCase):
    def setUp(self):
        with open("tests/data/countries.geojson", "r") as f:
            self.COUNTRIES_GEOJSON = geojson.load(f)

    def test_http_load(self):
        result = http_load(FGB_URL)
        self.assertDictEqual(result, self.COUNTRIES_GEOJSON)

    def test_http_load_bbox(self):
        bbox = (-26.5699, 63.1191, -12.1087, 67.0137)
        result = http_load(FGB_URL, bbox=bbox)
        ids = [feat.properties["id"] for feat in result.features]
        self.assertListEqual(ids, ["RUS", "ISL", "GRL"])

    def test_load(self):
        with open("tests/data/countries.fgb", "rb") as f:
            result = load(f)

        self.assertDictEqual(result, self.COUNTRIES_GEOJSON)

    def test_load_bbox(self):
        bbox = (-26.5699, 63.1191, -12.1087, 67.0137)

        with open("tests/data/countries.fgb", "rb") as f:
            result = load(f, bbox=bbox)

        ids = [feat.properties["id"] for feat in result.features]
        self.assertListEqual(ids, ["RUS", "ISL", "GRL"])

    def test_http_reader(self):
        reader = HTTPReader(FGB_URL)
        features = []
        for feature in reader:
            features.append(feature)
        self.assertListEqual(features, self.COUNTRIES_GEOJSON.features)

        bbox = (-26.5699, 63.1191, -12.1087, 67.0137)
        reader = HTTPReader(FGB_URL, bbox=bbox)
        features = []
        for feature in reader:
            features.append(feature)
        ids = [feat.properties["id"] for feat in features]
        self.assertListEqual(ids, ["RUS", "ISL", "GRL"])

    def test_reader(self):
        with open("tests/data/countries.fgb", "rb") as f:
            reader = Reader(f)
            features = []
            for feature in reader:
                features.append(feature)
            self.assertListEqual(features, self.COUNTRIES_GEOJSON.features)

            bbox = (-26.5699, 63.1191, -12.1087, 67.0137)
            reader = Reader(f, bbox=bbox)
            features = []
            for feature in reader:
                features.append(feature)
            ids = [feat.properties["id"] for feat in features]
            self.assertListEqual(ids, ["RUS", "ISL", "GRL"])