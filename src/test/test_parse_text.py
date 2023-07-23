from typing import List

from pgpc.parser import topology, position, char, Parser
from pgpc.scanner import TextScanner, Position


@topology
def parse_text(text: str):
    start = yield position()

    parsed: List[str] = []

    for letter in text:
        last_parsed_letter = yield char(letter)
        parsed.append(last_parsed_letter)

    end = yield position()

    return parsed, start, end


def test_scanner_move() -> None:
    text = "Hello"

    test_parser: Parser[str] = parse_text(text)

    start: Position
    end: Position
    _, start, end = test_parser(TextScanner(text))

    assert start.offset + len(text) == end.offset


def test_parsed_text() -> None:
    text = "HELLO"
    test_parser: Parser[str] = parse_text(text)
    parsed, _, _ = test_parser(TextScanner(text))

    assert parsed == list(text)
