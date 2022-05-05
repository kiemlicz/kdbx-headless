from typing import List, Tuple

from marshmallow import Schema


class Secret:
    def __init__(self, secret: str, attachments: List[Tuple[str, str]] = None) -> None:
        self.secret = secret
        self.attachments = attachments


class SecretSchema(Schema):
    class Meta:
        fields = ("secret", "attachments", "creds")
