from typing import Generic, TypeVar

T = TypeVar('T')


class ListResult(Generic[T]):
    def __init__(self, data, total, start, sort, order, size) -> None:
        self.data: list[T] = data
        self.total: int = total
        self.start: int = start
        self.sort: str = sort
        self.order: str = order
        self.size: int = size
