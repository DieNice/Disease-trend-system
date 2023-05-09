from typing import Tuple

import dash_core_components as dcc
from dash_extensions.enrich import Input, Output, State, no_update
from flask import session
from flask_login import current_user, login_user, logout_user

from disease_trend_system.app import User, app, create_session


@app.callback(
    Output('url_login', 'pathname'),
    Output('output-state', 'children'),
    Output('login-status', 'data'),
    [Input('login-button', 'n_clicks')],
    [State('uname-box', 'value'), State('pwd-box', 'value')])
def login_button_click(n_clicks: int, username: str, password: str) -> Tuple:
    """Аутентификация

    Args:
        n_clicks (int): Нажатие на кнопку Login
        username (str): Имя пользователя
        password (str): Пароль пользователя

    Returns:
        Tuple: Кортеж элементов
    """
    if (username is None) or (password is None):
        return no_update, "Please enter login/password", "loggedout"

    if n_clicks > 0:
        try:
            sql_session = create_session()
            with sql_session:
                user = sql_session.query(User).filter(
                    User.username == username).first()

            if user is None:
                return no_update, "Incorrect username or password!", "loggedout"
            if user.check_password(password):
                login_user(user)
                session['username'] = current_user.get_id()
                return '/success', '', current_user.get_id()
            else:
                return no_update, "Incorrect username or password!", "loggedout"
        except Exception as _:
            return no_update, "Incorrected username or password!", "loggedout"


@app.callback(Output('user-status-div', 'children'),
              Output('login-status', 'data'),
              Output('username-div', 'children'),
              [Input('url', 'pathname')])
def login_status(url: str) -> Tuple:
    """Колбэк для отображения состояния входа login/loggouted
    в заголовке

    Args:
        url (str): Адрес строки

    Returns:
        Tuple: Кортеж элементов
    """
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated \
            and url != '/logout':
        return dcc.Link('logout', href='/logout'), current_user.username, current_user.username
    else:
        logout_user()
        return dcc.Link('login', href='/login'), 'loggedout', ""
