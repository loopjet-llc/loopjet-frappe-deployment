from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import quote

import httpx


class FrappeError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class FrappeClient:
    def __init__(
        self,
        base_url: str,
        api_token: str,
        timeout: float = 30,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.timeout = timeout
        self._client = client

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"token {self.api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        if self._client is not None:
            response = await self._client.request(
                method,
                url,
                headers=self._headers(),
                params=params,
                json=json_body,
                timeout=self.timeout,
            )
        else:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method,
                    url,
                    headers=self._headers(),
                    params=params,
                    json=json_body,
                    timeout=self.timeout,
                )
        if response.status_code >= 400:
            raise FrappeError(_extract_error(response), response.status_code)
        if not response.content:
            return None
        payload = response.json()
        if isinstance(payload, dict):
            if "data" in payload:
                return payload["data"]
            if "message" in payload:
                return payload["message"]
        return payload

    async def call_method(
        self,
        method_name: str,
        *,
        http_method: str = "POST",
        params: dict[str, Any] | None = None,
    ) -> Any:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*", method_name):
            raise FrappeError(f"Invalid Frappe method name: {method_name}")
        verb = http_method.upper()
        if verb not in {"GET", "POST", "PUT", "DELETE"}:
            raise FrappeError(f"Unsupported method verb: {http_method}")
        request_kwargs: dict[str, Any] = (
            {"params": params} if verb == "GET" else {"json_body": params}
        )
        return await self.request(verb, f"/api/method/{method_name}", **request_kwargs)

    async def get_logged_user(self) -> str:
        user = await self.request("GET", "/api/method/frappe.auth.get_logged_user")
        if not isinstance(user, str):
            raise FrappeError("Frappe did not return a logged-in user")
        return user

    async def list_docs(
        self,
        doctype: str,
        *,
        fields: list[str] | None = None,
        filters: Any | None = None,
        limit: int = 20,
        limit_start: int = 0,
        order_by: str = "modified desc",
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "fields": json.dumps(fields or ["name", "modified"]),
            "limit_page_length": min(max(limit, 1), 100),
            "limit_start": max(limit_start, 0),
            "order_by": order_by,
        }
        if filters is not None:
            params["filters"] = json.dumps(filters)
        data = await self.request("GET", f"/api/resource/{_quote_doctype(doctype)}", params=params)
        return data if isinstance(data, list) else []

    async def get_doc(self, doctype: str, name: str) -> dict[str, Any]:
        data = await self.request(
            "GET", f"/api/resource/{_quote_doctype(doctype)}/{_quote_name(name)}"
        )
        if not isinstance(data, dict):
            raise FrappeError(f"Unexpected response for {doctype} {name}")
        return data

    async def create_doc(self, doctype: str, doc: dict[str, Any]) -> dict[str, Any]:
        data = await self.request("POST", f"/api/resource/{_quote_doctype(doctype)}", json_body=doc)
        if not isinstance(data, dict):
            raise FrappeError(f"Unexpected create response for {doctype}")
        return data

    async def update_doc(self, doctype: str, name: str, updates: dict[str, Any]) -> dict[str, Any]:
        data = await self.request(
            "PUT",
            f"/api/resource/{_quote_doctype(doctype)}/{_quote_name(name)}",
            json_body=updates,
        )
        if not isinstance(data, dict):
            raise FrappeError(f"Unexpected update response for {doctype} {name}")
        return data

    async def delete_doc(self, doctype: str, name: str) -> dict[str, Any] | None:
        data = await self.request(
            "DELETE", f"/api/resource/{_quote_doctype(doctype)}/{_quote_name(name)}"
        )
        return data if isinstance(data, dict) else None

    async def get_meta(self, doctype: str) -> dict[str, Any]:
        data = await self.call_method(
            "frappe.client.get_meta", http_method="GET", params={"doctype": doctype}
        )
        if not isinstance(data, dict):
            raise FrappeError(f"Unexpected meta response for {doctype}")
        return data

    async def get_count(self, doctype: str, filters: Any | None = None) -> int:
        params: dict[str, Any] = {"doctype": doctype}
        if filters is not None:
            params["filters"] = json.dumps(filters)
        data = await self.call_method("frappe.client.get_count", http_method="GET", params=params)
        if not isinstance(data, int):
            raise FrappeError(f"Unexpected count response for {doctype}")
        return data

    async def submit_doc(self, doctype: str, name: str) -> dict[str, Any]:
        doc = await self.get_doc(doctype, name)
        data = await self.call_method("frappe.client.submit", params={"doc": doc})
        if not isinstance(data, dict):
            raise FrappeError(f"Unexpected submit response for {doctype} {name}")
        return data

    async def cancel_doc(self, doctype: str, name: str) -> dict[str, Any]:
        data = await self.call_method(
            "frappe.client.cancel",
            params={"doctype": doctype, "name": name},
        )
        if not isinstance(data, dict):
            raise FrappeError(f"Unexpected cancel response for {doctype} {name}")
        return data

    async def apply_workflow(self, doctype: str, name: str, action: str) -> dict[str, Any]:
        doc = await self.get_doc(doctype, name)
        data = await self.call_method(
            "frappe.model.workflow.apply_workflow",
            params={"doc": doc, "action": action},
        )
        if not isinstance(data, dict):
            raise FrappeError(f"Unexpected workflow response for {doctype} {name}")
        return data

    async def run_report(
        self,
        report_name: str,
        *,
        filters: dict[str, Any] | None = None,
        user: str | None = None,
        ignore_prepared_report: bool = True,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "report_name": report_name,
            "filters": json.dumps(filters or {}),
            "ignore_prepared_report": 1 if ignore_prepared_report else 0,
        }
        if user:
            params["user"] = user
        data = await self.call_method(
            "frappe.desk.query_report.run", http_method="GET", params=params
        )
        if not isinstance(data, dict):
            raise FrappeError(f"Unexpected report response for {report_name}")
        return data

    async def search_link(
        self,
        doctype: str,
        *,
        text: str = "",
        filters: Any | None = None,
        query: str | None = None,
        page_length: int = 20,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "doctype": doctype,
            "txt": text,
            "page_length": min(max(page_length, 1), 100),
        }
        if filters is not None:
            params["filters"] = json.dumps(filters)
        if query:
            params["query"] = query
        data = await self.call_method(
            "frappe.desk.search.search_link", http_method="GET", params=params
        )
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and isinstance(data.get("results"), list):
            return data["results"]
        return []


def _extract_error(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text or f"Frappe HTTP {response.status_code}"
    if isinstance(payload, dict):
        for key in ("_server_messages", "exception", "exc", "message"):
            if payload.get(key):
                return str(payload[key])
    return f"Frappe HTTP {response.status_code}: {response.text}"


def _quote_doctype(value: str) -> str:
    return quote(value, safe="")


def _quote_name(value: str) -> str:
    return quote(value, safe="")
