import hashlib
import json
from dataclasses import asdict, astuple, dataclass
from datetime import datetime
from typing import Any, Dict, Generator, List

import sqlalchemy
from flask import request
from flask_restful import Resource, inputs, reqparse
from sqlalchemy import MetaData
from sqlalchemy.sql import text

from disease_trend_system.config import (hostname_db, name_db, password_db,
                                         port, username_db)


@dataclass
class SymptomDTO:
    """Data transfer object
    """
    name: str
    value: Any
    percent_people: float
    total_number: int
    date: datetime
    symptom_hash: str
    symptom_complex_hash: str

    def __post__init__(self):
        self.name = self.name.lower()
        if isinstance(self.value, str):
            self.value = self.value.lower()

    def __repr__(self) -> str:
        extra = str({self.name: self.value})
        extra = extra.replace('\'', '\"')
        return f"({self.total_number},'{self.date}',{self.percent_people},'{extra}','{self.symptom_hash}','{self.symptom_complex_hash}')"


class SymtomComplexTransform:
    """Класс преобразования симптомокомплексов в список объектов
    """

    @staticmethod
    def _dict_hash(dictionary: Dict[str, Any]) -> str:
        """MD5 hash of a dictionary."""
        dhash = hashlib.md5()
        encoded = json.dumps(dictionary, sort_keys=True).encode()
        dhash.update(encoded)
        return dhash.hexdigest()

    @staticmethod
    def symptom_complex_to_symptoms(symptom_complex: Dict[str, Any]) -> List[SymptomDTO]:
        """Преобразование симптомокомлексов в набор симптомов с хеш-ключами

        Args:
            symptom_complex (Dict): Симптомокомлекс

        Returns:
            List[SymptomDTO]: Список объектов ДТО класса
        """
        result_lst = []
        symptoms = symptom_complex["symptoms"]
        symptom_complex_hash = SymtomComplexTransform._dict_hash(symptoms)
        for k, v in symptoms.items():
            symptom_hash = SymtomComplexTransform._dict_hash({k: v})
            result_lst.append(SymptomDTO(
                name=k, value=v,
                percent_people=symptom_complex["percent_people"],
                total_number=symptom_complex["total_number_people"],
                date=symptom_complex["date_symptoms"],
                symptom_hash=symptom_hash,
                symptom_complex_hash=symptom_complex_hash))

        return result_lst


