from .brainfuck import BaseBrainfuck, BytesBrainfuck, UnicodeBrainfuck
from .memory import BaseMemory, DictMemory, BytesMemory
from .errors import ParsingError


Brainfuck = BytesBrainfuck
Memory = BytesMemory


def debug_info(bf: BaseBrainfuck):
    return (
        f"s*: {bf.spointer}; d*: {bf.dpointer}; mem: {bf.memory}; sloops: {bf.sloops}"
    )
