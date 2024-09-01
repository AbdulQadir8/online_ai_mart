from sqlmodel import select, Session
from app.models.user_model import  User, UserCreate, UserUpdate
from app.utils import get_hashed_password
from typing import Any
from app.deps import SessionDep

def get_user_by_email(*,session: Session, email: str):
       statement = select(User).where(User.email == email)
       session_user = session.exec(statement).one_or_none()
       return session_user

def create_user(*, session: SessionDep, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_hashed_password(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: SessionDep, db_user: User, user_in: UserUpdate) -> Any:
      user_data = user_in.model_dump(exclude_unset=True)
      extra_data= {}
      if "password" in user_data:
            password = user_data["password"]
            hashed_password = get_hashed_password(password)
            extra_data["hashed_password"] = hashed_password
      db_user.sqlmodel_update(user_data, update=extra_data)
      session.add(db_user)
      session.commit()
      session.refresh(db_user)
      return db_user
            
      