class SymptomsDAO:
    """Объект доступа к таблице symptom_complexes
    """
    @staticmethod
    def _symptoms_to_dict(symptoms: List[SymptomDTO]) -> Generator:
        """Список DTO в список словарей

        Args:
            symptoms (List[SymptomDTO]): Список симптомов

        Returns:
            Generator: Генератор в словари
        """
        for symptom in symptoms:
            extra = str({symptom.name: symptom.value})
            symptom_dict = asdict(symptom)
            symptom_dict.pop("name")
            symptom_dict.pop("value")
            symptom_dict["extra"] = extra
            yield symptom_dict
            del symptom_dict

    def __init__(self, usr: str, pswd: str, host: str, port: int, db: str) -> None:
        self.engine = sqlalchemy.create_engine(
            f"mysql+pymysql://{usr}:{pswd}@{host}:{port}/{db}")
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)
        self.metadata.create_all(bind=self.engine, checkfirst=True)

    def _insert(self, symptoms: List[SymptomDTO]) -> None:
        """Вставка данных в таблицу

        Args:
            symptoms (List[SymptomDTO]): Список симптомов (симтомокоплекс)
        """
        self.metadata.reflect(bind=self.engine)
        tbl = self.metadata.tables['symptom_complexes']
        self.metadata.create_all(bind=self.engine, checkfirst=True)
        with self.engine.connect() as conn:
            for symptom_dict in SymptomsDAO._symptoms_to_dict(symptoms):
                conn.execute(tbl.insert(),
                             symptom_dict)
            conn.commit()

    def _insert_with_concurrency(self, symptoms: List[SymptomDTO]) -> None:
        """Вставка данных с учетом пересечений с другими симптомокомлексами

        Args:
            symptoms (List[SymptomDTO]): Список симптомов
        """
        min_con = len(symptoms) - 1
        max_con = len(symptoms) + 1
        values = ','.join([str(symptom) for symptom in symptoms])
        queries = {}
        queries['query_1'] = '''create temporary table if not exists `symptom_complexes_temp` (
                `total_number` int unsigned NOT NULL,
                `date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
                `percent_people` double NOT NULL,
                `extra` json NOT NULL,
                `symptom_hash` varchar(32) NOT NULL,
                `symptom_complex_hash` varchar(32) NOT NULL
                );'''
        queries['query_2'] = "truncate symptom_complexes_temp;"
        queries['query_3'] = '''create temporary table if not exists `symptom_complexes_hash_temp` (
                `symptom_complex_hash` varchar(32) NOT NULL
                );'''
        queries['query_4'] = "truncate symptom_complexes_hash_temp;"
        queries['query_5'] = f'''insert
                    into
                    symptom_complexes_temp (total_number,
                    date,
                    percent_people,
                    extra,
                    symptom_hash,
                    symptom_complex_hash
                    )
                values
                   {values};'''
        queries['query_6'] = f'''insert
                    into
                    symptom_complexes_hash_temp (symptom_complex_hash)
                with cte as (
                select
                    sc.*,
                    sct.total_number as '_total_number',
                    sct.`date` as '_date',
                    sct.percent_people as '_percent_people',
                    sct.extra as '_extra',
                    sct.symptom_hash as '_symptom_hash',
                    sct.symptom_complex_hash as '_symptom_complex_hash'
                from
                    symptom_complexes_temp sct
                left join symptom_complexes sc on
                    sct.symptom_hash = sc.symptom_hash
                order by
                    sct.symptom_hash),
                cte_2 as (
                select
                    distinct symptom_complex_hash as symptom_complex_hash
                from
                    (
                    select
                        cte.*,
                        count(1) over (partition by symptom_complex_hash) as `concurrency`
                    from
                        cte) mt
                where
                    mt.concurrency BETWEEN {min_con} and {max_con})
                select
                    symptom_complex_hash
                from
                    cte_2;'''
        queries['query_7'] = '''insert
                    into
                    symptom_complexes(total_number,
                    `date`,
                    percent_people,
                    extra,
                    symptom_hash,
                    symptom_complex_hash
                ) select
                    sct.total_number,
                    sct.`date`,
                    sct.percent_people,
                    sct.extra,
                    sct.symptom_hash,
                    scht.symptom_complex_hash
                from
                    symptom_complexes_hash_temp scht
                cross join symptom_complexes_temp sct;'''
        queries['query_8'] = '''insert into symptom_complexes(total_number,
                    `date`,
                    percent_people,
                    extra,
                    symptom_hash,
                    symptom_complex_hash)
                select total_number,
                    `date`,
                    percent_people,
                    extra,
                    symptom_hash,
                    symptom_complex_hash from symptom_complexes_temp;'''
        queries['query_9'] = "truncate symptom_complexes_temp;"
        queries['query_10'] = "truncate symptom_complexes_hash_temp;"
        queries['query_11'] = "drop table if exists symptom_complexes_temp;"
        queries['query_12'] = "drop table if exists symptom_complexes_hash_temp;"

        with self.engine.connect() as conn:
            for _, query in queries.items():
                conn.execute(text(query))
                conn.commit()

    def save_symptoms(self, symptoms: List[SymptomDTO]) -> None:
        """Сохранение списка симптов (симптомокомлекс) в таблицу

        Args:
            symptoms (List[SymptomDTO]): Симптомокомлекс

        """
        symptom_complex_hash = symptoms[0].symptom_complex_hash
        with self.engine.connect() as conn:

            symptom_complex_hash_exist_query = text(
                f"select id from symptom_complexes sc where sc.symptom_complex_hash = '{symptom_complex_hash}'")
            proxy_result = conn.execute(symptom_complex_hash_exist_query)
            flag_exists = bool([row._data for row in proxy_result])
        if flag_exists:
            self._insert(symptoms)
        else:
            self._insert_with_concurrency(symptoms)


class SymptomsResource(Resource):
    """Ендоинт для сохранения сиптомокомлексов
    """

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("symptoms", type=dict, required=True)
        self.parser.add_argument("percent_people", type=float, required=True)
        self.parser.add_argument(
            "total_number_people", type=float, required=True)
        self.parser.add_argument(
            "date_symptoms", type=inputs.datetime_from_iso8601, required=True)

    def post(self):
        _ = self.parser.parse_args()
        symptom_complex = request.get_json()

        try:
            _ = symptom_complex["symptoms"]
        except KeyError as _:
            return {"message": "Can't contains symptoms"}
        else:
            symptoms = SymtomComplexTransform.symptom_complex_to_symptoms(
                symptom_complex)
            symptom_dao = SymptomsDAO(
                username_db, password_db, hostname_db, port, name_db)
            symptom_dao.save_symptoms(symptoms)

        return {'message': 'successfull added'}
