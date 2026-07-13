from __future__ import annotations

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    frappe_base_url: AnyHttpUrl = "https://erp.loopjet.io"
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8000
    mcp_resource_server_url: AnyHttpUrl = "https://mcp.loopjet.io"
    mcp_issuer_url: AnyHttpUrl = "https://erp.loopjet.io"


settings = Settings()
