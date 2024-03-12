from __future__ import annotations

import urllib.request
from logging import getLogger

logger = getLogger(__name__)


class BufferedHttpRangeClient:
    def __init__(self, source: str | HttpRangeClient):
        self.bytes_ever_used = 0
        self.bytes_ever_fetched = 0
        self.buffer = bytearray()
        self.head = 0

        if isinstance(source, str):
            self.http_client = HttpRangeClient(source)
        elif isinstance(source, HttpRangeClient):
            self.http_client = source
        else:
            raise ValueError("Unknown source")

    async def get_range(
        self, start: int, length: int, min_req_length: int, purpose: str
    ) -> bytes:
        self.bytes_ever_used += length

        start_i = start - self.head
        end_i = start_i + length
        if start_i >= 0 and end_i <= len(self.buffer):
            return self.buffer[start_i:end_i]

        length_to_fetch = max(length, min_req_length)

        self.bytes_ever_fetched += length_to_fetch
        self.buffer = await self.http_client.get_range(start, length_to_fetch, purpose)
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


class HttpRangeClient:
    def __init__(self, url: str):
        self.url = url
        self.requests_ever_made = 0
        self.bytes_ever_requested = 0

    async def get_range(self, begin: int, length: int, purpose: str) -> bytes:
        self.requests_ever_made += 1
        self.bytes_ever_requested += length

        range_header = f"bytes={begin}-{begin + length - 1}"
        headers = {
            "Range": range_header,
        }

        req = urllib.request.Request(self.url, headers=headers)
        response = urllib.request.urlopen(req)

        return response.read()
