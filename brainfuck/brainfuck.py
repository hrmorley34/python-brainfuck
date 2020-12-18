from typing import Callable, IO, BinaryIO, TextIO, Literal, Optional, Union
from io import BytesIO, StringIO
from abc import ABC, abstractmethod
from .memory import BaseMemory, BytesMemory, DictMemory
from .errors import ParsingError


class BaseBrainfuck(ABC):
    script: str
    eof: Optional[int]
    debugfunc: Optional[Callable[["BaseBrainfuck"], None]]

    memory: BaseMemory
    input: IO
    output: IO

    spointer: int
    dpointer: int
    sloops: list[int]

    @abstractmethod
    def __init__(
        self,
        script: str,
        input: Optional[IO] = None,
        output: Optional[IO] = None,
        memory: Optional[BaseMemory] = None,
        eof: Union[int, Literal[False], None] = 0,
        debugfunc: Optional[Callable[["BaseBrainfuck"], None]] = None,
    ):
        raise NotImplementedError

    def __iter__(self):
        while True:
            yield self.next()

    def __next__(self):
        return self.next()

    @abstractmethod
    def _c_input(self) -> int:
        " Input a character/byte "
        raise NotImplementedError

    def _c_input_eof(self) -> int:
        " Value for input of an EOF "
        if self.eof is None:
            return None  # No change
        elif self.eof is False:
            raise EOFError
        else:
            return self.eof

    @abstractmethod
    def _c_output(self, data: int):
        " Output a character/byte "
        raise NotImplementedError

    def next(self):
        " Run the next command in the script "
        c = self.script[self.spointer]

        if c == ">":
            # Increase data pointer by 1; don't overflow memory size
            self.dpointer += 1
            if self.dpointer >= self.memory._memsize:
                self.dpointer = self.memory._memsize - 1
        elif c == "<":
            # Decrease data pointer by 1; don't go below 0
            self.dpointer -= 1
            if self.dpointer < 0:
                self.dpointer = 0

        elif c == "+":
            # Increase memory at pointer by 1 (let Memory handle overflow)
            self.memory[self.dpointer] += 1
        elif c == "-":
            # Decrease memory at pointer by 1
            self.memory[self.dpointer] -= 1

        elif c == ",":
            # Input the next byte at pointer
            d = self._c_input()
            if d is not None:
                self.memory[self.dpointer] = d
        elif c == ".":
            # Output the byte at the pointer
            self._c_output(self.memory[self.dpointer])

        elif c == "[":
            # Loop unless 0 at pointer
            if self.memory[self.dpointer] == 0:
                # Skip to the end of the loop
                skippointer = self.spointer + 1
                skipdepth = 1
                while skipdepth > 0:
                    skipc = self.script[skippointer]
                    if skipc == "[":
                        skipdepth += 1
                    if skipc == "]":
                        skipdepth -= 1
                    skippointer += 1
                self.spointer = skippointer
                return
            else:
                self.sloops.append(self.spointer)
        elif c == "]":
            # Return to start of loop unless 0 at pointer
            if not len(self.sloops):
                raise ParsingError(
                    "No opening bracket matching close at {}".format(self.spointer)
                )
            p = self.sloops.pop(-1)
            if self.memory[self.dpointer] == 0:
                self.spointer += 1  # Continue on
            else:
                self.spointer = p  # Return to the start of the loop
            return

        elif c == "#":
            # Debug point: runs debugfunc
            if self.debugfunc is not None:
                self.debugfunc(self)

        else:
            # All other characters represent comments
            pass

        self.spointer += 1  # Move on to the next instruction

    def run(self):
        while self.spointer < len(self.script):
            self.next()
        if len(self.sloops) == 1:
            raise ParsingError("Unclosed loop at {}".format(self.sloops[0]))
        elif len(self.sloops) > 1:
            raise ParsingError(
                "Unclosed loops at {}, and {}".format(
                    ", ".join(map(str, self.sloops[:-1])), self.sloops[-1]
                )
            )


class BytesBrainfuck(BaseBrainfuck):
    memory: BaseMemory
    input: BinaryIO
    output: BinaryIO

    def __init__(
        self,
        script: str,
        input: Optional[BinaryIO] = None,
        output: Optional[BinaryIO] = None,
        memory: Optional[BaseMemory] = None,
        eof: Union[int, Literal[False], None] = 0,
        debugfunc: Optional[Callable[[BaseBrainfuck], None]] = None,
    ):
        self.script = script
        self.eof = eof if eof in (None, False) else int(eof)
        self.debugfunc = debugfunc

        self.memory = memory or BytesMemory()
        self.input = input or BytesIO()
        self.output = output or BytesIO()

        self.spointer = 0
        self.dpointer = 0
        self.sloops = []

    def _c_input(self) -> int:
        " Get the next input byte "
        inchar = self.input.read(1)
        if len(inchar):
            return inchar[0]
        else:
            return self._c_input_eof()

    def _c_output(self, data: int):
        " Output a byte "
        self.output.write(bytes([int(data) % 256]))


class UnicodeBrainfuck(BaseBrainfuck):
    memory: BaseMemory
    input: TextIO
    output: TextIO

    def __init__(
        self,
        script: str,
        input: Optional[TextIO] = None,
        output: Optional[TextIO] = None,
        memory: Optional[BaseMemory] = None,
        eof: Union[int, Literal[False], None] = 0,
        debugfunc: Optional[Callable[[BaseBrainfuck], None]] = None,
    ):
        self.script = script
        self.eof = eof if eof in (None, False) else int(eof)
        self.debugfunc = debugfunc

        self.memory = memory or DictMemory(cellsize=None)
        self.input = input or StringIO()
        self.output = output or StringIO()

        self.spointer = 0
        self.dpointer = 0
        self.sloops = []

    def _c_input(self) -> int:
        " Get the next input char "
        inchar = self.input.read(1)
        if len(inchar):
            return ord(inchar)
        else:
            return self._c_input_eof()

    def _c_output(self, data: int):
        " Output a char "
        self.output.write(chr(data))
