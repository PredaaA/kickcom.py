from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class AccessToken:
    access_token: str
    expires_at: datetime
    token_type: str

    def __post_init__(self) -> None:
        self.expires_at = (
            datetime.fromtimestamp(self.expires_at)
            if isinstance(self.expires_at, int)
            else self.expires_at
        )

    def to_dict(self) -> dict:
        return {
            "access_token": self.access_token,
            "expires_at": int(self.expires_at.timestamp()),
            "token_type": self.token_type,
        }
