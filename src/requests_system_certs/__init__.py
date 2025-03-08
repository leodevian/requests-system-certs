"""Patch Requests to use system CA certificates."""

from __future__ import annotations

__all__ = ("init_poolmanager", "patch")

from typing import Any

init_poolmanager: Any = None


def patch() -> None:
    """Patch Requests to use system CA certificates."""
    import os

    global init_poolmanager  # noqa: PLW0603

    if init_poolmanager is not None:
        return

    if os.environ.get("DISABLE_REQUESTS_SYSTEM_CERTS_PATCH") is None:
        import ssl
        from functools import partialmethod

        from requests.adapters import HTTPAdapter

        ssl_context = ssl.create_default_context()
        ssl_context.load_default_certs()

        init_poolmanager = HTTPAdapter.init_poolmanager

        HTTPAdapter.init_poolmanager = partialmethod(  # type: ignore[assignment]
            init_poolmanager,
            ssl_context=ssl_context,
        )
