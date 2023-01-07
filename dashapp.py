import os
import pickle
import datetime

import dash.dependencies
import dash_bootstrap_components as dbc
import dash_table
import pandas as pd
from dash import dcc
from dash import html

import config as cfg
import main
import plot
import savings_loans as snl
import ui_config as uicfg

external_stylesheets = [dbc.themes.BOOTSTRAP]


def left_label(comp, name, style=None):
    return dbc.Row([
        dbc.Col([
            html.H6(name)
        ], xs=5, sm=5, md=5, lg=5, xl=5, xxl=5),
        dbc.Col([
            comp
        ], xs=7, sm=7, md=7, lg=7, xl=7, xxl=7)
    ], style=style)


percentage_interest_rate_marks = {i / 100: f'{i}' for i in range(0, 12, 1)}
percentage_savings_rate_marks = {i / 100: f'{i}' for i in range(0, 20, 1)}
integer_marks = {i: f'{i}' for i in range(0, 12, 1)}
tooltip_marks = lambda id_: {'always_visible': False}


def create_interest_sliders(assume_inflation):
    return [
        left_label(
            dbc.Spinner(
                dcc.Slider(id='inflation-slider',
                           min=0,
                           max=0.1,
                           step=0.001,
                           value=cfg.inflation_rate,
                           marks=percentage_interest_rate_marks,
                           className='slider',
                           tooltip=tooltip_marks('inflation_rate')),
            ),
            'inflation_rate',
        ),
        left_label(
            dbc.Spinner(
                dcc.Slider(id='interest_rate-slider',
                           min=0,
                           max=0.1,
                           step=0.001,
                           value=cfg.interest_rate,
                           marks=percentage_interest_rate_marks,
                           className='slider',
                           tooltip=tooltip_marks('interest_rate')),
            ),
            'interest_rate',
            style={'display': 'none'} if assume_inflation else None
        ),
        left_label(
            dbc.Spinner(
                dcc.Slider(id='promotion_frequency_years-slider',
                           min=0,
                           max=max([cfg.promotion_frequency_years, 10]),
                           step=1,
                           value=cfg.promotion_frequency_years,
                           marks=integer_marks,
                           className='slider',
                           tooltip=tooltip_marks('promotion_frequency_years')),
            ),
            'promotion_frequency_years',
        ),
        left_label(
            dbc.Spinner(
                dcc.Slider(id='salary_increase_inflation-slider',
                           min=0,
                           max=0.1,
                           step=0.001,
                           value=cfg.salary_increase_inflation,
                           marks=percentage_interest_rate_marks,
                           className='slider',
                           tooltip=tooltip_marks('salary_increase_inflation')),
            ),
            'salary_increase_inflation',
            style={'display': 'none'} if assume_inflation else None
        ),
        left_label(
            dbc.Spinner(
                dcc.Slider(id='varex_varin_increase_inflation-slider',
                           min=0,
                           max=0.1,
                           step=0.001,
                           value=cfg.varex_varin_increase_inflation,
                           marks=percentage_interest_rate_marks,
                           className='slider',
                           tooltip=tooltip_marks('varex_varin_increase_inflation')),
            ),
            'varex_varin_increase_inflation',
            style={'display': 'none'} if assume_inflation else None
        ),
    ]


def setting_(id, label='Setting [units]:', disabled=False) -> list:
    settings_comp = [
        dbc.Container(dbc.Tooltip('This feature has not been implemented yet.', target=f'{id}-input-card'))
    ] if disabled else []

    settings_comp.append(
        dbc.Container([
            dbc.Card([
                dbc.CardHeader([
                    html.H5(label),
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Row([
                                dbc.Col(
                                    dcc.Input(id=f'{id}-input',
                                              type='text',
                                              value=f'',
                                              placeholder='',
                                              debounce=True,
                                              disabled=disabled,
                                              style={'width': '100%'}),
                                    width=12,
                                ),
                            ], justify='center'),
                        ], width=12),
                    ]),

                ]),
                dbc.CardHeader(),
            ], id=f'{id}-input-card')
        ])
    )
    return settings_comp


