import json
from datetime import datetime
from typing import Any, Dict

import plotly.express as px
import plotly.graph_objs as go
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


@app.callback(
    Output("graph-1", "figure"),
    Input("btn-1", "n_clicks"),
    Input("date-range-1", "start_date"),
    Input("date-range-1", "end_date"),
    State("id_threshold_input", "value"),
    State("dropdown-city-1", "value"),
    State("dropdown-region-1", "value"),
    State("dropdown-hospital-1", "value")
)
def update_line_chart(n_clicks: int, start_date: datetime,
                      end_date: datetime, input_thresold: int,
                      city: str, region: str, hospital: str):
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
    fig = px.line(df,
                  x="date", y="percent_people", color="symptom_complex_hash", markers=True)
    fig.update_traces(mode="markers+lines", hovertemplate=None)

    return fig


@app.callback(
    Output("graph-tooltip", "show"),
    Output("graph-tooltip", "bbox"),
    Output("graph-tooltip", "children"),
    Input("graph-1", "hoverData"),
    State("date-range-1", "start_date"),
    State("date-range-1", "end_date"),
    State("id_threshold_input", "value"),
    State("dropdown-city-1", "value"),
    State("dropdown-region-1", "value"),
    State("dropdown-hospital-1", "value")
)
def display_hover(hoverData: Dict[str, Any],
                  start_date: datetime,
                  end_date: datetime,
                  input_thresold: int,
                  city: str, region: str,
                  hospital: str):
    """Подсказка при наведении

    Args:
        hoverData (Dict[str,Any]): Данные при наведении на точку
        start_date (datetime): Начало периода
        end_date (datetime): Конец периода
        input_thresold (int): Порог тренда

    Returns:
        Tuple[bool,Dict,List]: Кортеж для tooltip
    """
    if hoverData is None:
        return False, no_update, no_update

    pt = hoverData["points"][0]
    bbox = pt["bbox"]
    symptom_dao = SymptomsDAO(
        username_db, password_db, hostname_db, port, name_db)
    df = symptom_dao.get_trends_data(
        start_date, end_date, city, region, hospital)

    df = TrendDetector(input_thresold).execute(df)
    if not df.empty:
        df["symptom_complex_hash"] = df["symptom_complex_hash"].apply(
            generate_fake_symptom_complex_name)
    df = df[df["date"] == pt["x"]]
    df = df[df["percent_people"] == pt["y"]]
    df = df.iloc[0]

    hover_data = df.to_dict()
    hover_data["extra"] = hover_data["extra"].replace('\'', '\"')
    hover_data["extra"] = hover_data["extra"].replace('\"{', '{')
    hover_data["extra"] = hover_data["extra"].replace('}\"', '}')
    num_symp = len(json.loads(hover_data["extra"]))
    sympt_hash = hover_data["symptom_complex_hash"]
    date = hover_data["date"]
    name = f"Симптомокомлекс {sympt_hash} {date}"
    form = f"Число симптомов {num_symp}"
    desc = hover_data["extra"]
    if len(desc) > 300:
        desc = desc[:100] + '...'

    children = [
        html.Div([
            html.H3(f"{name}", style={"color": "darkblue",
                    "overflow-wrap": "break-word"}),
            html.P(f"{form}"),
            html.P(f"{desc}"),
        ], style={'width': '20vw', 'white-space': 'normal'})
    ]

    return True, bbox, children


@app.callback(
    Output("dropdown-region-1", "options"),
    Input("dropdown-city-1", "value")
)
def update_dropdown_cities(city: str):
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
    Output("dropdown-hospital-1", "options"),
    Input("dropdown-city-1", "value"),
    Input("dropdown-region-1", "value")
)
def update_dropdown_hospitals(city: str, region: str):
    """Обновить выпадающий список мед. учреждение города и района

    Args:
        city (str): город

    """
    if city == '' or region == '':
        return []
    symptom_dao = SymptomsDAO(
        username_db, password_db, hostname_db, port, name_db)
    return symptom_dao.get_hospitals_by_city_region(city, region)
