# PGPC

## Overview

**PGPC** is a parser combinator library. Its name is an acronym, which stands for **P**ython **G**enerator based **P**arser **C**ombinator library.

The library was heavily influenced by the [Parsec](https://github.com/haskell/parsec) monadic parser combinator library,
so the transition from `Parsec` (and other parser combinators) to `PGPC` should be relatively easy.

The original idea of the library is emulating the `do`-notation with the `yield` Python keyword.

## Quick start

The `@topology` decorator over a function allows the `yield` keyword work with parsers in a `do`-notation-like fashion:

1. install the package: `pip install pgpc`
1. save the following code into `main.py`:
```python
from pgpc.scanner import TextScanner
from pgpc.parser import Parser, topology, char, position, content


@topology
def parse_hello_world():
    start = yield position()

    for c in "Hello":
        yield char(c)

    yield char(",")
    yield char(" ")

    for c in "World":
        yield char(c)

    yield char("!")

    end = yield position()
    source = yield content()

    return f"Parsed '{source[start.offset:end.offset]}' which started at {start} and ended at {end}"


if __name__ == '__main__':
    text = "Hello, World!"

    hw_parser: Parser[str] = parse_hello_world()

    result = hw_parser(TextScanner(text))

    print(result)
```
3. run `main.py`: `python main.py`
