import json

class CustomJSONEncoder(json.JSONEncoder):
    """
    #Custom JSON Encoder for complex numbers.
    """
    def default(self, o):
        if isinstance(o, complex):
            #Converts complex numbers to a string representation
            return str(o).replace("(", "").replace(")", "")
        #For any other type, we let the base implementation handle it
        return super().default(o)
