import json

class CustomJSONEncoder(json.JSONEncoder):
    """
    Custom JSON Encoder for handling complex numbers.

    This encoder converts complex numbers into a string representation
    and delegates other types to the base implementation.

    Methods:
        default(o): Overrides the default method to handle complex numbers.
    """
    def default(self, o):
        """
        Overrides the default method to provide custom serialization.

        Args:
            o: The object to serialize.

        Returns:
            str: String representation of complex numbers.
            Any: Base implementation for other types.
        """
        if isinstance(o, complex):
            #Converts complex numbers to a string representation
            return str(o).replace("(", "").replace(")", "")
        #For any other type, we let the base implementation handle it
        return super().default(o)
