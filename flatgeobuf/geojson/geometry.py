from __future__ import annotations

from typing import List, cast

from geojson import (
    GeometryCollection,
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
)

from flatgeobuf.FlatGeobuf.Geometry import Geometry
from flatgeobuf.FlatGeobuf.GeometryType import GeometryType
from flatgeobuf.generic.geometry import (
    ParsedGeometry,
    flat,
    pair_flat_coordinates,
    to_geometry_type,
)


def parse_geometry(
    geometry: (
        Point | MultiPoint | LineString | MultiLineString | Polygon | MultiPolygon
    ),
) -> ParsedGeometry:
    cs = geometry.coordinates
    xy = []
    z = []
    ends = None
    parts = None
    type = to_geometry_type(geometry.type)
    end = 0
    if geometry.type == "Point":
        flat(cs, xy, z)
    elif geometry.type in ["MultiPoint", "LineString"]:
        flat(cs, xy, z)
    elif geometry.type in ["MultiLineString", "Polygon"]:
        css = cs
        flat(css, xy, z)
        if len(css) > 1:
            ends = [end + len(c) for c in css]
    elif geometry.type == "MultiPolygon":
        csss = cs
        geometries = [
            cast(Polygon, {"type": "Polygon", "coordinates": coordinates})
            for coordinates in csss
        ]
        parts = [parse_geometry(geometry) for geometry in geometries]

    parsed_geometry: ParsedGeometry = {
        "xy": xy,
        "z": z if len(z) > 0 else None,
        "ends": ends,
        "type": type,
        "parts": parts,
    }
    return parsed_geometry


def parse_gc(geometry: GeometryCollection) -> ParsedGeometry:
    type = to_geometry_type(geometry.type)
    parts = []
    for g in geometry.geometries:
        if g.type == "GeometryCollection":
            parts.append(parse_gc(g))
        else:
            parts.append(parse_geometry(g))

    parsed_geometry: ParsedGeometry = {
        "type": type,
        "parts": parts,
    }
    return parsed_geometry


def extract_parts(xy: List[float], z: List[float] | None, ends: List[int] | None):
    if ends is None or len(ends) == 0:
        return [pair_flat_coordinates(xy, z)]

    s = 0
    xy_slices = [xy[s : (s := e << 1)] for e in ends]

    z_slices = None
    if z:
        s = 0
        z_slices = [z[s : (s := e)] for e in ends]

    return [
        pair_flat_coordinates(xy, z_slices[i] if z_slices else None)
        for i, xy in enumerate(xy_slices)
    ]


def to_geojson_coordinates(geometry: Geometry, type: GeometryType):
    xy = geometry.XyAsNumpy()
    if isinstance(xy, int) and xy == 0:
        raise ValueError("Geometry has no xy coordinates")
    else:
        xy = xy.tolist()

    z = geometry.ZAsNumpy()
    z = z.tolist() if not (isinstance(z, int) and z == 0) else None

    if type == GeometryType.Point:
        a = list(xy)
        if z:
            a.append(z[0])
        return a
    elif type in [GeometryType.MultiPoint, GeometryType.LineString]:
        return pair_flat_coordinates(xy, z)
    elif type in [GeometryType.MultiLineString, GeometryType.Polygon]:
        ends = geometry.EndsAsNumpy()
        ends = ends.tolist() if not (isinstance(ends, int) and ends == 0) else None
        return extract_parts(xy, z, ends)


def from_geometry(geometry: Geometry, header_type: GeometryType):
    type = header_type

    if type == GeometryType.Unknown:
        type = geometry.Type()

    if type == GeometryType.GeometryCollection:
        geometries = []

        for i in range(geometry.PartsLength()):
            part = geometry.Parts(i)
            part_type = part.Type()
            geometries.append(from_geometry(part, part_type))

        return GeometryCollection(geometries)

    elif type == GeometryType.MultiPolygon:
        geometries = []

        for i in range(geometry.PartsLength()):
            geometries.append(from_geometry(geometry.Parts(i), GeometryType.Polygon))

        return MultiPolygon([g["coordinates"] for g in geometries])

    coordinates = to_geojson_coordinates(geometry, type)

    # NOTE: Modified
    geometry_type = next(filter(lambda x: x[1] == type, GeometryType.__dict__.items()))[
        0
    ]

    return {"type": geometry_type, "coordinates": coordinates}
