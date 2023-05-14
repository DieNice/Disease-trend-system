import json
from datetime import datetime, timedelta
from typing import Any, Dict

import plotly.express as px
from dash import no_update
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Input, Output, State, html

from disease_trend_system.app import app
from disease_trend_system.config import (hostname_db, name_db, password_db,
                                         port, username_db)
from disease_trend_system.services.create_data_trend import TrendDetector
from disease_trend_system.services.symptom_complexes_dao import SymptomsDAO

MAX_DELTA = 30


def pprint_json(json_str: str) -> str:
    """Форматирование json строк

    Args:
        json_str (str): входная json строка

    Returns:
        str: выходная json строка
    """
    tmp_str = json_str
    tmp_str = tmp_str.replace('\'', '\"')
    tmp_str = tmp_str.replace('\"{', '{')
    tmp_str = tmp_str.replace('}\"', '}')
    tmp_dict = json.loads(tmp_str)
    result_str = ""
    for k, v in tmp_dict.items():
        result_str += f"{k}:{v}\n"
    return result_str


@app.callback(
    Output("table-2", "data"),
    Output("header-report", "children"),
    Input("date-range-3", "date")
)
def update_raiting_table(date: datetime):
    """Обновление графика трендов

    Args:
        n_clicks (int): Нажатие на кнопку
        start_date (datetime): Начала периода
        end_date (datetime): Конец периода
        input_thresold (int): Порог тренда

    Raises:
        PreventUpdate: Не обновлять

    Returns:
        Figure: Объект Figure
    """

    symptom_dao = SymptomsDAO(
        username_db, password_db, hostname_db, port, name_db)
    end_date = datetime.fromisoformat(date)
    start_date = end_date - timedelta(days=MAX_DELTA)
    df = symptom_dao.get_trends_data(start_date, end_date)

    d1 = start_date.strftime("%d/%m/%Y")
    d2 = end_date.strftime("%d/%m/%Y")
    header_report = f"Рейтинг симптомокомлексов с {d1} по {d2}"
    df["extra"] = df["extra"].apply(pprint_json)
    df["percent_people"] = df["percent_people"]/100
    agg_df = df.groupby(["symptom_complex_hash", "extra"]).agg(
        {"date": "count", "percent_people": "max", "total_number": "max"})
    agg_df = agg_df.reset_index()
    agg_df = agg_df.sort_values(['date'], ascending=False)

    if df.empty:
        return [], header_report

    return agg_df.to_dict('records'), header_report
