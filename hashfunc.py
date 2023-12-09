import hashlib

def hash(key): 
    hash_object = hashlib.sha256(key.encode())
    return hash_object.hexdigest()

# Example usage:
hashed_value = hash("Hello, world!")
print("Hashed value:", hashed_value)