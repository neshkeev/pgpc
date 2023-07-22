# PGPC

## Overview

**PGPC** is a parser combinator library. Its name is an acronym, and it stands for **P**ython **G**enerator based **P**arser **C**ombinator library.

The library was heavily influenced by the [Parsec](https://github.com/haskell/parsec) monadic parser combinator library,
so the transition from `Parsec` (and other parser combinators) to `PGPC` should be more or less easy.

The original idea of the library is emulating the `do`-notation with the `yield` Python keyword.

## Quick start

The `@topology` decorator over a function allows the `yield` keyword work with parsers in a `do`-notation-like fashion:

```python
from pgpc.scanner import TextScanner
from pgpc.parser import Parser, topology, char, position, content


@topology
def hello(value: str):
    start = yield position()

    for c in value:
        yield char(c)

    end = yield position()
    source = yield content()

    return f"Parsed {source[start.offset:end.offset]} which started at {start} and ended at {end}"


if __name__ == '__main__':
    text = "HELLO"
    
    par: Parser[str] = hello(text)
    
    result = par(TextScanner(text))
    
    print(result)
```
