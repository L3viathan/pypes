"""
Inspired by dplr's %>%, this project allows you to use functional pipes in
Python code. For example, instead of:

    print(sum(map(int, input().split(","))))

you can write

    -(O| input() | str.split | print)

You can also assign a pipe to a variable. The following code puts the sum into
the variable `foo` instead of printing it.

    foo = -(O| input() | str.split | "," | (map, int) | sum)

"""
from functools import partial
from collections import deque

__all__ = ['O']


class Pipe:
    """
    Pipe object

    This object can be |'d with either a callable, a tuple, a list, or a dict.
    A callable causes this callable to be added to the call stack. The other
    datastructures prefill arguments of the callable:
        - Tuples cause the first element to be interpreted as the callable, the
          other ones as the first arguments. The pipe value gets added as a
          parameter after this.
        - Lists add arguments after the existing arguments, to the last added
          callable.
        - Dictionaries act like lists, but with keyword arguments.
    """
    def __init__(self, new=True):
        self.chain = deque()
        self.val = None
        self.new = new

    def __or__(self, other):
        if self.new:
            return Pipe(new=False) | other
        elif self.val is None:
            self.val = other
        elif isinstance(other, tuple):
            # put argument _after_ these
            # x | (map, len)
            fn, *rest = other
            self.chain.append(partial(fn, *rest))
        elif callable(other):
            self.chain.append(other)
        elif isinstance(other, list):
            # put argument _before_ these
            # x | str.split | [","]
            fn = self.chain[-1]
            self.chain[-1] = lambda x: fn(x, *other)
        elif isinstance(other, dict):
            # put argument _before_ these
            fn = self.chain[-1]
            self.chain[-1] = lambda x: fn(x, **other)
            # x | sum | {'start':0}
        else:
            # add a single argument
            fn = self.chain[-1]
            self.chain[-1] = lambda x: fn(x, other)
        return self

    def __neg__(self):
        """
        Start the evaluation of the pipe.
        """
        if self.val is None:
            fn = self.chain.popleft()
            self.val = fn()
        while self.chain:
            fn = self.chain.popleft()
            self.val = fn(self.val)
        return self.val


O = Pipe()
