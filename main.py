from pgpc.scanner import TextScanner
from pgpc.parser import Parser, topology, char, position, content


@topology
def hello(value: str):
    start = yield position()

    for c in value:
        yield char(c)

    end = yield position()
    source = yield content()

    return f"Parsed '{source[start.offset:end.offset]}' which started at {start} and ended at {end}"


if __name__ == '__main__':
    text = "HELLO"

    par: Parser[str] = hello(text)

    result = par(TextScanner(text))

    print(result)
