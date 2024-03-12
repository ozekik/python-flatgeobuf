from __future__ import annotations

from io import BufferedIOBase
from logging import getLogger

logger = getLogger(__name__)


class BufferedFileRangeClient:
    def __init__(self, source: BufferedIOBase | FileRangeClient):
        self.bytes_ever_used = 0
        self.bytes_ever_fetched = 0
        self.buffer = bytearray()
        self.head = 0

        if isinstance(source, BufferedIOBase):
            self.file_client = FileRangeClient(source)
        elif isinstance(source, FileRangeClient):
            self.file_client = source
        else:
            raise ValueError("Unknown source")

    def get_range(
        self, start: int, length: int, min_req_length: int, purpose: str
    ) -> bytes:
        self.bytes_ever_used += length

        start_i = start - self.head
        end_i = start_i + length
        if start_i >= 0 and end_i <= len(self.buffer):
            return self.buffer[start_i:end_i]

        length_to_fetch = max(length, min_req_length)

        self.bytes_ever_fetched += length_to_fetch
        self.buffer = self.file_client.get_range(start, length_to_fetch, purpose)
        self.head = start

        return self.buffer[:length]

    def log_usage(self, purpose: str) -> None:
        category = purpose.split(" ")[0]
        used = self.bytes_ever_used
        requested = self.bytes_ever_fetched
        efficiency = f"{(100.0 * used / requested):.2f}"

        logger.info(
            f"{category} bytes used/requested: {used} / {requested} = {efficiency}%"
        )


class FileRangeClient:
    def __init__(self, file: BufferedIOBase):
        self.file = file
        self.requests_ever_made = 0
        self.bytes_ever_requested = 0

    def get_range(self, begin: int, length: int, purpose: str) -> bytes:
        self.requests_ever_made += 1
        self.bytes_ever_requested += length

        self.file.seek(begin)
        return self.file.read(length)
