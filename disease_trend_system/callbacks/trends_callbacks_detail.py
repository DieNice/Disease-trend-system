import json
from datetime import datetime
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
    Output("table-1", "data"),
    Input("btn-2", "n_clicks"),
    Input("date-range-2", "start_date"),
    Input("date-range-2", "end_date"),
    State("id_threshold_input-2", "value")
)
def update_table(n_clicks: int, start_date: datetime,
                 end_date: datetime, input_thresold: int):
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
    if input_thresold is None:
        raise PreventUpdate
    symptom_dao = SymptomsDAO(
        username_db, password_db, hostname_db, port, name_db)

    df = symptom_dao.get_trends_data(start_date, end_date)
    df = TrendDetector(input_thresold).execute(df)
    df["extra"] = df["extra"].apply(pprint_json)
    df["percent_people"] = df["percent_people"]/100

    if df.empty:
        return []

    return df.to_dict('records')
