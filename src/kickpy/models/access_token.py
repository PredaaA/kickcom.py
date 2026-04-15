from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class AccessToken:
    access_token: str
    expires_at: datetime
    token_type: str
    refresh_token: str | None = None
    scope: str | None = None
    token_kind: str = "app"

    def __post_init__(self) -> None:
        self.expires_at = (
            datetime.fromtimestamp(self.expires_at)
            if isinstance(self.expires_at, (int, float))
            else self.expires_at
        )

    def to_dict(self) -> dict:
        data = {
            "access_token": self.access_token,
            "expires_at": int(self.expires_at.timestamp()),
            "token_type": self.token_type,
            "token_kind": self.token_kind,
        }
        if self.refresh_token is not None:
            data["refresh_token"] = self.refresh_token
        if self.scope is not None:
            data["scope"] = self.scope
        return data
