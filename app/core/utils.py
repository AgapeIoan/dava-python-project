import json

class CustomJSONEncoder(json.JSONEncoder):
    """
    Un encoder JSON custom care stie sa serializeze obiecte de tip 'complex'.
    """
    def default(self, o):
        if isinstance(o, complex):
            # Convertim numarul complex intr-un string, formatul standard
            return str(o).replace("(", "").replace(")", "")
        # Pentru orice alt tip, lasam implementarea de baza sa se ocupe
        return super().default(o)
    
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_api_key(api_key: str) -> str:
    return pwd_context.hash(api_key)

def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    return pwd_context.verify(plain_key, hashed_key)