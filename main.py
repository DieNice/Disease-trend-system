import os
from typing import Any

import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash import no_update
from dash.dash import PreventUpdate
from dash_extensions.enrich import Input, Output, html
from flask_login import current_user, logout_user

from disease_trend_system.app import app
from disease_trend_system.app import srv as server
from disease_trend_system.callbacks.auth_callbalcks import (login_button_click,
                                                            login_status)
from disease_trend_system.callbacks.raiting_callbacks import \
    update_raiting_table
from disease_trend_system.callbacks.trends_callbacks import (display_hover,
                                                             update_line_chart)
from disease_trend_system.callbacks.trends_callbacks_detail import update_table
from disease_trend_system.layouts.auth_layout import (failed, login, logout,
                                                      success)
from disease_trend_system.layouts.navbar import Navbar
from disease_trend_system.layouts.raiting_layout import raiting_layout
from disease_trend_system.layouts.trends_layout import trends_layout
from disease_trend_system.layouts.trends_layout_detail import \
    trends_layout_detail

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


@app.callback(Output('page-content', 'children'), Output('redirect', 'pathname'),
              [Input('url', 'pathname')])
def display_page(pathname: str) -> Any:
    """Функция для оторисовки страниц

    Args:
        pathname (str): url

    Returns:
        Any: Layout
    """
    if pathname is None:
        raise PreventUpdate
    view = no_update
    url = no_update
    if pathname.endswith("/login"):
        view = login()
    elif pathname in [app_name, app_name + "/", '/']:
        view = html.Div(
            [
                dcc.Markdown(
                    """      
        """, className='main-content'
                ),
                html.Img(src="./assets/images/picture_3.jpeg",
                         style={"display": "block", "margin-left": "auto", "margin-right": "auto"})
            ],
            className="home",
        )   
    elif pathname.endswith("/success"):
        if current_user.is_authenticated:
            view = success()
        else:
            view = failed()
    elif pathname.endswith("/logout"):
        view = logout()
    elif pathname.endswith("/trends"):
        if current_user.is_authenticated:
            view = trends_layout()
        else:
            view = login()
    elif pathname.endswith("/symptoms"):
        if current_user.is_authenticated:
            view = trends_layout_detail()
        else:
            view = login()
    elif pathname.endswith("/rating"):
        if current_user.is_authenticated:
            view = raiting_layout()
        else:
            view = login()
    else:
        return "ERROR 404: Page not found!", url
    return view, url


def index():
    return html.Div([nav, container,
                     dcc.Location(id='redirect', refresh=True),
                     dcc.Store(id='login-status', storage_type='session')
                     ])


app.layout = index()


if __name__ == '__main__':
    app.run_server(host='localhost', port=8050, debug=True)
