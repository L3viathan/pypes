# Pypes

Inspired by dplr's %>%, this project allows you to use functional pipes in
Python code. For example, instead of:

    print(sum(map(int, input().split(","))))

you can write

    start | input() | str.split | "," | (map, int) | sum | print | end

You can also assign a pipe to a variable. The following code puts the sum into
the variable `foo` instead of printing it.

    foo = start | input() | str.split | "," | (map, int) | sum | end

## Usage

All you need to do is to import `start` and `end` (or `*`) from `pypes`
