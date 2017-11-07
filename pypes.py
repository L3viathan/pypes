"""
Inspired by dplr's %>%, this project allows you to use functional pipes in
Python code. For example, instead of:

    print(sum(map(int, input().split(","))))

you can write

    start | input() | str.split | "," | (map, int) | sum | print | end

You can also assign a pipe to a variable. The following code puts the sum into
the variable `foo` instead of printing it.

    foo = start | input() | str.split | "," | (map, int) | sum | end

"""
from functools import partial
from collections import deque

__all__ = ['start', 'end']


class Pipe:
    def __init__(self):
        self.chain = deque()
        self.val = None

    def __or__(self, other):
        if isinstance(other, Pipe):
            return self.go()
        elif self.val is None:
            self.val = other
        elif isinstance(other, tuple):
            # put argument _after_ these
            assert callable(self.chain[-1])
            fn, *rest = other
            self.chain.append(partial(fn, *rest))
        elif callable(other):
            self.chain.append(other)
        elif isinstance(other, list):
            # put argument _before_ these
            # x | sum&(1,)
            fn = self.chain[-1]
            self.chain[-1] = lambda x: fn(x, *other)
        elif isinstance(other, dict):
            # put argument _before_ these
            fn = self.chain[-1]
            self.chain[-1] = lambda x: fn(x, **other)
            # x | sum&{'start':0}
        else:
            fn = self.chain[-1]
            self.chain[-1] = lambda x: fn(x, other)
        return self

    def __ror__(self, other):
        self.val = other
        return self

    def go(self):
        while self.chain:
            fn = self.chain.popleft()
            self.val = fn(self.val)
        return self.val


class PipeStarter:
    def __or__(self, other):
        return Pipe() | other


start, end = PipeStarter(), Pipe()
