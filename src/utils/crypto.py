import hashlib
import base64
import uuid

def md5(s: str):
    hash = hashlib.md5(s.encode())
    return base64.urlsafe_b64encode(hash.digest()).decode()

def generate_base64_url_safe_uuid():
    uuid_value = uuid.uuid4()
    uuid_bytes = uuid_value.bytes
    base64_url_safe = base64.urlsafe_b64encode(uuid_bytes)
    base64_url_safe_string = base64_url_safe.decode('utf-8')
    return base64_url_safe_string