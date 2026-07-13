from __future__ import annotations

import json
from typing import Any

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

    async def get_logged_user(self) -> str:
        user = await self.request("GET", "/api/method/frappe.auth.get_logged_user")
        if not isinstance(user, str):
            raise FrappeError("Frappe did not return a logged-in user")
        return user

    async def list_docs(
        self,
        doctype: str,
        *,
        fields: list[str],
        filters: list[list[Any]] | None = None,
        limit: int = 20,
        order_by: str = "modified desc",
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "fields": json.dumps(fields),
            "limit_page_length": min(max(limit, 1), 100),
            "order_by": order_by,
        }
        if filters:
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
    return value.replace(" ", "%20")


def _quote_name(value: str) -> str:
    from urllib.parse import quote

    return quote(value, safe="")
