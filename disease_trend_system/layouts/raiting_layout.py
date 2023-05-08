
from datetime import datetime

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html
from dash.dash_table.Format import Format, Scheme

COLUMNS = [
    dict(id="symptom_complex_hash", name="ИД симмптомокомплекса"),
    dict(id="date", name="Максимальная продолжительность"),
    dict(id="percent_people", name="Процент людей",
         type="numeric",
         format=Format(precision=2, scheme=Scheme.percentage)),
    dict(id="total_number", name="Общее число людей", type="numeric",
         format=Format(precision=0, scheme=Scheme.fixed)),
    dict(id="extra", name="Описание симптомокомлекса")]

MAX_PAGE_SIZE = 50


def raiting_layout():
    return dbc.Container([
        dbc.Row(html.Br()),
        dbc.Row([
            dbc.Col([html.P("Выберите дату"),
                     dcc.DatePickerSingle(id="date-range-3", date=datetime.now())]),
            dbc.Col(),
            dbc.Col(),
            dbc.Col()
        ]),
        dbc.Row(html.Br()),

        dbc.Row([dash_table.DataTable(data=[], id="table-2",
                                      columns=COLUMNS,
                                      filter_action="native",
                                      sort_action="native",
                                      sort_mode="multi",
                                      page_action="native",
                                      page_current=0,
                                      page_size=MAX_PAGE_SIZE,
                                      style_table={
                                          'height': '70vh', 'overflowY': 'auto'},
                                      style_header={
            'backgroundColor': '#6A5ACD',
            'fontWeight': 'bold',
            'color': "white"
        },
            style_data={
            'color': 'black',
            'backgroundColor': 'white',
            'whiteSpace': 'normal'
        },
            style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(220, 220, 220)',
            }
        ])]),
        dbc.Row(className="justify-content-md-center"),
        dbc.Row(html.Br()),
        dbc.Row(html.Br()),
        dbc.Row(html.Br()),
        dbc.Row(html.Br()),
        dbc.Row(html.Br()),
    ])
