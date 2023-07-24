from copy import copy

from pgpc.scanner import Scanner, Position, ELEMENT
from typing import TypeVar, Generic, Callable, Any, Sequence, List
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

    def __call__(self, scanner: Scanner, *args, **kwargs) -> V:
        return self.__parser(scanner)

    def alt(self, parser: 'Parser[U]') -> 'Parser[V | U]':
        def __with_scanner(scanner: Scanner) -> V:
            try:
                scanner.mark()
                return self.__parser(scanner)
            except ValueError:
                scanner.reset()
                return parser(scanner)

        return Parser(__with_scanner)

    def map(self, mapper: Callable[[V], U]) -> 'Parser[U]':
        def __with_scanner(scanner: Scanner) -> U:
            result = self.__parser(scanner)
            return mapper(result)

        return Parser(__with_scanner)

    def replace_with(self, parser: 'Parser[U]') -> 'Parser[U]':
        return self.replace_lazy(lambda: parser)

    def replace_lazy(self, parser: Callable[[], 'Parser[U]']) -> 'Parser[U]':
        def __with_scanner(scanner: Scanner) -> U:
            self.__parser(scanner)
            value = parser()(scanner)
            return value

        return Parser(__with_scanner)

    def drain_next(self, parser: 'Parser[V]') -> 'Parser[V]':
        def __with_scanner(scanner: Scanner) -> V:
            value = self.__parser(scanner)
            parser(scanner)
            return value

        return Parser(__with_scanner)

    def __or__(self, other: 'Parser[U]') -> 'Parser[V | U]':
        return self.alt(other)


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


def satisfy(predicate: Callable[[V], bool]) -> Parser[V]:
    def __with_scanner(scanner: Scanner) -> V:
        result = scanner.advance_if(predicate)
        if not result:
            raise Parser.ParserError(f"Unexpected '{scanner.current}' at {scanner.pos}")
        return result

    return Parser(__with_scanner)


def any_char() -> Parser[str]:
    return satisfy(lambda x: True)


def char(c: V) -> Parser[V]:
    return satisfy(lambda x: c == x)


def opt(parser: Parser[V]) -> Parser[V | None]:
    def __with_scanner(scanner: Scanner) -> V | None:
        try:
            scanner.mark()
            return parser(scanner)
        except ValueError:
            scanner.reset()
            return None

    return Parser(__with_scanner)


def many(parser: Parser[V]) -> Parser[List[V]]:
    def __with_scanner(scanner: Scanner) -> List[V]:
        result = []
        try:
            while True:
                element = parser(scanner)
                result.append(element)
        except ValueError:
            return result

    return Parser(__with_scanner)


def ws() -> Parser[str]:
    return satisfy(lambda x: type(x) is str and x.isspace())


def letter() -> Parser[str]:
    return satisfy(lambda x: type(x) is str and x.isalpha())


def digit() -> Parser[str]:
    return satisfy(lambda x: type(x) is str and x.isdigit())


def alphanum() -> Parser[str]:
    return satisfy(lambda x: type(x) is str and x.isalnum())


def content() -> Parser[Sequence[ELEMENT]]:
    def __with_scanner(scanner: Scanner) -> Sequence[ELEMENT]:
        return scanner.content

    return Parser(__with_scanner)


def position() -> Parser[Position]:
    def __with_scanner(scanner: Scanner) -> Position:
        return copy(scanner.pos)

    return Parser(__with_scanner)
