import json
from datetime import datetime
from typing import Any, Dict

import plotly.express as px
from dash import no_update
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Input, Output, State, html
from numpy.typing import ArrayLike
from pandas import DataFrame

from disease_trend_system.app import app
from disease_trend_system.config import (hostname_db, name_db, password_db,
                                         port, username_db)
from disease_trend_system.services.symptom_complexes_dao import SymptomsDAO


class TrendDetector:
    """Класс фильтрующий тренды

    """

    def _is_desc_sorted(self, arr: ArrayLike) -> bool:
        if len(arr) == 1:
            return False
        for i in range(arr.size-1):
            if arr[i+1] > arr[i]:
                return False
        return True

    def __init__(self, trend_threshold: int) -> None:
        self.threshold = trend_threshold

    def execute(self, df: DataFrame) -> DataFrame:
        hashes = df["symptom_complex_hash"].unique()
        bad_hashes = []
        for iter_hash in hashes:
            tmp_df = df[df["symptom_complex_hash"] == iter_hash]
            tmp_df.sort_values(by=["date"], ascending=True, inplace=True)
            if len(tmp_df) < self.threshold:
                bad_hashes.append(iter_hash)
                continue
            if self._is_desc_sorted(tmp_df.total_number.to_numpy()):
                bad_hashes.append(iter_hash)
        return df[~df["symptom_complex_hash"].isin(bad_hashes)]


@app.callback(
    Output("graph-1", "figure"),
    Input("btn-1", "n_clicks"),
    Input("date-range-1", "start_date"),
    Input("date-range-1", "end_date"),
    State("id_threshold_input", "value")
)
def update_line_chart(n_clicks: int, start_date: datetime,
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
    State("id_threshold_input", "value")
)
def display_hover(hoverData: Dict[str, Any],
                  start_date: datetime,
                  end_date: datetime,
                  input_thresold: int):
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
    df = symptom_dao.get_trends_data(start_date, end_date)
    df = TrendDetector(input_thresold).execute(df)
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
