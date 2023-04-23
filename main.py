import os
from typing import Any

import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash_extensions.enrich import Input, Output, html

from disease_trend_system.app import app
from disease_trend_system.app import srv as server
from disease_trend_system.callbacks.trends_callbacks import update_line_chart
from disease_trend_system.layouts.navbar import Navbar
from disease_trend_system.layouts.trends_layout import trends_layout

app_name = os.getenv("DASH_APP_PATH", "/disease_trend_system")

nav = Navbar()


header = html.Div(
    children=[
        html.H1(
            children="", className="header-title"
        ),
    ],
    className="header",
)

content = html.Div([dcc.Location(id="url"), html.Div(id="page-content")])

container = dbc.Container([header, content])


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname: str) -> Any:
    """Функция для оторисовки страниц

    Args:
        pathname (str): url

    Returns:
        Any: Layout
    """

    if pathname in [app_name, app_name + "/", '/']:
        return html.Div(
            [
                dcc.Markdown(
                    """
            Данное приложение необходимо для анализа трендов симптомокомплексов             
        """, className='main-content'
                ),
                html.Img(src="./assets/images/picture_3.jpeg",
                         style={"display": "block", "margin-left": "auto", "margin-right": "auto"})
            ],
            className="home",
        )
    elif pathname.endswith("/trends"):
        return trends_layout()
    elif pathname.endswith("/symptoms"):
        return ""
    elif pathname.endswith("/rating"):
        return ""
    else:
        return "ERROR 404: Page not found!"


def index():
    return html.Div([nav, container])


app.layout = index()

if __name__ == '__main__':
    app.run_server(host='localhost', port=8050, debug=False)
