import os

import dash_bootstrap_components as dbc
from dash import html

app_name = os.getenv("DASH_APP_PATH", "/desease-knowlege-base-dash")


def Navbar():
    """Навигационная панель
    """
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Тренды симптомокомплексов",
                        href=f"{app_name}/trends")),
            dbc.NavItem(dbc.NavLink("Детализация симптомокомплексов",
                        href=f"{app_name}/symptoms")),
            dbc.NavItem(dbc.NavLink("Рейтинг симптомокомплексов за месяц",
                        href=f"{app_name}/rating")),
            dbc.NavItem([html.Div([
                html.Div(id='username-div', className="header-username"),
                html.Div(id='user-status-div', className="header-status")
            ],
                id="right-part-header-id"
            )])
        ],
        brand="Главная",
        brand_href="/",
        sticky="top",
        color="#6A5ACD",
        dark=True,
        expand="lg",
    )
    return navbar
