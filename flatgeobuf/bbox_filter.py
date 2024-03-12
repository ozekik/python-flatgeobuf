from geojson import Feature

from flatgeobuf.packedrtree import Rect

try:
    import shapely.geometry
    import shapely.prepared
except ImportError:
    shapely = None


# NOTE: Assuming GeoJSON
class BBoxFilter:
    def __init__(self, bbox: Rect):
        if shapely is None:
            return

        prep_bbox = shapely.prepared.prep(shapely.geometry.box(*bbox, ccw=True))
        self.prep_bbox = prep_bbox

    def has_intersection(self, feature: Feature) -> bool:
        """Check if a feature intersects with a bbox."""

        # NOTE: If shapely is not installed, we assume that the feature intersects
        if shapely is None:
            return True

        shape = shapely.geometry.shape(feature.geometry)

        return self.prep_bbox.intersects(shape)
