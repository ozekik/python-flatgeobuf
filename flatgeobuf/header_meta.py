from __future__ import annotations

from dataclasses import dataclass
from typing import List

from flatgeobuf.column_meta import ColumnMeta
from flatgeobuf.crs_meta import CrsMeta
from flatgeobuf.FlatGeobuf.GeometryType import GeometryType
from flatgeobuf.FlatGeobuf.Header import Header


@dataclass
class HeaderMeta:
    geometry_type: GeometryType
    columns: List[ColumnMeta] | None
    envelope: List[float] | None  # Float64Array
    features_count: int
    index_node_size: int
    crs: CrsMeta | None
    title: str | None
    description: str | None
    metadata: str | None


def from_byte_buffer(bb: bytes | bytearray) -> HeaderMeta:
    header = Header.GetRootAsHeader(bb, 0)
    features_count = header.FeaturesCount()
    index_node_size = header.IndexNodeSize()

    columns = []
    for j in range(header.ColumnsLength()):
        column = header.Columns(j)
        if not column:
            raise ValueError("Column unexpectedly missing")
        # NOTE: FlatBuf returns bytes, not str
        column_name = column.Name()
        if not column_name:
            raise ValueError("Column name unexpectedly missing")
        columns.append(
            ColumnMeta(
                name=column_name.decode("utf-8"),
                type=column.Type(),
                title=column.Title(),
                description=column.Description(),
                width=column.Width(),
                precision=column.Precision(),
                scale=column.Scale(),
                nullable=column.Nullable(),
                unique=column.Unique(),
                primary_key=column.PrimaryKey(),
            )
        )

    crs = header.Crs()
    crs_meta = None
    if crs:
        crs_meta = CrsMeta(
            org=crs.Org(),
            code=crs.Code(),
            name=crs.Name(),
            description=crs.Description(),
            wkt=crs.Wkt(),
            code_string=crs.CodeString(),
        )

    header_meta = HeaderMeta(
        geometry_type=header.GeometryType(),
        columns=columns,
        envelope=None,
        features_count=features_count,
        index_node_size=index_node_size,
        crs=crs_meta,
        title=header.Title(),
        description=header.Description(),
        metadata=header.Metadata(),
    )

    return header_meta
