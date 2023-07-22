from abc import abstractmethod
from typing import List, Generic, TypeVar, Callable, Sequence


class Position:
    def __init__(self, offset: int = 0):
        self.__offset = offset

    @property
    def offset(self):
        return self.__offset

    @abstractmethod
    def increase(self, offset: int):
        self.__offset += offset


class TextPosition(Position):

    def __init__(self, content: str):
        super().__init__()
        self.__content = content
        self.__line: int = 1
        self.__column: int = 1

    @property
    def line(self):
        return self.__line

    @property
    def column(self):
        return self.__column

    def increase(self, offset: int):
        if super().offset + offset > len(self.__content):
            raise EOFError(f"{super().offset} is greater that {len(self.__content)}")

        new_lines = self.__content.count("\n", super().offset, super().offset + offset)
        self.__line += new_lines

        if new_lines > 0:
            last_new_line = self.__content.rindex("\n", super().offset, super().offset + offset)
            self.__column = super().offset + offset - last_new_line
        else:
            self.__column += offset

        super().increase(offset)

    def __repr__(self) -> str:
        return f"({self.__line}, {self.__column})"


ELEMENT = TypeVar('ELEMENT')


class Scanner(Generic[ELEMENT]):
    def __init__(self, content: Sequence[ELEMENT], pos: Position):
        self.__pos: Position = pos
        self.__content: Sequence[ELEMENT] = content
        self.__marks: List[Position] = []

    def mark(self) -> None:
        self.__marks.append(self.__pos)

    def reset(self) -> None:
        if self.__marks:
            self.__pos = self.__marks.pop()

    @property
    def pos(self) -> Position:
        return self.__pos

    @property
    def current(self) -> ELEMENT:
        if self.__pos.offset >= len(self.content):
            raise EOFError(f"No value at {self.__pos.offset}")
        result = self.content[self.pos.offset]
        return result

    def advance_if(self, predicate: Callable[[ELEMENT], bool]) -> ELEMENT | None:
        element = self.current
        if predicate(element):
            self.__pos.increase(1)
            return element
        else:
            return None

    @property
    def content(self) -> Sequence[ELEMENT]:
        return self.__content


class TextScanner(Scanner[str]):
    def __init__(self, content: str):
        super().__init__(content, TextPosition(content))

    @classmethod
    def from_file(cls, file: str) -> 'TextScanner':
        with open(file, "r") as f:
            value_ = f.read()
            return cls(value_)
