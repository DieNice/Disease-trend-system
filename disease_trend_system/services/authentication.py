import sqlalchemy
import dash_auth as auth
from sqlalchemy import text
from disease_trend_system.config import (hostname_db, name_db, password_db,
                                         port, username_db)

from typing import Any, Dict, List, Tuple


class Authorizer:

    def __init__(self) -> None:
        self.engine = sqlalchemy.create_engine(
            f"mysql+pymysql://{username_db}:{password_db}@{hostname_db}:{port}/{name_db}")

    def add_authorization(self,app: Any)-> Any:
        users = self.get_users()
        return auth.BasicAuth(
        app, users
        )

    def get_users(self)-> Dict[str,str]:
        users = {}
        with self.engine.connect() as conn:
            user_data = conn.execute(text("Select username, password from users"))
            for data in user_data:
                users[data[0]] = data[1]
            return users
