from typing import Any, BinaryIO, IO, Optional, Sequence, Union
from io import BytesIO
from abc import ABC, abstractmethod


class BaseMemory(ABC):
    _default: int = 0
    _memsize: Optional[int]
    _cellsize: Optional[int]
    _cellwrap: bool
    data: Any

    def __init__(
        self,
        memsize: Optional[int] = 30000,
        cellsize: Optional[int] = 256,
        cellwrap: bool = False,
    ):
        self._memsize = memsize
        self._cellsize = cellsize
        self._cellwrap = cellwrap

    @abstractmethod
    def __setitem__(self, key: int, value: int):
        raise NotImplementedError

    @abstractmethod
    def __getitem__(self, key: int) -> int:
        raise NotImplementedError

    def __delitem__(self, key: int):
        self.__setitem__(key, self._default)

    def __repr__(self):
        return f"Memory[{self._memsize}]"


class DictMemory(BaseMemory):
    data: dict

    def __init__(
        self,
        memsize: Optional[int] = 30000,
        cellsize: Optional[int] = 256,
        cellwrap: bool = False,
    ):
        self._memsize = memsize
        self._cellsize = cellsize
        self._cellwrap = cellwrap
        self.data = dict()

    def __setitem__(self, key: int, value: int):
        key = int(key)
        assert 0 <= key
        assert self._memsize is None or key < self._memsize

        value = int(value)
        if self._cellsize:
            if self._cellwrap:
                value %= self._cellsize
            else:
                value = max(min(value, self._cellsize), 0)

        self.data[key] = value

    def __getitem__(self, key: int) -> int:
        key = int(key)
        assert 0 <= key
        assert self._memsize is None or key < self._memsize

        return self.data.get(key, self._default)

    def __delitem__(self, key: int):
        if key in self.data:
            del self.data[key]

    def __repr__(self) -> str:
        if not len(self.data):
            return f"Memory[{self._memsize}]"
        if self._cellsize is None:
            cs = min(max(len(hex(max(self.data.value()))) - 2, 2), 8)
        else:
            cs = len(hex(self._cellsize - 1)) - 2
        text = f"Memory[{self._memsize}]" + "{"
        for x in range(0, max(self.data.keys()) + 1, 16):
            text += "\n "
            for i in range(x, x + 16):
                text += " " + hex(self[i])[2:].rjust(cs, "0")
        text += "\n}"
        return text


class IOMemory(BaseMemory):
    data: IO


class BytesMemory(IOMemory):
    @property
    def _cellsize(self) -> int:
        return 256

    data: BinaryIO

    def __init__(self, memsize: Optional[int] = 30000, dataobj: BinaryIO = None):
        self._memsize = memsize
        self.data = dataobj or BytesIO()

    def __setitem__(
        self, key: Union[int, slice], value: Union[int, Sequence[int]]
    ) -> Union[int, Sequence[int]]:
        if isinstance(key, slice):
            start = int(key.start or 0)
            stop = key.stop and int(key.stop)
            step = int(key.step or 1)

            if step == 1:
                self.data.seek(start)
                assert stop is None or stop - start == len(value)
                self.data.write(bytes(value))
            else:
                self.data.getbuffer()[key] = bytes(value)

        key = int(key)
        assert 0 <= key
        assert self._memsize is None or key < self._memsize

        self.data.seek(key)
        self.data.write(bytes([int(value) % self._cellsize]))

    def __getitem__(self, key: Union[int, slice]) -> Union[int, Sequence[int]]:
        if isinstance(key, slice):
            start = int(key.start or 0)
            stop = key.stop and int(key.stop)
            step = int(key.step or 1)

            if step == 1:
                self.data.seek(start)
                return self.data.read(-1 if stop is None else stop - start)
            else:
                return bytes(self.data.getbuffer()[key])

        key = int(key)
        assert 0 <= key
        assert self._memsize is None or key < self._memsize

        self.data.seek(key)
        return (self.data.read(1) or b"\x00")[0]

    def __repr__(self) -> str:
        self.data.seek(0)
        c = self.data.read(1)

        if len(c) <= 0:
            return f"Memory[{self._memsize}]"

        text = f"Memory[{self._memsize}]" + "{\n"
        nullrowcount = 0
        while c:
            row, nullrow = " ", True
            for i in range(16):
                row += " " + (c.hex() or "00")
                if any(c):
                    nullrow = False
                c = self.data.read(1)
            if nullrow:
                nullrowcount += 1
            else:
                if nullrowcount > 3:
                    text += "  {}... {} null rows ...\n".format(" " * 13, nullrowcount)
                else:
                    text += (" " + " 00" * 16 + "\n") * nullrowcount
                nullrowcount = 0
                text += row + "\n"
        text += "}"
        return text
