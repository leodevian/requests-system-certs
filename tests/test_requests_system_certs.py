"""Unit tests for `requests_system_certs`."""

from __future__ import annotations

import os
import ssl
from typing import TYPE_CHECKING

import pytest
from requests.adapters import HTTPAdapter

import requests_system_certs

if TYPE_CHECKING:
    from collections.abc import Generator


if os.environ.get("DISABLE_REQUESTS_SYSTEM_CERTS_PATCH") is None:
    pytest.skip(
        "Requests was patched prior to running tests", allow_module_level=True
    )  # pragma: no cover


@pytest.fixture
def ssl_context() -> ssl.SSLContext:
    """Return an SSL context."""
    ssl_context = ssl.create_default_context()
    ssl_context.load_default_certs()
    return ssl_context


@pytest.fixture
def patch_requests() -> Generator[None]:
    """Patch Requests to use system CA certificates."""
    env = os.environ.pop("DISABLE_REQUESTS_SYSTEM_CERTS_PATCH")

    try:
        requests_system_certs.patch()
        yield

    finally:
        os.environ["DISABLE_REQUESTS_SYSTEM_CERTS_PATCH"] = env
        HTTPAdapter.init_poolmanager = requests_system_certs.init_poolmanager  # type: ignore[method-assign]
        requests_system_certs.init_poolmanager = None


@pytest.mark.usefixtures("patch_requests")
def test_patch(ssl_context: ssl.SSLContext) -> None:
    """Test patching Requests."""
    requests_system_certs.patch()
    assert requests_system_certs.init_poolmanager is not None
    http_adapter = HTTPAdapter()
    assert "ssl_context" in http_adapter.poolmanager.connection_pool_kw
    assert isinstance(
        http_adapter.poolmanager.connection_pool_kw["ssl_context"], ssl.SSLContext
    )
    assert (
        http_adapter.poolmanager.connection_pool_kw["ssl_context"].get_ca_certs()
        == ssl_context.get_ca_certs()
    )


def test_bypass_patch() -> None:
    """Test bypassing patching Requests."""
    requests_system_certs.patch()
    assert requests_system_certs.init_poolmanager is None
