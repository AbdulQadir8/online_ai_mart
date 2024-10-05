from sqlmodel import SQLModel, Field
import enum




class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"
    superuser = "super_user"


# Shared Properties
# Todo replace email str with EmailStr when SQLModel suppports it
class UserBase(SQLModel):
    user_name: str = Field(unique=True, index=True)
    email : str = Field(unique=True, index=True)
    is_active : bool = True
    is_superuser: bool = False
    full_name: str | None = None
    role: UserRole = Field(default=UserRole.user) 


# properties to recieve via API on creation
class UserCreate(UserBase):
    password: str


# Todo: replace email str with EmailStr when sqlmodel supports it
class UserRegister(SQLModel):
    email: str
    password: str
    user_name: str | None = None



# Properties to receive via API on update, all are optional
# Todo replace email str with EmailStr when sqlmodel supports it
class UserUpdate(UserBase):
    user_name: str | None = None
    email: str | None = None # type: ignore
    password: str | None = None


# Todo replace email str with EmailStr when sqlmodel supportd it
class UserUpdateMe(SQLModel):
    full_name: str | None = None
    email: str | None = None




# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    

# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: int


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Generic message 
class Message(SQLModel):
    message: str

# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None
    expires_in: int

# Content of JWT token 
class TokenPayload(SQLModel):
    sub: str | None = None

class PasswordResetRequest(SQLModel):
    email: str

class NewPassword(SQLModel):
    token: str
    new_password: str


class UpdatePassword(SQLModel):
    current_password: str
    new_password: str

