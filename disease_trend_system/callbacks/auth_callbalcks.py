from typing import Tuple

import dash_core_components as dcc
from dash_extensions.enrich import Input, Output, State, no_update
from flask import session
from flask_login import current_user, login_user

from disease_trend_system.app import User, app


@app.callback(
    Output('url_login', 'pathname'),
    Output('output-state', 'children'),
    Output('login-status', 'data'),
    [Input('login-button', 'n_clicks')],
    [State('uname-box', 'value'), State('pwd-box', 'value')])
def login_button_click(n_clicks: int, username: str, password: str) -> Tuple:
    """Аутентификация через АД

    Args:
        n_clicks (int): Нажатие на кнопку Login
        username (str): Имя пользователя
        password (str): Пароль пользователя

    Returns:
        Tuple: Кортеж элементов
    """

    OUS = ["OU=Фед. служба управленческого учета", "OU=Фед. IT подразделения"]

    if (username is None) or (password is None):
        return no_update, "Please enter login/password", "loggedout"

    if n_clicks > 0:

        try:

            if conn.result['result'] == 0:
                conn.search(search_base='DC=partner,DC=ru',
                            search_filter=f'(sAMAccountName={username})', search_scope=SUBTREE)
                entry = conn.entries[0]
                entry_dn = entry.entry_dn
                attrs = entry_dn.split(',')
                if len(set(OUS) & set(attrs)) != 0:
                    user = User(username)
                    login_user(user)
                    session['username'] = current_user.get_id()
                    return '/success', '', current_user.get_id()
                else:
                    return no_update, "Your user does not have access to this system"
            elif conn.result['result'] == 49:
                return no_update, "Incorrect username or password!", "loggedout"
        except Exception as _:
            return no_update, "Incorrected username or password!", "loggedout"
        finally:
            if conn.bound:
                conn.unbind()


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
        return dcc.Link('logout', href='/logout'), current_user.get_id(), current_user.get_id()
    else:
        return dcc.Link('login', href='/login'), 'loggedout', ""
