from __future__ import annotations

from mcp.server.auth.provider import AccessToken, TokenVerifier

from loopjet_frappe_mcp.config import settings
from loopjet_frappe_mcp.frappe import FrappeClient, FrappeError


class FrappeTokenVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        if ":" not in token:
            return None
        client = FrappeClient(str(settings.frappe_base_url), token)
        try:
            user = await client.get_logged_user()
        except FrappeError:
            return None
        return AccessToken(
            token=token,
            client_id=user,
            scopes=["frappe"],
            expires_at=None,
            subject=user,
            claims={"frappe_user": user},
        )
