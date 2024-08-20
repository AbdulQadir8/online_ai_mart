from jose import jwt
from datetime import datetime, timedelta

ALGORITHM: str = "HS256"
SECRET_KEY: str = "Secure Secret Key"

def create_access_token(subject: str, expires_delta: timedelta) -> str:
        expire = datetime.utcnow() + expires_delta
        to_encode = {"exp":expire, "sub": str(subject)}
        encode_jwt = jwt.encode(to_encode, SECRET_KEY , algorithm=ALGORITHM)
        return encode_jwt
   
def decode_token(token: str):
    decoded_token_data = jwt.decode(token, SECRET_KEY , algorithms=[ALGORITHM])
    return {"decoded_token": decoded_token_data}
   
    

