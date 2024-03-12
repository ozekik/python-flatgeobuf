from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Callable, List, Optional, TypedDict, Union, cast

from flatgeobuf.FlatGeobuf.Geometry import Geometry
from flatgeobuf.FlatGeobuf.GeometryType import GeometryType


class ParsedGeometry(TypedDict, total=False):
    xy: List[float] | None
    z: List[float] | None
    ends: List[int] | None
    parts: List["ParsedGeometry"] | None
    type: GeometryType | None


class SimpleGeometry(metaclass=ABCMeta):
    @abstractmethod
    def get_flat_coordinates(self) -> List[float]:
        pass

    @abstractmethod
    def get_type(self) -> str:
        pass


class BasePolygon(SimpleGeometry):
    @abstractmethod
    def get_ends(self) -> List[int]:
        pass


class BaseMultiLineString(SimpleGeometry):
    @abstractmethod
    def get_ends(self) -> List[int]:
        pass


class BaseMultiPolygon(SimpleGeometry):
    @abstractmethod
    def get_endss(self) -> List[List[int]]:
        pass

    @abstractmethod
    def get_polygons(self) -> List[BasePolygon]:
        pass


CreateGeometryCallable = Callable[
    [Union[Geometry, None], GeometryType], Optional[SimpleGeometry]
]


def build_geometry(parsed_geometry: ParsedGeometry) -> Geometry:
    raise NotImplementedError()
    # xy = parsed_geometry.get("xy", None)
    # z = parsed_geometry.get("z", None)
    # ends = parsed_geometry.get("ends", None)
    # parts = parsed_geometry.get("parts", None)
    # type = parsed_geometry.get("type", None)

    # if parts:
    #     part_offsets = [build_geometry(part) for part in parts]
    #     parts_offset = Geometry.create_parts_vector(part_offsets)
    #     geometry = Geometry(xy=[], z=[], ends=[], parts=parts_offset, type=type)
    #     return geometry

    # xy_offset = Geometry.create_xy_vector(xy)
    # z_offset = Geometry.create_z_vector(z) if z else None
    # ends_offset = Geometry.create_ends_vector(ends) if ends else None

    # geometry = Geometry(xy=xy_offset, z=z_offset, ends=ends_offset, type=type)
    # return geometry


def flat(
    a: List[Union[List[float], float]], xy: List[float], z: List[float]
) -> Optional[List[float]]:
    if len(a) == 0:
        return None

    if isinstance(a[0], list):
        for sa in a:
            flat(sa, xy, z)
    else:
        if len(a) == 2:
            xy.extend(a)
        else:
            xy.extend(a[:2])
            z.append(a[2])


def parse_geometry(
    geometry: SimpleGeometry, header_geom_type: GeometryType
) -> ParsedGeometry:
    xy = None
    ends = None
    parts = None

    type = header_geom_type
    if type == GeometryType.Unknown:
        type = to_geometry_type(geometry.get_type())

    if type == GeometryType.MultiLineString:
        if hasattr(geometry, "get_flat_coordinates"):
            xy = geometry.get_flat_coordinates()
        mls_ends = cast(BaseMultiLineString, geometry).get_ends()
        if len(mls_ends) > 1:
            ends = [e >> 1 for e in mls_ends]
    elif type == GeometryType.Polygon:
        if hasattr(geometry, "get_flat_coordinates"):
            xy = geometry.get_flat_coordinates()
        p_ends = cast(BasePolygon, geometry).get_ends()
        if len(p_ends) > 1:
            ends = [e >> 1 for e in p_ends]
    elif type == GeometryType.MultiPolygon:
        mp = cast(BaseMultiPolygon, geometry)
        parts = [parse_geometry(p, GeometryType.Polygon) for p in mp.get_polygons()]
    else:
        if hasattr(geometry, "get_flat_coordinates"):
            xy = geometry.get_flat_coordinates()

    parsed_geometry: ParsedGeometry = {
        "xy": xy,
        "ends": ends,
        "type": type,
        "parts": parts,
    }

    return parsed_geometry


def pair_flat_coordinates(
    xy: List[float], z: Optional[List[float]] = None
) -> List[List[float]]:
    new_array = []
    for i in range(0, len(xy), 2):
        a = [xy[i], xy[i + 1]]
        if z:
            a.append(z[i >> 1])
        new_array.append(a)
    return new_array


def to_geometry_type(name: Optional[str]) -> GeometryType:
    if not name:
        return GeometryType.Unknown
    return getattr(GeometryType, name)
