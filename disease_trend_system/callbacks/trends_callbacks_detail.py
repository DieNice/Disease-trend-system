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
from disease_trend_system.services.fake_name_service import \
    generate_fake_symptom_complex_name
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
    State("id_threshold_input-2", "value"),
    State("dropdown-city-2", "value"),
    State("dropdown-region-2", "value"),
    State("dropdown-hospital-2", "value")
)
def update_table(n_clicks: int, start_date: datetime,
                 end_date: datetime, input_thresold: int,
                 city: str, region: str,
                 hospital: str):
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

    df = symptom_dao.get_trends_data(
        start_date, end_date, city, region, hospital)
    df = TrendDetector(input_thresold).execute(df)
    if not df.empty:
        df["symptom_complex_hash"] = df["symptom_complex_hash"].apply(
            generate_fake_symptom_complex_name)
    df["extra"] = df["extra"].apply(pprint_json)
    df["percent_people"] = df["percent_people"]/100

    if df.empty:
        return []

    return df.to_dict('records')


@app.callback(
    Output("dropdown-region-2", "options"),
    Input("dropdown-city-2", "value")
)
def update_dropdown_cities_2(city: str):
    """Обновить выпадающий список районов города

    Args:
        city (str): город
    """
    if city == '':
        return []
    symptom_dao = SymptomsDAO(
        username_db, password_db, hostname_db, port, name_db)
    return symptom_dao.get_regions_by_city(city)


@app.callback(
    Output("dropdown-hospital-2", "options"),
    Input("dropdown-city-2", "value"),
    Input("dropdown-region-2", "value")
)
def update_dropdown_hospitals_2(city: str, region: str):
    """Обновить выпадающий список мед. учреждение города и района

    Args:
        city (str): город

    """
    if city == '' or region == '':
        return []
    symptom_dao = SymptomsDAO(
        username_db, password_db, hostname_db, port, name_db)
    return symptom_dao.get_hospitals_by_city_region(city, region)
