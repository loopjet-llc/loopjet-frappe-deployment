import httpx
import pytest

from loopjet_frappe_mcp.frappe import FrappeClient, FrappeError


@pytest.mark.asyncio
async def test_get_logged_user_uses_frappe_token_header() -> None:
    requests = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"message": "agent@example.com"})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http:
        client = FrappeClient("https://erp.loopjet.io", "key:secret", client=http)
        assert await client.get_logged_user() == "agent@example.com"

    assert requests[0].headers["Authorization"] == "token key:secret"


@pytest.mark.asyncio
async def test_frappe_error_extracts_message() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"message": "Not permitted"})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http:
        client = FrappeClient("https://erp.loopjet.io", "key:secret", client=http)
        with pytest.raises(FrappeError, match="Not permitted"):
            await client.get_doc("Sales Invoice", "ACC-SINV-1")
