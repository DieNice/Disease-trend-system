from datetime import datetime

import plotly.express as px
from dash_extensions.enrich import Input, Output, html

from disease_trend_system.app import app
from disease_trend_system.config import (hostname_db, name_db, password_db,
                                         port, username_db)
from disease_trend_system.services.symptom_complexes_dao import SymptomsDAO


@app.callback(
    Output("graph-1", "figure"),
    Input("btn-1", "n_clicks"))
def update_line_chart(n_clicks: int):
    symptom_dao = SymptomsDAO(
        username_db, password_db, hostname_db, port, name_db)
    df = symptom_dao.get_trends_data(
        datetime(2023, 1, 1), datetime(2023, 4, 23))
    fig = px.line(df,
                  x="date", y="percent_people", color="symptom_complex_hash", markers=True)
    return fig
