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


@pytest.mark.asyncio
async def test_list_docs_encodes_doctype_filters_and_pagination() -> None:
    requests = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"data": [{"name": "INV-1"}]})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http:
        client = FrappeClient("https://erp.loopjet.io", "key:secret", client=http)
        result = await client.list_docs(
            "Sales Invoice",
            fields=["name", "customer"],
            filters=[["Sales Invoice", "customer", "=", "Example"]],
            limit=250,
            limit_start=10,
            order_by="name asc",
        )

    assert result == [{"name": "INV-1"}]
    request = requests[0]
    assert request.url.raw_path.startswith(b"/api/resource/Sales%20Invoice")
    assert request.url.params["limit_page_length"] == "100"
    assert request.url.params["limit_start"] == "10"
    assert request.url.params["order_by"] == "name asc"


@pytest.mark.asyncio
async def test_call_method_rejects_path_like_method_names() -> None:
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda request: httpx.Response(200))
    ) as http:
        client = FrappeClient("https://erp.loopjet.io", "key:secret", client=http)
        with pytest.raises(FrappeError, match="Invalid Frappe method name"):
            await client.call_method("../bad/path")


@pytest.mark.asyncio
async def test_run_report_calls_query_report_endpoint() -> None:
    requests = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"message": {"columns": [], "result": []}})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http:
        client = FrappeClient("https://erp.loopjet.io", "key:secret", client=http)
        result = await client.run_report("Accounts Receivable", filters={"company": "Loopjet LLC"})

    assert result == {"columns": [], "result": []}
    request = requests[0]
    assert request.url.path == "/api/method/frappe.desk.query_report.run"
    assert request.url.params["report_name"] == "Accounts Receivable"
    assert '"Loopjet LLC"' in request.url.params["filters"]
