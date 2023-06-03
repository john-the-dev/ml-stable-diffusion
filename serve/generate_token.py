import secrets
import string

alphabet = string.ascii_letters + string.digits
size = 20
token = ''.join(secrets.choice(alphabet) for i in range(size))
print(f"generated a token with {size} length: {token}")