def datetime_picker_setting_(id, label='Setting [units]:', disabled=False) -> list:
    settings_comp = [
        dbc.Container(dbc.Tooltip('This feature has not been implemented yet.', target=f'{id}-input-card'))
    ] if disabled else []

    settings_comp.append(
        dbc.Container([
            dbc.Card([
                dbc.CardHeader([
                    html.H5(label),
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Row([
                                dbc.Col(
                                    dcc.DatePickerRange(
                                        id=id,
                                        display_format="DD/MM/YY",
                                        min_date_allowed=cfg.birthday,
                                        max_date_allowed=cfg.retirement_date,
                                        # initial_visible_month=cfg.to_date,
                                        start_date=cfg.from_date,
                                        end_date=cfg.to_date
                                    ),
                                    width=12,
                                ),
                            ], justify='center'),
                        ], width=12),
                    ]),

                ]),
                dbc.CardHeader(),
            ], id=f'{id}-input-card')
        ])
    )
    return settings_comp


def col_(children, width=6):
    return dbc.Col(children=children, xs=12, sm=12, md=12, lg=width, xl=width, xxl=width, style={'padding-top': f'1vh'})


def full_col_(children):
    width = 12
    return col_(children, width=width)


def half_col_(children):
    width = 6
    return col_(children, width=width)


def row_(children):
    return dbc.Row(children=children,
                   style={'height': f'auto', 'width': '100%', 'padding-top': '1vh',
                          # 'display': 'block',
                          # 'margin-left': 'auto',
                          # 'margin-right': 'auto',
                          })


