import bcrypt

import sys
import os
sys.path.append(os.path.join(sys.path[0], '..'))


def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password=pwd_bytes, salt=salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_byte_enc, hashed_password_byte_enc = plain_password.encode(
        'utf-8'), hashed_password.encode('utf-8')
    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password_byte_enc)


if __name__ == "__main__":
    # Example usage
    password = "my_secure_password"
    hashed_password = hash_password(password)
    print(f"Original Password: {password}")
    print(f"Hashed Password: {hashed_password}")

    # Verify the hash
    assert verify_password(
        password, hashed_password), "Password hash does not match!"
    print("Password hash verification successful!")
