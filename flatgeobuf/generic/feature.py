from abc import ABCMeta
import json
from typing import Any, Callable, Dict, List, Optional, Union
from flatgeobuf.FlatGeobuf.GeometryType import GeometryType

from flatgeobuf.column_meta import ColumnMeta
from flatgeobuf.FlatGeobuf.ColumnType import ColumnType
from flatgeobuf.FlatGeobuf.Feature import Feature
from flatgeobuf.header_meta import HeaderMeta

from flatgeobuf.generic.geometry import ParsedGeometry, SimpleGeometry


class BaseFeature(metaclass=ABCMeta):
    def get_geometry(self) -> Optional[SimpleGeometry]:
        pass

    def get_properties(self) -> Any:
        pass

    def set_properties(self, properties: Dict[str, Union[bool, int, str, Any]]) -> Any:
        pass


CreateFeatureCallable = Callable[
    [SimpleGeometry, Dict[str, Union[bool, int, str, Any]]], BaseFeature
]

IProperties = Dict[str, Union[bool, int, str, Any]]


def from_feature(
    feature: Feature,
    header: HeaderMeta,
    create_geometry: Callable[[ParsedGeometry, GeometryType], SimpleGeometry],
    create_feature: Callable[
        [SimpleGeometry, Dict[str, Union[bool, int, str, Any]]], BaseFeature
    ],
) -> BaseFeature:
    columns = header.columns
    geometry = feature.Geometry()
    if not geometry:
        raise ValueError("Feature has no geometry")
    simple_geometry = create_geometry(geometry, header.geometry_type)
    properties = parse_properties(feature, columns)
    return create_feature(simple_geometry, properties)


def parse_properties(
    feature: Feature, columns: Optional[List[ColumnMeta]] = None
) -> Dict[str, Union[bool, int, str, Any]]:
    properties = {}
    if not columns or len(columns) == 0:
        return properties
    array = feature.PropertiesAsNumpy().tobytes()
    if array == 0:
        return properties
    view = memoryview(array)
    length = feature.PropertiesLength()
    offset = 0
    while offset < length:
        i = view[offset : offset + 2].cast("H")[0]
        offset += 2
        column = columns[i]
        name = column.name
        column_type = column.type
        if column_type == ColumnType.Bool:
            properties[name] = view[offset].cast("b")[0] == 1
            offset += 1
        elif column_type == ColumnType.Byte:
            properties[name] = view[offset].cast("b")[0]
            offset += 1
        elif column_type == ColumnType.UByte:
            properties[name] = view[offset].cast("B")[0]
            offset += 1
        elif column_type == ColumnType.Short:
            properties[name] = view[offset : offset + 2].cast("h")[0]
            offset += 2
        elif column_type == ColumnType.UShort:
            properties[name] = view[offset : offset + 2].cast("H")[0]
            offset += 2
        elif column_type == ColumnType.Int:
            properties[name] = view[offset : offset + 4].cast("i")[0]
            offset += 4
        elif column_type == ColumnType.UInt:
            properties[name] = view[offset : offset + 4].cast("I")[0]
            offset += 4
        elif column_type == ColumnType.Long:
            properties[name] = view[offset : offset + 8].cast("q")[0]

            offset += 8
        elif column_type == ColumnType.ULong:
            properties[name] = view[offset : offset + 8].cast("Q")[0]
            offset += 8
        elif column_type == ColumnType.Float:
            properties[name] = view[offset : offset + 4].cast("f")[0]
            offset += 4
        elif column_type == ColumnType.Double:
            properties[name] = view[offset : offset + 8].cast("d")[0]
            offset += 8
        elif column_type in (ColumnType.DateTime, ColumnType.String):
            str_length = view[offset : offset + 4].cast("I")[0]
            offset += 4
            str_value = view[offset : offset + str_length].tobytes().decode()
            properties[name] = str_value
            offset += str_length
        elif column_type == ColumnType.Json:
            str_length = view[offset : offset + 4].cast("I")[0]
            offset += 4
            str_value = view[offset : offset + str_length].tobytes().decode()
            properties[name] = json.loads(str_value)
            offset += str_length
        else:
            raise ValueError(f"Unknown type {column_type}")

    return properties
