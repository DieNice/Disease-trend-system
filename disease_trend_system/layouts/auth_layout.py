
import dash_core_components as dcc
from dash_extensions.enrich import html


def login() -> html.Div:
    """View login
    """
    return html.Div([
    dcc.Location(id='url_login', refresh=True),
    html.Div([
        html.H2('''Введите данные для входа в систему''', id='h1'),
        dcc.Input(
            placeholder='Enter your username',
            type='text',
            id='uname-box',
            className='form-input'
        ),
        dcc.Input(
            placeholder='Enter your password',
            type='password',
            id='pwd-box',
            className='form-input'
        ),
        html.Button(
            children='Login',
            type='submit',
            id='login-button',
            className='form-button'
        ),
        html.Div(
            children='',
            id='output-state',
            className='form-output'
        )
    ], className='login-form')
])


def success() -> html.Div:
    """View success
    """
    return html.Div([html.Div([html.H2('Login successful.'),
                              html.Br(),
                              dcc.Link('Go Home', href='/')])
                     ], className="login-form")


def failed() -> html.Div:
    """View failed
    """
    return html.Div([html.Div([html.H2('Log in Failed. Please try again.'),
                               html.Br(),
                               dcc.Link('Login', href='/login')
                               ])
                     ], className="login-form")


def logout() -> html.Div:
    """View logout
    """
    return html.Div([html.Div(html.H2('You have been logged out - Please login')),
                     html.Br(),
                     dcc.Link('Login', href='/login')
                     ],
                    className="login-form")
