from copy import copy

from pgpc.scanner import Scanner, Position, ELEMENT
from typing import TypeVar, Generic, Callable, Any, Sequence
from functools import wraps

V = TypeVar('V')
U = TypeVar('U')


class Parser(Generic[V]):
    class ParserError(ValueError):
        def __init__(self, *args: Any):
            super().__init__(*args)

    def __init__(self, parser: Callable[[Scanner], V]):
        self.__parser = parser

    def and_then(self, consumer: Callable[[V], 'Parser[U]']) -> 'Parser[U]':
        def __with_scanner(scanner: Scanner) -> U:
            v = self.__parser(scanner)
            return consumer(v)(scanner)

        return Parser(__with_scanner)

    def __call__(self, scanner: Scanner, *args, **kwargs):
        return self.__parser(scanner)


def topology(parser_builder) -> Callable[..., Parser[V]]:
    @wraps(parser_builder)
    def wrapper(*args: Any, **kwargs: Any) -> Parser[V]:
        gen = parser_builder(*args, **kwargs)

        def __with_scanner(scanner: Scanner) -> V:
            parser = next(gen)
            try:
                while True:
                    result = parser(scanner)
                    parser = gen.send(result)
            except StopIteration as e:
                return e.value

        return Parser(__with_scanner)

    return wrapper


def satisfy(predicate: Callable[[str], bool]) -> Parser[str]:
    def __with_scanner(scanner: Scanner) -> str:
        result = scanner.advance_if(predicate)
        if not result:
            raise Parser.ParserError(f"Unexpected '{scanner.current}' at {scanner.pos}")
        return result

    return Parser(__with_scanner)


def any_char() -> Parser[str]:
    return satisfy(lambda x: True)


def char(c: str) -> Parser[str]:
    return satisfy(lambda x: c == x)


def content() -> Parser[Sequence[ELEMENT]]:
    def __with_scanner(scanner: Scanner) -> Sequence[ELEMENT]:
        return scanner.content

    return Parser(__with_scanner)


def position() -> Parser[Position]:
    def __with_scanner(scanner: Scanner) -> Position:
        return copy(scanner.pos)

    return Parser(__with_scanner)

