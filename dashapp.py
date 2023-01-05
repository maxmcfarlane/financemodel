import dash.dependencies

import main
from plot import *
import config as cfg
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

    daily, monthly, _, _, _, \
    periodic_salary_tax_data_monthly, _, _ = main.generate_table_data()

    pension_fig = generate_pension_fig(periodic_salary_tax_data_monthly, cfg.savings_goal)
    balance_fig = generate_balance_fig(daily, monthly, cfg.balance)

    app.layout = html.Div([
        # Add the plotly figure

        dbc.Row([
            dbc.Col([
                dcc.Graph(figure=pension_fig,
                          id='pension_fig',
                          style={'height': f'{int(graph_height)}vh', 'width': '100%'}),
            ]),
            dbc.Col([
                dcc.Graph(figure=balance_fig,
                          id='balance_fig',
                          style={'height': f'{int(graph_height)}vh', 'width': '100%'}),
            ])
        ]),
        dbc.Container([
            dbc.Row([
                dbc.Col([

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
                ], xs=12, sm=12, md=12, lg=6, xl=6, xxl=6, style={'padding-top': f'{settings_pad}vh'}),
                dbc.Col([
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
                                                dcc.Slider(id='savings_factor-slider',
                                                           min=0,
                                                           max=max(list(percentage_savings_rate_marks.keys())),
                                                           step=0.001,
                                                           value=cfg.savings_factor,
                                                           marks=percentage_savings_rate_marks,
                                                           className='slider',
                                                           tooltip=tooltip_marks('savings_factor')),
                                            ),
                                            'savings_factor',
                                        )
                                    ])
                                ], xs=12, sm=12, md=12, lg=12, xl=12, xxl=12),
                            ]),

                        ]),
                        dbc.CardHeader(),
                    ]),
                ], xs=12, sm=12, md=12, lg=6, xl=6, xxl=6, style={'padding-top': f'{settings_pad}vh'})
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5('Setting [units]:'),
                        ]),
                        dbc.Tooltip('This feature has not been implemented yet.', target='centre-column'),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Row([
                                        dbc.Col(
                                            dcc.Input(id='setting1-input',
                                                      type='text',
                                                      disabled=True,
                                                      value=f'',
                                                      placeholder='',
                                                      debounce=True,
                                                      style={'width': '100%'}),
                                            width=12,
                                        ),
                                    ], justify='center'),
                                ], width=12, id='centre-column'),
                            ]),

                        ]),
                        dbc.CardHeader(),
                    ]),
                ], xs=12, sm=12, md=12, lg=6, xl=6, xxl=6, style={'padding-top': f'{settings_pad}vh'}),
                dbc.Col([
                    dbc.Tooltip('This feature has not been implemented yet.', target='target-card'),
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5('Setting [units]:'),
                        ]),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Row([
                                        dbc.Col(
                                            dcc.Input(id='setting2-input',
                                                      type='text',
                                                      value=f'',
                                                      placeholder='',
                                                      debounce=True,
                                                      disabled=True,
                                                      style={'width': '100%'}),
                                            width=12,
                                        ),
                                    ], justify='center'),
                                ], width=12),
                            ]),

                        ]),
                        dbc.CardHeader(),
                    ], id='setting2-input-card'),
                ], xs=12, sm=12, md=12, lg=6, xl=6, xxl=6, style={'padding-top': f'{settings_pad}vh'}),
            ])
        ], style={'height': f'{100 - int(graph_height) - int(2 * settings_pad)}vh', 'width': '100%',
                  'padding-top': f'{settings_pad}vh'})
    ], style={'height': '100vh', 'width': '100%'}
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

            dash.dependencies.Input('savings_factor-slider', 'value'),

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
            savings_factor,
            pension_fig,
            balance_fig,
            interest_sliders):
        # Get the current figure
        # Update the figure's opacity

        assume_inflation = 'interest' in assume_inflation
        if dash.callback_context.triggered_id == 'inflation-slider' or \
                        dash.callback_context.triggered_id == 'promotion_frequency_years-slider' or \
                        dash.callback_context.triggered_id == 'savings_factor-slider' or \
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
            cfg.set_savings_factor(savings_factor)

            daily, monthly, _, _, _, \
            periodic_salary_tax_data_monthly, _, _ = main.generate_table_data()

            balance_fig = generate_balance_fig(daily, monthly, cfg.balance)
            pension_fig = generate_pension_fig(periodic_salary_tax_data_monthly, cfg.savings_goal)
        elif dash.callback_context.triggered_id == 'inflation-checkbox':
            cfg.set_inflation_rate(inflation_rate_,
                                   interest_rate_,
                                   salary_increase_inflation_,
                                   varex_varin_increase_inflation_, assume_inflation)
            interest_sliders = create_interest_sliders(assume_inflation)
            if assume_inflation:
                daily, monthly, _, _, _, \
                periodic_salary_tax_data_monthly, _, _ = main.generate_table_data()
                pension_fig = generate_pension_fig(periodic_salary_tax_data_monthly, cfg.savings_goal)

        return [pension_fig, balance_fig, inflation_rate_, interest_sliders]

    return app.server
