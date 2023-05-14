from dataclasses import asdict, dataclass
from datetime import datetime
from functools import cache
from typing import Any, Generator, List

import pandas as pd
import sqlalchemy
from pandas import DataFrame
from sqlalchemy import MetaData
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import text


@dataclass
class SymptomDTO:
    """Data transfer object
    """
    name: str
    value: Any
    percent_people: float
    total_number: int
    city: str
    region: str
    hospital: str
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
        return f"({self.total_number},'{self.date}',{self.percent_people},'{self.city}','{self.region}','{self.hospital}','{extra}','{self.symptom_hash}','{self.symptom_complex_hash}')"


class SymptomsDAO:
    """Объект доступа к таблице symptom_complexes
    """
    @staticmethod
    def _symptoms_to_dict(symptoms: List[SymptomDTO]) -> Generator:
        """Список DTO в список словарей

        Args:symptom_complexe
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
            conn.close()
        self.engine.dispose()

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
                `city` varchar(64) NOT NULL,
                `region` varchar(128) NOT NULL,
                `hospital` varchar(128) NOT NULL,
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
                    city,
                    region,
                    hospital,
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
                    sct.city as '_city',
                    sct.region as '_region',
                    sct.hospital as '_hospital',
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
                    city,
                    region,
                    hospital,
                    extra,
                    symptom_hash,
                    symptom_complex_hash
                ) select
                    sct.total_number,
                    sct.`date`,
                    sct.percent_people,
                    sct.city,
                    sct.region,
                    sct.hospital,
                    sct.extra,
                    sct.symptom_hash,
                    scht.symptom_complex_hash
                from
                    symptom_complexes_hash_temp scht
                cross join symptom_complexes_temp sct;'''
        queries['query_8'] = '''insert into symptom_complexes(total_number,
                    `date`,
                    percent_people,
                    city,
                    region,
                    hospital,
                    extra,
                    symptom_hash,
                    symptom_complex_hash)
                select total_number,
                    `date`,
                    percent_people,
                    city,
                    region,
                    hospital,
                    extra,
                    symptom_hash,
                    symptom_complex_hash from symptom_complexes_temp;'''
        queries['query_9'] = "truncate symptom_complexes_temp;"
        queries['query_10'] = "truncate symptom_complexes_hash_temp;"
        queries['query_11'] = "drop table if exists symptom_complexes_temp;"
        queries['query_12'] = "drop table if exists symptom_complexes_hash_temp;"

        try:
            with self.engine.connect() as conn:
                for _, query in queries.items():
                    conn.execute(text(query))
                    conn.commit()
        except IntegrityError as _:
            with self.engine.connect() as conn:
                query = f'''insert
                    into
                    symptom_complexes (total_number,
                    date,
                    percent_people,
                    city,
                    region,
                    hospital,
                    extra,
                    symptom_hash,
                    symptom_complex_hash
                    )
                values
                   {values};'''
                conn.execute(text(query))
                conn.commit()
                conn.close()

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
        self.engine.dispose()

    @cache
    def get_trends_data(self, start_date: datetime, end_date: datetime) -> DataFrame:
        """Получить график трендов

        Args:
            start_date (datetime): Начала диапазона
            end_date (datetime): Конец диапазона

        Returns:
            DataFrame: Датафрейм с данными
        """
        special_replace = '"},{"'
        query_text = f'''with filtered_dates as (
                select
                    sc.id ,
                    sc.total_number,
                    sc.percent_people,
                    sc.city,
                    sc.region,
                    sc.hospital,
                    sc.extra,
                    sc.symptom_hash,
                    sc.symptom_complex_hash,	
                    date_format(sc.`date`, "%Y-%m-%d") as `date`
                from
                    symptom_complexes sc
                where
                    (date_format(sc.`date`, "%Y-%m-%d") BETWEEN date('{start_date}') and date('{end_date}')))
                select
                    sc.symptom_complex_hash,
                    sc.date,
                    avg(sc.percent_people) as percent_people,
                    count(sc.total_number) as num_symp,
                    avg(sc.total_number) as total_number,
                    replace(GROUP_CONCAT(distinct(sc.extra)), {special_replace}, ",") as extra
                from
                    filtered_dates sc
                group by
                    sc.`date`,
                    sc.symptom_complex_hash
                order by
                    `date`
        '''
        with self.engine.connect() as conn:
            df = pd.read_sql(text(query_text), conn)
            conn.close()
            self.engine.dispose()

        return df
