from fastapi import HTTPException, Depends
from requests import get, post
from app.utils import load_error_json
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login-endpoint")


def get_current_user(token: Annotated[str | None, Depends(oauth2_scheme)]):
    url = "http://user-service:8000/me"
    headers = {"Authorization":f"Bearer {token}"}
    response = get(url=url, headers=headers)
    print("AUTHENTICATED_USER_DATA: ",response.json())

    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=load_error_json(response))

def login_for_access_token(form_data):
    url = "http://user-service:8000/login"
    data = {
        "username": form_data.username,
        "password":form_data.password
    }
    response = post(url, data=data)
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=load_error_json(response))
