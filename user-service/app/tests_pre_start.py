import logging

from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, select
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app import settings 
from app.db_engine import  test_engine
from app.crud.user_crud import create_user
from app.models.user_model import User, UserCreate, UserRole



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 1# 5 minutes
wait_seconds = 1



def create_tables(*, db_engine: Engine) -> None:
    # Create All Tables
    # SQLModel.metadata.drop_all(db_engine)
    logging.info("Creating all tables")
    SQLModel.metadata.create_all(db_engine)

@retry(
        stop=stop_after_attempt(max_tries),
        wait=wait_fixed(wait_seconds),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.WARN),
)

def init_test_db(db_engine: Engine) -> None:
    try:
        # Try to create session to check if DB is awake
        logging.info("Checking if DB is awake")
        create_tables(db_engine=db_engine)
        with Session(db_engine) as session:
            session.exec(select(1))
            user = session.exec(
                select(User).where(User.email == settings.FIRST_SUPERUSER)
            ).first()
            if not user:
                user_in = UserCreate(
                    user_name="usama123",
                    email=settings.FIRST_SUPERUSER,
                    password=settings.FIRST_SUPERUSER_PASWORD,
                    is_superuser=True,
                    role=UserRole.admin
                )
            user = create_user(session=session,user_create=user_in)

    except Exception as e:
        logging.error(e)
        raise e
    
def main() -> None:
    logger.info("Iniializing service")
    init_test_db(test_engine)
    logger.info("Service finished initializing")

if __name__=="__main__":
    main()