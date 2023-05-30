import random
import string


def generate_token():
    letters_and_digits = string.ascii_letters + string.digits
    token = ''.join(random.choice(letters_and_digits) for _ in range(32))
    return token
