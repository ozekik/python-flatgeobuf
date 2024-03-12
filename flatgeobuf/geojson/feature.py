from geojson import Feature as GeoJsonFeature

from flatgeobuf.FlatGeobuf.Feature import Feature
from flatgeobuf.generic.feature import BaseFeature, parse_properties
from flatgeobuf.geojson.geometry import from_geometry
from flatgeobuf.header_meta import HeaderMeta


class IGeoJsonFeature(BaseFeature, GeoJsonFeature):
    pass


def from_feature(feature: Feature, header: HeaderMeta) -> IGeoJsonFeature:
    columns = header.columns
    geometry = from_geometry(feature.Geometry(), header.geometry_type)
    geo_json_feature = GeoJsonFeature(
        type="Feature",
        geometry=geometry,
        properties=parse_properties(feature, columns),
    )
    return geo_json_feature
