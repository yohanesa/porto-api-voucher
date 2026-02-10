import string
import secrets

class CodeGenerator:
    def __init__(self):
        # We use a set to keep track of generated codes for O(1) lookup speed
        self.generated_codes = set()

    def generate(self, length=10):
        """Generates a unique, uppercase alphanumeric code."""
        # Define our pool: A-Z and 0-9
        characters = string.ascii_uppercase + string.digits
        
        while True:
            # Create a random string of the specified length
            code = ''.join(secrets.choice(characters) for _ in range(length))
            
            # Check for uniqueness
            if code not in self.generated_codes:
                self.generated_codes.add(code)
                return code