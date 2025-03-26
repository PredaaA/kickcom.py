from dataclasses import dataclass
from datetime import datetime


@dataclass
class AccessToken:
    access_token: str
    expires_at: datetime
    token_type: str

    @classmethod
    def from_dict(cls, data: dict):
        expires_at = (
            datetime.fromtimestamp(data["expires_at"])
            if data.get("expires_at")
            else datetime.fromtimestamp(datetime.now().timestamp() + data["expires_in"])
        )
        return cls(
            access_token=data["access_token"],
            expires_at=expires_at,
            token_type=data["token_type"],
        )

    def to_dict(self) -> dict:
        return {
            "access_token": self.access_token,
            "expires_at": int(self.expires_at.timestamp()),
            "token_type": self.token_type,
        }
