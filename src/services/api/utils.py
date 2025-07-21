import random
import string
from uuid import UUID

datetime_url_format = "%Y-%m-%dT%H:%M"


def generate_token_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=5))

class UUIDConverter:
    regex = '[0-9a-fA-F-]+'  # Regex para UUID com hífens

    def to_python(self, value):
        return UUID(value)

    def to_url(self, value):
        return str(value)
