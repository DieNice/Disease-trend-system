import hashlib
import json
from dataclasses import asdict, astuple, dataclass
from datetime import datetime
from typing import Any, Dict, Generator, List

import sqlalchemy
from flask import request
from flask_restful import Resource, inputs, reqparse
from sqlalchemy import MetaData
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import text

from disease_trend_system.config import (hostname_db, name_db, password_db,
                                         port, username_db)
from disease_trend_system.services.symptom_complexes_dao import SymptomDTO


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
                city=symptom_complex["city"],
                region=symptom_complex["region"],
                hospital=symptom_complex["hospital"],
                date=symptom_complex["date_symptoms"],
                symptom_hash=symptom_hash,
                symptom_complex_hash=symptom_complex_hash))

        return result_lst
