# Pypes

Inspired by dplr's %>%, this project allows you to use functional pipes in
Python code. For example, instead of:

    print(sum(map(int, input().split(","))))

you can write

    -(O| input() | str.split | "," | (map, int) | sum | print)

You can also assign a pipe to a variable. The following code puts the sum into
the variable `foo` instead of printing it.

    foo = -(O| input() | str.split | "," | (map, int) | sum)

## Usage

All you need to do is to import `O` (or `*`) from `pypes`
