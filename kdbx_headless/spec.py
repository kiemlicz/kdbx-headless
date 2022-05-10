from typing import List, Tuple

from marshmallow import Schema, fields


class Secret:
    def __init__(self, secret: str, attachments: List[Tuple[str, str]] = None) -> None:
        self.secret = secret
        self.attachments = attachments


class SecretSchema(Schema):
    secret = fields.Str(metadata={'description': "plain-text secret data"})
    attachments = fields.List(
        fields.Tuple(
            [
                fields.Str(metadata={'description': "filename"}),
                fields.Str(metadata={'description': "file contents"})]
        )
    )
