import os

import dash_bootstrap_components as dbc

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
            dbc.NavItem(dbc.NavLink("Рейтинг симптомокомплексов",
                        href=f"{app_name}/rating")),
        ],
        brand="Главная",
        brand_href="/",
        sticky="top",
        color="black",
        dark=True,
        expand="lg",
    )
    return navbar
