import math

import numpy as np
import pandas as pd

from calculations import expand_yearly, calculate_yearly_series, calculate_compound_savings, condition_transaction_date


def get_compounding_exp(cases,
                        interest_rate,
                        COMPOUNDING_PERIODS,
                        ):
    # todo - implement series factor i.e. proportion of savings will likely increase with increase in overall salary
    periodic_data = pd.DataFrame()
    for case in cases:
        target = case.get('target', None)
        source = case.get('source', None)
        diff = case.get('diff', None)
        factor = case.get('factor', None)
        initial = case.get('initial', None)

        periodic_data[target] = source * factor
        if diff is not None:
            periodic_data[target] = periodic_data[target] - diff
        total = calculate_compound_savings(periodic_data[target], initial, interest_rate, COMPOUNDING_PERIODS)
        periodic_data[f'{target}_total'] = total['total']
        periodic_data[target] = -total[target]

    return periodic_data

    # data_monthly['personal_pension_savings'] = data_monthly['net_salary'] * save_factor
    # data_monthly['student_loan'] = data_monthly['net_salary'] * student_loan_factor
    # data_monthly['workplace_pension'] = data_monthly['gross_salary'] * workplace_pension_amount
    # data_monthly['workplace_pension_combined'] = data_monthly['gross_salary'] * (workplace_pension_amount \
    #                                                                        + employer_pension_contribution *
    #                                                                        (workplace_pension_amount / 0.035))
    #
    # # calculate total compound savings based on constant interest rate
    # for c, initial in [('personal_pension_savings', initial_personal_savings),
    #                    ('student_loan', initial_student_loan_paid),
    #                    ('workplace_pension', 0),
    #                    ('workplace_pension_combined', initial_workplace_pension),
    #                    ]:
    #     # todo - calculate amount remaining of loan (student loan)
    #     total = calculate_compound_savings(data_monthly[c], initial, interest_rate, COMPOUNDING_PERIODS)
    #     data_monthly[f'{c}_total'] = total['total']
    #     data_monthly[c] = -total[c]


def get_varexinc(
        volume,
        granularity,
        years,
        freq,
        varex,
        varinc,
        varex_inflation,
        varex_out,
        varex_next_business_day,
        varex_varin_increase_inflation,
        varex_max,
        varex_end,
        varinc_inflation,
        varinc_in,
        start_from,
):
    """

    :param varex: dict of monthly expenditure
    :param varinc: dict of monthly income
    :param varex_inflation: dict of booleans, forcing/preventing calculation of inflation
    :param varex_varin_increase_inflation:
    :param varex_max:
    :param varex_end:
    :param varinc_inflation:
    :param months_until_retirement:
    :param start_from:
    :return:
    """
    # if datetime_index is None:
    #     months = months_until_retirement
    # else:
    #     months = len(datetime_index)
    #
    # years = math.ceil(months/12)

    yearly_varex = pd.DataFrame({k: pd.Series(np.repeat([v], math.ceil(years))) for k, v in varex.items()})
    yearly_varinc = pd.DataFrame({k: pd.Series(np.repeat([v], math.ceil(years))) for k, v in varinc.items()})

    for idc, col in yearly_varex.iteritems():
        if varex_inflation.get(idc, True):
            yearly_col = calculate_yearly_series(col, varex_varin_increase_inflation,
                                                 max_amount=varex_max.get(idc, varex[idc]),
                                                 inflate_max_amount=True)
            yearly_varex[idc] = yearly_col

    periodic_varex = []
    for idc, col in yearly_varex.iteritems():
        periodic = expand_yearly(
            col.values, idc,
            volume,
            start_from,
            granularity=granularity,
            freq=freq
        )
        if varex_end.get(idc, None) is not None:
            periodic.loc[varex_end.get(idc, None):] = 0
        periodic_varex.append(periodic)

    periodic_varex = pd.concat(periodic_varex, axis=1).iloc[:volume, :]

    if freq == 'D':
        periodic_varex_ = periodic_varex.copy()
        periodic_varex = condition_transaction_date(periodic_varex, varex_out,
                                                    next_business_day=varex_next_business_day)

    for idc, col in yearly_varinc.iteritems():
        if varinc_inflation.get(idc, False):
            yearly_col = calculate_yearly_series(col, varex_varin_increase_inflation)
            yearly_varinc[idc] = yearly_col

    periodic_varinc = []
    for idc, col in yearly_varinc.iteritems():
        periodic = expand_yearly(
            col.values, idc,
            volume,
            start_from,
            granularity=granularity,
            freq=freq
        )
        periodic_varinc.append(periodic)

    periodic_varinc = pd.concat(periodic_varinc, axis=1).iloc[:volume, :]

    if freq == 'D':
        periodic_varinc_ = periodic_varinc.copy()
        periodic_varinc = condition_transaction_date(periodic_varinc, varinc_in)

    periodic_varinc.index.names = ['date/time']
    periodic_varex.index.names = ['date/time']

    return periodic_varinc, periodic_varex
