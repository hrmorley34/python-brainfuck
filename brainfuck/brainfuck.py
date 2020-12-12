DEBUG = False


class Memory(object):
    def __init__(self,
                 memsize: int = 30000,
                 cellsize: int = 256,
                 ):
        self._default = 0
        self._memsize = memsize
        self._cellsize = cellsize
        self.data = {}

    def __setitem__(self, key, value):
        key = int(key)
        assert 0 <= key < self._memsize

        value = int(value)
        value %= self._cellsize

        self.data[key] = value

    def __getitem__(self, key):
        key = int(key)
        assert 0 <= key < self._memsize

        return self.data.get(key, self._default)

    def __repr__(self):
        if not len(self.data):
            return f"Memory[{self._memsize}]"
        cs = len(hex(self._cellsize-1)[2:])
        text = f"Memory[{self._memsize}]"+"{"
        for x in range(0, max(self.data.keys()) + 1, 16):
            text += "\n "
            for i in range(x, x+16):
                text += " " + hex(self[i])[2:].rjust(cs, "0")
        text += "\n}"
        return text


class BrainFuck(object):
    def __init__(self,
                 script: str = "",
                 input: str = "",
                 output: str = "",
                 memopts: dict = {},
                 ):
        self.script = script
        self.spointer = 0
        self.sloops = []

        self.memory = Memory(**memopts)
        self.dpointer = 0

        self.input = input
        self.output = output

    def run(self):
        while self.spointer < len(self.script):
            self.next()

    def run_io(self):
        while self.spointer < len(self.script):
            try:
                self.next()
            except EOFError:
                inputv = input("\n> ")
                try:
                    self.input += chr(int(inputv))
                except ValueError:
                    self.input += inputv
            else:
                if len(self.output):
                    print(self.output, end="")
                    self.output = ""

    def next(self):
        c = self.script[self.spointer]

        if DEBUG:
            print(f"s*: {self.spointer}; c: {c}; d*: {self.dpointer}; mem: {self.memory}; sloops: {self.sloops}")

        if c == ">":
            self.dpointer += 1
            if self.dpointer >= self.memory._memsize:
                self.dpointer = self.memory._memsize - 1
        if c == "<":
            self.dpointer -= 1
            if self.dpointer < 0:
                self.dpointer = 0
        if c == "+":
            self.memory[self.dpointer] += 1
        if c == "-":
            self.memory[self.dpointer] -= 1
        if c == ".":
            self.output += chr(self.memory[self.dpointer])
        if c == ",":
            if len(self.input) < 1:
                raise EOFError
            self.memory[self.dpointer] = ord(self.input[0])
            self.input = self.input[1:]
        if c == "[":
            self.sloops.append(self.spointer)
            if self.memory[self.dpointer] == 0:
                escapelevel = len(self.sloops)
                while len(self.sloops) >= escapelevel:
                    self.spointer += 1
                    skipc = self.script[self.spointer]
                    if skipc == "[":
                        self.sloops.append(self.spointer)
                    if skipc == "]":
                        self.sloops.pop(-1)
        if c == "]":
            self.spointer = self.sloops.pop(-1)
            return

        self.spointer += 1
