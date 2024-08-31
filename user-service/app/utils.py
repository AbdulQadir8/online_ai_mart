from jose import jwt
import secrets
from datetime import datetime, timedelta
from passlib.context import CryptContext



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM: str = "HS256"
SECRET_KEY: str = "The new Secret key"


def create_access_token(subject: str, expires_delta: timedelta) -> str:
        expire = datetime.utcnow() + expires_delta
        to_encode = {"exp":expire, "sub": str(subject)}
        encode_jwt = jwt.encode(to_encode, SECRET_KEY , algorithm=ALGORITHM)
        return encode_jwt
   
def decode_token(token: str):
    decoded_token_data = jwt.decode(token, SECRET_KEY , algorithms=[ALGORITHM])
    return decoded_token_data
   
    

def get_hashed_password(password: str) -> str:
      return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
      return pwd_context.verify(plain_password, hashed_password)