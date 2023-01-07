import math

import numpy as np
import pandas as pd

from calculations import expand_yearly, calculate_yearly_series, calculate_compound_savings, condition_transaction_date


def get_compounding_exp_cases(cases,
                              interest_rate,
                              COMPOUNDING_PERIODS,
                              ):
    # todo - implement series factor i.e. proportion of savings will likely increase with increase in overall salary
    periodic_data = pd.DataFrame()
    for case in cases:
        name = case.get('name', None)
        source = case.get('source', None)
        diff = case.get('diff', None) if case.get('diff', None) is not None else 0
        factor = case.get('factor', None) if case.get('factor', None) is not None else 0
        initial = case.get('initial', None) if case.get('initial', None) is not None else 0
        interest = case.get('interest', interest_rate)
        interest = interest_rate if isinstance(interest, bool) and interest \
            else interest if interest else 0

        periodic_data[name] = source * factor

        if diff is not None:
            periodic_data[name] = periodic_data[name] - diff

        total = calculate_compound_savings(periodic_data[name], initial, interest, COMPOUNDING_PERIODS)
        periodic_data[f'{name}_interest'] = total['interest']
        periodic_data[f'{name}_total'] = total['total']
        periodic_data[name] = -total[name]

    return periodic_data


def combine_aggregate_savings_loans(periodic_compounding_exp: pd.DataFrame, target_amount: dict):
    periodic_compounding_exp_ = periodic_compounding_exp.copy()

    aggregate_targets = list(filter(lambda t: '+' in t, target_amount.keys()))

    for aggregate_target in aggregate_targets:
        targets = aggregate_target.split('+')
        periodic_compounding_exp_[aggregate_target] = periodic_compounding_exp_[targets].sum(axis=1)
        periodic_compounding_exp_[aggregate_target + '_total'] = periodic_compounding_exp_[
            map(lambda c: c + '_total', targets)].sum(axis=1)
        periodic_compounding_exp_[aggregate_target + '_interest'] = periodic_compounding_exp_[
            map(lambda c: c + '_interest', targets)].sum(axis=1)

    return periodic_compounding_exp_


def get_compounding_exp(
        periodic_salary_tax,
        source,
        cost_factors,
        interest,
        initial_balances,
        names,
        interest_rate,
        COMPOUNDING_PERIODS,
        target_amount,
):
    # calculate savings and loan amounts through time
    periodic_compounding_exp = get_compounding_exp_cases(
        [
            dict(
                name=name,
                source=periodic_salary_tax[source[name]],
                factor=cost_factors[name],
                interest=interest[name],
                initial=initial_balances[name]
            )
            for name in names
        ],
        interest_rate,
        COMPOUNDING_PERIODS,
    )

    # aggregate savings/loans, defined by savings_loans.target_amount
    periodic_compounding_exp = combine_aggregate_savings_loans(periodic_compounding_exp, target_amount)

    return periodic_compounding_exp


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
        varinc_prev_business_day,
        varex_varin_increase_inflation,
        varex_max,
        varex_end,
        varinc_end,
        varinc_inflation,
        varinc_in,
        from_date,
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
    :param from_date:
    :return:
    """
    # if datetime_index is None:
    #     months = months_until_retirement
    # else:
    #     months = len(datetime_index)
    #
    # years = math.ceil(months/12)

    yearly_varex = pd.DataFrame({k: pd.Series(np.repeat([v], math.ceil(years)))
                                 for k, v in varex.items()
                                 if not isinstance(v, list)})
    yearly_varinc = pd.DataFrame({k: pd.Series(np.repeat([v], math.ceil(years)))
                                  for k, v in varinc.items()
                                  if not isinstance(v, list)})

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
            from_date,
            granularity=granularity,
            freq=freq
        )
        if varex_end.get(idc, None) is not None:
            periodic.loc[varex_end.get(idc, None):] = 0
        periodic_varex.append(periodic)

    periodic_varex = pd.concat(periodic_varex, axis=1).iloc[:volume, :]

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
            from_date,
            granularity=granularity,
            freq=freq
        )
        if varinc_end.get(idc, None) is not None:
            periodic.loc[varinc_end.get(idc):] = 0
        periodic_varinc.append(periodic)

    periodic_varinc = pd.concat(periodic_varinc, axis=1).iloc[:volume, :]

    periodic_varinc_ = periodic_varinc.copy()
    periodic_varinc = condition_transaction_date(periodic_varinc, varinc_in,
                                                 prev_business_day=varinc_prev_business_day)

    periodic_varinc.index.names = ['date/time']
    periodic_varex.index.names = ['date/time']

    return periodic_varinc, periodic_varex
