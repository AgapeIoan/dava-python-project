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
