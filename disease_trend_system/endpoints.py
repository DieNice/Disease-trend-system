from flask_restful import Resource, inputs, reqparse


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
        args = self.parser.parse_args()
        # some logic for adding
        return {'message': 'successfull added'}
