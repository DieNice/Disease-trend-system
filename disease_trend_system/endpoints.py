from flask import request
from flask_restful import Resource, inputs, reqparse

from disease_trend_system.config import (hostname_db, name_db, password_db,
                                         port, username_db)
from disease_trend_system.services.symptom_complex_transform import \
    SymtomComplexTransform
from disease_trend_system.services.symptom_complexes_dao import SymptomsDAO


class SymptomsResource(Resource):
    """Ендоинт для сохранения сиптомокомлексов
    """

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("symptoms", type=dict, required=True)
        self.parser.add_argument("percent_people", type=float, required=True)
        self.parser.add_argument("city", type=str, required=True)
        self.parser.add_argument("region", type=str, required=True)
        self.parser.add_argument("hospital", type=str, required=True)
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
