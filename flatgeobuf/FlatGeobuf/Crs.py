# automatically generated by the FlatBuffers compiler, do not modify

# namespace: FlatGeobuf

import flatbuffers
from flatbuffers.compat import import_numpy
from typing import Any
from typing import Optional
np = import_numpy()

class Crs(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset: int = 0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = Crs()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsCrs(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    # Crs
    def Init(self, buf: bytes, pos: int):
        self._tab = flatbuffers.table.Table(buf, pos)

    # Crs
    def Org(self) -> Optional[str]:
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

    # Crs
    def Code(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int32Flags, o + self._tab.Pos)
        return 0

    # Crs
    def Name(self) -> Optional[str]:
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

    # Crs
    def Description(self) -> Optional[str]:
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

    # Crs
    def Wkt(self) -> Optional[str]:
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

    # Crs
    def CodeString(self) -> Optional[str]:
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(14))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

def CrsStart(builder: flatbuffers.Builder):
    builder.StartObject(6)

def Start(builder: flatbuffers.Builder):
    CrsStart(builder)

def CrsAddOrg(builder: flatbuffers.Builder, org: int):
    builder.PrependUOffsetTRelativeSlot(0, flatbuffers.number_types.UOffsetTFlags.py_type(org), 0)

def AddOrg(builder: flatbuffers.Builder, org: int):
    CrsAddOrg(builder, org)

def CrsAddCode(builder: flatbuffers.Builder, code: int):
    builder.PrependInt32Slot(1, code, 0)

def AddCode(builder: flatbuffers.Builder, code: int):
    CrsAddCode(builder, code)

def CrsAddName(builder: flatbuffers.Builder, name: int):
    builder.PrependUOffsetTRelativeSlot(2, flatbuffers.number_types.UOffsetTFlags.py_type(name), 0)

def AddName(builder: flatbuffers.Builder, name: int):
    CrsAddName(builder, name)

def CrsAddDescription(builder: flatbuffers.Builder, description: int):
    builder.PrependUOffsetTRelativeSlot(3, flatbuffers.number_types.UOffsetTFlags.py_type(description), 0)

def AddDescription(builder: flatbuffers.Builder, description: int):
    CrsAddDescription(builder, description)

def CrsAddWkt(builder: flatbuffers.Builder, wkt: int):
    builder.PrependUOffsetTRelativeSlot(4, flatbuffers.number_types.UOffsetTFlags.py_type(wkt), 0)

def AddWkt(builder: flatbuffers.Builder, wkt: int):
    CrsAddWkt(builder, wkt)

def CrsAddCodeString(builder: flatbuffers.Builder, codeString: int):
    builder.PrependUOffsetTRelativeSlot(5, flatbuffers.number_types.UOffsetTFlags.py_type(codeString), 0)

def AddCodeString(builder: flatbuffers.Builder, codeString: int):
    CrsAddCodeString(builder, codeString)

def CrsEnd(builder: flatbuffers.Builder) -> int:
    return builder.EndObject()

def End(builder: flatbuffers.Builder) -> int:
    return CrsEnd(builder)