def create_app(server_):
    app = dash.Dash(__name__,
                    title='name',
                    meta_tags=[{'name': 'viewport',
                                'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'}],
                    external_stylesheets=external_stylesheets, server=server_)

    # Define the layout of the app
    graph_height = 60
    settings_pad = 2

    DIR = os.path.dirname(__file__)

    if not os.path.exists('./cache.p'):
        periodic_salary_tax_saving_loan_data, periodic_salary_tax_data_monthly, years = main.generate_table_data()

        daily, monthly, _, _, _, _, _, _ = \
            main.generate_with_varinvex(periodic_salary_tax_saving_loan_data, years)

        pension_fig = plot.generate_pension_fig(periodic_salary_tax_data_monthly, cfg.pension_goal)
        balance_fig = plot.generate_balance_fig(daily, monthly, cfg.balance,
                                                cfg.from_date,
                                                cfg.to_date)
        loan_fig, _ = plot.generate_loan_figs(periodic_salary_tax_saving_loan_data[snl.get_loans()],
                                              periodic_salary_tax_saving_loan_data[snl.get_loan_totals()])
        savings_fig, _ = plot.generate_savings_figs(periodic_salary_tax_saving_loan_data[snl.get_savings()],
                                                    periodic_salary_tax_saving_loan_data[snl.get_savings_totals()])

        pickle.dump((
            pension_fig,
            daily, monthly,
            periodic_salary_tax_data_monthly,
            balance_fig,
            loan_fig,
            savings_fig,
        ), open('./cache.p', 'wb'))
    else:
        (
            pension_fig,
            daily, monthly,
            periodic_salary_tax_data_monthly,
            balance_fig,
            loan_fig,
            savings_fig,
        ) = pickle.load(open('./cache.p', 'rb'))

    app.layout = html.Div([
        # Add the plotly figure

        row_([
            col_(
                datetime_picker_setting_('date_range-picker', 'Date range', disabled=False),
                width=4
            ),
        ]),
        row_([
            half_col_([
                dbc.Spinner([
                    dcc.Graph(figure=pension_fig,
                              id='pension_fig',
                              style={'height': f'{int(graph_height)}vh', 'width': '100%'}),
                ])
            ]),
            half_col_([
                dbc.Spinner([
                    dcc.Graph(figure=balance_fig,
                              id='balance_fig',
                              style={'height': f'{int(graph_height)}vh', 'width': '100%'}),
                ])
            ])
        ]),
        row_([
            half_col_([
                dbc.Spinner([
                    dcc.Graph(figure=savings_fig,
                              id='savings_fig',
                              style={'height': f'{int(graph_height)}vh', 'width': '100%'}),
                ])
            ]),
            half_col_([
                dbc.Spinner([
                    dcc.Graph(figure=loan_fig,
                              id='loan_fig',
                              style={'height': f'{int(graph_height)}vh', 'width': '100%'}),
                ])
            ])
        ]),
        row_([
            half_col_([
                dbc.Container([
                    dbc.Card([
                        dbc.CardHeader([
                            dbc.Row([
                                dbc.Col([
                                    html.H5('Inflation rate [%]:'),
                                ], xs=5, sm=5, md=5, lg=5, xl=5, xxl=5),
                                dbc.Col([
                                    html.H5([
                                        dbc.Checklist(
                                            options=[
                                                {'label': 'Interest/salary = inflation', 'value': 'interest'}
                                            ],
                                            id='inflation-checkbox',
                                            value=['interest'] if uicfg.ASSUME_INFLATION else []
                                        )
                                    ])
                                ], xs=7, sm=7, md=7, lg=7, xl=7, xxl=7),
                            ]),
                        ]),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Div(create_interest_sliders(uicfg.ASSUME_INFLATION), id='interest-sliders')
                                ], xs=12, sm=12, md=12, lg=12, xl=12, xxl=12),
                            ]),

                        ]),
                        dbc.CardHeader(),
                    ]),
                ])
            ]),
            half_col_([
                dbc.Container([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5('Savings [%]:'),
                        ]),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        left_label(
                                            dbc.Spinner(
                                                dcc.Slider(id='house_savings_factor-slider',
                                                           min=0,
                                                           max=max(list(percentage_savings_rate_marks.keys())),
                                                           step=0.001,
                                                           value=snl.cost_factors['house_savings'],
                                                           marks=percentage_savings_rate_marks,
                                                           className='slider',
                                                           tooltip=tooltip_marks('house_savings')),
                                            ),
                                            'house_savings',
                                        )
                                    ])
                                ], xs=12, sm=12, md=12, lg=12, xl=12, xxl=12),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        left_label(
                                            dbc.Spinner(
                                                dcc.Slider(id='personal_pension_savings_factor-slider',
                                                           min=0,
                                                           max=max(list(percentage_savings_rate_marks.keys())),
                                                           step=0.001,
                                                           value=snl.cost_factors['personal_pension_savings'],
                                                           marks=percentage_savings_rate_marks,
                                                           className='slider',
                                                           tooltip=tooltip_marks('personal_pension_savings')),
                                            ),
                                            'personal_pension_savings',
                                        )
                                    ])
                                ], xs=12, sm=12, md=12, lg=12, xl=12, xxl=12),
                            ]),

                        ]),
                        dbc.CardHeader(),
                    ]),
                ])
            ])
        ]),

        row_([
            half_col_(
                setting_('settings1', disabled=True)
            ),
            half_col_(
                setting_('settings2', disabled=True)
            )
        ]),
        row_([
            full_col_([
                dbc.Container([
                    dbc.Card([
                        dbc.CardHeader([

                        ]),
                        dbc.CardBody([
                            dash_table.DataTable(
                                id='table',
                                columns=[{"name": i, "id": i} for i in daily.reset_index().columns],
                                data=daily.iloc[:365, :].reset_index().to_dict('records'),
                                # style_table={
                                #     'maxHeight': '75vh',
                                #     'maxWidth': '75vw',
                                #     'overflowY': 'scroll'
                                # }
                            )
                        ], style={
                            'height': '100%',
                            # 'marginLeft': 'auto', 'marginRight': 'auto',
                            # 'margin': '0px',
                            'width': '100%',
                            'overflowY': 'scroll'
                        }),
                        # dbc.Table.from_dataframe(daily.iloc[:365, :].reset_index())
                    ], style={
                        'height': '75vh',
                        # 'marginLeft': 'auto', 'marginRight': 'auto',
                        'width': '100%',
                        # 'margin': '0px',
                    },
                        id='table_card')
                ])
            ]),
        ]),
        # dbc.Row([
        #     dbc.Col([
        #
        #     ], style={
        #                 # 'height': '75vh',
        #                 # 'marginLeft': 'auto', 'marginRight': 'auto',
        #                 'width': '75vw',
        #                 # 'margin': '0px',
        #             })
        # ],
        #     style={
        #         'display': 'block',
        #         'margin-left': 'auto',
        #         'margin-right': 'auto',
        #         'width': '40%',
        #     },
        #     justify="center"),

    ], style={'height': '100vh', 'width': '98vw'}
    )

    # Define a callback function to update the figure's opacity when the slider value changes
    @app.callback(
        [
            dash.dependencies.Output('pension_fig', 'figure'),
            dash.dependencies.Output('balance_fig', 'figure'),
            dash.dependencies.Output('inflation-slider', 'value'),
            dash.dependencies.Output('interest-sliders', 'children'),
        ],
        [
            dash.dependencies.Input('inflation-slider', 'value'),
            dash.dependencies.Input('promotion_frequency_years-slider', 'value'),
            dash.dependencies.Input('interest_rate-slider', 'value'),
            dash.dependencies.Input('salary_increase_inflation-slider', 'value'),
            dash.dependencies.Input('varex_varin_increase_inflation-slider', 'value'),
            dash.dependencies.Input('inflation-checkbox', 'value'),

            dash.dependencies.Input('house_savings_factor-slider', 'value'),
            dash.dependencies.Input('personal_pension_savings_factor-slider', 'value'),
            dash.dependencies.Input('date_range-picker', 'start_date'),
            dash.dependencies.Input('date_range-picker', 'end_date'),

        ],
        [
            dash.dependencies.State('pension_fig', 'figure'),
            dash.dependencies.State('balance_fig', 'figure'),
            dash.dependencies.State('interest-sliders', 'children'),
        ],
        prevent_initial_callbacks=True
    )
    def update_figure(
            inflation_rate_,
            promotion_frequency_years_,
            interest_rate_,
            salary_increase_inflation_,
            varex_varin_increase_inflation_,
            assume_inflation,
            house_savings_factor,
            personal_pension_savings_factor,
            from_date_,
            to_date_,
            pension_fig,
            balance_fig,
            interest_sliders):
        # Get the current figure
        # Update the figure's opacity

        assume_inflation = 'interest' in assume_inflation
        if dash.callback_context.triggered_id == 'inflation-slider' or \
                dash.callback_context.triggered_id == 'promotion_frequency_years-slider' or \
                dash.callback_context.triggered_id == 'house_savings_factor-slider' or \
                dash.callback_context.triggered_id == 'personal_pension_savings_factor-slider' or \
                dash.callback_context.triggered_id == 'date_range-picker' or \
                (dash.callback_context.triggered_id == 'interest_rate-slider' and not assume_inflation) or \
                (
                        dash.callback_context.triggered_id == 'salary_increase_inflation-slider' and not assume_inflation) or \
                (
                        dash.callback_context.triggered_id == 'varex_varin_increase_inflation-slider' and not assume_inflation):

            cfg.set_inflation_rate(inflation_rate_,
                                   interest_rate_,
                                   salary_increase_inflation_,
                                   varex_varin_increase_inflation_, assume_inflation)
            cfg.set_promotion_rate(promotion_frequency_years_)
            cfg.set_from_date(pd.to_datetime(from_date_))
            cfg.set_to_date(pd.to_datetime(to_date_))
            snl.set_cost_factor('house_savings_factor-slider', house_savings_factor)
            snl.set_cost_factor('personal_pension_savings_factor-slider', personal_pension_savings_factor)

            periodic_salary_tax_saving_loan_data, periodic_salary_tax_data_monthly, years = main.generate_table_data()

            daily, monthly, _, _, _, _, _, _ = \
                main.generate_with_varinvex(periodic_salary_tax_saving_loan_data, years)

            balance_fig = plot.generate_balance_fig(daily, monthly, cfg.balance,
                                                    cfg.from_date,
                                                    cfg.to_date)
            pension_fig = plot.generate_pension_fig(periodic_salary_tax_data_monthly, cfg.pension_goal)
        elif dash.callback_context.triggered_id == 'inflation-checkbox':
            cfg.set_inflation_rate(inflation_rate_,
                                   interest_rate_,
                                   salary_increase_inflation_,
                                   varex_varin_increase_inflation_, assume_inflation)
            interest_sliders = create_interest_sliders(assume_inflation)
            if assume_inflation:
                periodic_salary_tax_saving_loan_data, periodic_salary_tax_data_monthly, years = main.generate_table_data()

                pension_fig = plot.generate_pension_fig(periodic_salary_tax_data_monthly, cfg.pension_goal)

        return [pension_fig, balance_fig, inflation_rate_, interest_sliders]

    return app.server
