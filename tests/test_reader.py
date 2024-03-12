from unittest import IsolatedAsyncioTestCase, TestCase

import geojson

from flatgeobuf.geojson.reader import (
    AsyncHTTPReader,
    HTTPReader,
    Reader,
    load_http,
    load_http_async,
    load,
)

FGB_URL = "https://raw.githubusercontent.com/flatgeobuf/flatgeobuf/master/test/data/countries.fgb"


class TestAsyncReader(IsolatedAsyncioTestCase):
    def setUp(self):
        with open("tests/data/countries.geojson", "r") as f:
            self.COUNTRIES_GEOJSON = geojson.load(f)

    async def test_load_http_async(self):
        result = await load_http_async(FGB_URL)
        self.assertDictEqual(result, self.COUNTRIES_GEOJSON)

    async def test_load_http_async_bbox(self):
        bbox = (-26.5699, 63.1191, -12.1087, 67.0137)
        result = await load_http_async(FGB_URL, bbox=bbox)
        ids = [feat.properties["id"] for feat in result.features]
        try:
            import shapely  # noqa: F401

            self.assertListEqual(ids, ["ISL"])
        except:
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
        try:
            import shapely  # noqa: F401

            self.assertListEqual(ids, ["ISL"])
        except:
            self.assertListEqual(ids, ["RUS", "ISL", "GRL"])


class TestReader(TestCase):
    def setUp(self):
        with open("tests/data/countries.geojson", "r") as f:
            self.COUNTRIES_GEOJSON = geojson.load(f)

    def test_load_http(self):
        result = load_http(FGB_URL)
        self.assertDictEqual(result, self.COUNTRIES_GEOJSON)

    def test_load_http_bbox(self):
        bbox = (-26.5699, 63.1191, -12.1087, 67.0137)
        result = load_http(FGB_URL, bbox=bbox)
        ids = [feat.properties["id"] for feat in result.features]
        try:
            import shapely  # noqa: F401

            self.assertListEqual(ids, ["ISL"])
        except:
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
        try:
            import shapely  # noqa: F401

            self.assertListEqual(ids, ["ISL"])
        except:
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
        try:
            import shapely  # noqa: F401

            self.assertListEqual(ids, ["ISL"])
        except:
            self.assertListEqual(ids, ["RUS", "ISL", "GRL"])

    def test_reader(self):
        features = []

        with open("tests/data/countries.fgb", "rb") as f:
            reader = Reader(f)

            for feature in reader:
                features.append(feature)

        self.assertListEqual(features, self.COUNTRIES_GEOJSON.features)

        features = []
        bbox = (-26.5699, 63.1191, -12.1087, 67.0137)

        with open("tests/data/countries.fgb", "rb") as f:
            reader = Reader(f, bbox=bbox)

            for feature in reader:
                features.append(feature)

        ids = [feat.properties["id"] for feat in features]
        try:
            import shapely  # noqa: F401

            self.assertListEqual(ids, ["ISL"])
        except:
            self.assertListEqual(ids, ["RUS", "ISL", "GRL"])
