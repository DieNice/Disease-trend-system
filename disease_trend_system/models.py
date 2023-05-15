from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import (Column, DateTime, Double, Integer, MetaData, String,
                        event)
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy_utils import JSONType
from werkzeug.security import check_password_hash, generate_password_hash

from disease_trend_system.config import (SECRET_KEY, hostname_db, name_db,
                                         password_db, port, username_db)
from disease_trend_system.endpoints import SymptomsResource

Base = declarative_base()


class SymptomComplexes(Base):
    """Класс симптомокомплексов
    """
    __tablename__ = 'symptom_complexes'
    id = Column(Integer, primary_key=True)
    total_number = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=False)
    percent_people = Column(Double, nullable=False)
    city = Column(String(64), nullable=False)
    region = Column(String(128), nullable=False)
    hospital = Column(String(128), nullable=False)
    extra = Column(JSONType, nullable=False)
    symptom_hash = Column(String(32), nullable=False)
    symptom_complex_hash = Column(String(32), nullable=False)


class User(Base, UserMixin):
    """Класс пользователя
    """

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(120), nullable=False)
    role = Column(Integer, nullable=False)
    created_on = Column(DateTime, default=datetime.utcnow)
    updated_on = Column(DateTime(), default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    def __repr__(self):
        return f"User {self.id}:{self.username}>"

    def set_password(self, password: str) -> None:
        """Установка пароля

        Args:
            password (str): пароль
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self,  password: str) -> bool:
        """Проверка пароля на соответствие

        Args:
            password (str): пароль

        Returns:
            bool: Да/Нет
        """
        return check_password_hash(self.password, password)


@event.listens_for(User.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    if value != oldvalue:
        return generate_password_hash(value)
    return value
