from .brainfuck import BrainFuck
from .memory import Memory, DictMemory, BytesMemory


def debug_info(bf: BrainFuck):
    return (
        f"s*: {bf.spointer}; d*: {bf.dpointer}; mem: {bf.memory}; sloops: {bf.sloops}"
    )
