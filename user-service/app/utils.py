from jose import jwt, JWTError
import secrets
from datetime import datetime, timedelta
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM: str = "HS256"
SECRET_KEY: str = "The access token new Secret key"
REFRESH_TOKEN_SECRET_KEY = "The refresh-token-secret"
RESET_TOKEN_SECRET_KEY = "The reset-token-secret"

ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Token expiration time




def create_access_token(subject: str, expires_delta: timedelta) -> str:
        expire = datetime.utcnow() + expires_delta
        to_encode = {"exp":expire, "sub": str(subject)}
        return jwt.encode(to_encode, SECRET_KEY , algorithm=ALGORITHM)

def create_refresh_token(subject: str, expires_delta: timedelta = timedelta(days=7)) -> str:
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": subject}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)        

   
def decode_token(token: str):
    decoded_token_data = jwt.decode(token, SECRET_KEY , algorithms=[ALGORITHM])
    return decoded_token_data
   
    

def get_hashed_password(password: str) -> str:
      return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
      return pwd_context.verify(plain_password, hashed_password)

ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Token expiration time

def create_reset_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, REFRESH_TOKEN_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_reset_token(token: str):
    try:
        payload = jwt.decode(token, REFRESH_TOKEN_SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None


