from __future__ import annotations


class Config:
    global_instance: Config

    def __init__(self):
        self._extra_request_threshold = 256 * 1024

    def extra_request_threshold(self):
        return self._extra_request_threshold

    def set_extra_request_threshold(self, bytes):
        if bytes < 0:
            raise ValueError("extra_request_threshold cannot be negative")
        self._extra_request_threshold = bytes


Config.global_instance = Config()
