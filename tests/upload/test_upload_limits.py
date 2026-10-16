import pytest
from fastapi import HTTPException

from backend.app import BodyLimit
from backend.config import settings


def test_chunked_request_limit_without_content_length():
    import asyncio
    messages = iter([{"type": "http.request", "body": b"x" * settings.max_request_size, "more_body": True},
                     {"type": "http.request", "body": b"x", "more_body": False}])
    async def receive():
        return next(messages)
    async def send(message):
        pass
    async def application(scope, receive, send):
        await receive()
        await receive()
    with pytest.raises(HTTPException) as error:
        asyncio.run(BodyLimit(application)({"type": "http"}, receive, send))
    assert error.value.status_code == 413