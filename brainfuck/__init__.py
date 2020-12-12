from .brainfuck import Brainfuck
from .memory import Memory, DictMemory, BytesMemory


def debug_info(bf: Brainfuck):
    return (
        f"s*: {bf.spointer}; d*: {bf.dpointer}; mem: {bf.memory}; sloops: {bf.sloops}"
    )
