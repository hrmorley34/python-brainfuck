from typing import BinaryIO
from io import BytesIO
from .memory import Memory, DefaultMemory


class Brainfuck:
    script: str

    memory: Memory
    input: BinaryIO
    output: BinaryIO

    spointer: int
    dpointer: int
    sloops: list

    def __init__(
        self,
        script: str,
        input: BinaryIO = None,
        output: BinaryIO = None,
        memory: Memory = None,
    ):
        self.script = script

        self.memory = memory or DefaultMemory()
        self.input = input or BytesIO(input)
        self.output = output or BytesIO(output)

        self.spointer = 0
        self.dpointer = 0
        self.sloops = []

    def __iter__(self):
        while True:
            self.next()
            while len(self.output):
                o, self.output = self.output[0], self.output[1:]
                yield o

    def run(self):
        while self.spointer < len(self.script):
            self.next()

    def next(self):
        c = self.script[self.spointer]

        if c == ">":
            self.dpointer += 1
            if self.dpointer >= self.memory._memsize:
                self.dpointer = self.memory._memsize - 1
        elif c == "<":
            self.dpointer -= 1
            if self.dpointer < 0:
                self.dpointer = 0
        elif c == "+":
            self.memory[self.dpointer] += 1
        elif c == "-":
            self.memory[self.dpointer] -= 1
        elif c == ".":
            self.output.write(bytes([self.memory[self.dpointer]]))
        elif c == ",":
            inchar = self.input.read(1)
            if len(inchar) <= 0:
                raise EOFError
            self.memory[self.dpointer] = inchar[0]
        elif c == "[":
            if self.memory[self.dpointer] <= 0:
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
            p = self.sloops.pop(-1)
            if self.memory[self.dpointer] == 0:
                self.spointer += 1
            else:
                self.spointer = p
            return
        else:
            pass

        self.spointer += 1
