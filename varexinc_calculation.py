import numpy as np
import pandas as pd

from calculations import expand_yearly_to_monthly, calculate_yearly_series, calculate_compound_savings




def get_compounding_exp(cases,
                        interest_rate,
                        COMPOUNDING_PERIODS,
                        ):
    data_monthly = pd.DataFrame()
    for case in cases:
        target = case.get('target', None)
        source = case.get('source', None)
        factor = case.get('factor', None)
        initial = case.get('initial', None)

        data_monthly[target] = source * factor
        total = calculate_compound_savings(data_monthly[target], initial, interest_rate, COMPOUNDING_PERIODS)
        data_monthly[f'{target}_total'] = total['total']
        data_monthly[target] = -total[target]

    return data_monthly

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
        varex,
        varinc,
        varex_inflation,
        varex_varin_increase_inflation,
        varex_max,
        varex_end,
        varinc_inflation,
        years_until_retirement,
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
    :param years_until_retirement:
    :param start_from:
    :return:
    """
    yearly_varex = pd.DataFrame({k: pd.Series(np.repeat([v], years_until_retirement)) for k, v in varex.items()})
    yearly_varinc = pd.DataFrame({k: pd.Series(np.repeat([v], years_until_retirement)) for k, v in varinc.items()})

    for idc, col in yearly_varex.iteritems():
        if varex_inflation.get(idc, True):
            yearly_col = calculate_yearly_series(col, varex_varin_increase_inflation,
                                                 max_amount=varex_max.get(idc, varex[idc]),
                                                 inflate_max_amount=True)
            yearly_varex[idc] = yearly_col

    monthly_varex = []
    for idc, col in yearly_varex.iteritems():
        monthly = expand_yearly_to_monthly(col.values, idc,
                                           years_until_retirement,
                                           start_from)
        if varex_end.get(idc, None) is not None:
            monthly.loc[varex_end.get(idc, None):] = 0
        monthly_varex.append(monthly)

    monthly_varex = pd.concat(monthly_varex, axis=1)

    for idc, col in yearly_varinc.iteritems():
        if varinc_inflation.get(idc, False):
            yearly_col = calculate_yearly_series(col, varex_varin_increase_inflation)
            yearly_varinc[idc] = yearly_col

    monthly_varinc = []
    for idc, col in yearly_varinc.iteritems():
        monthly = expand_yearly_to_monthly(col.values, idc,
                                           years_until_retirement,
                                           start_from)
        monthly_varinc.append(monthly)

    monthly_varinc = pd.concat(monthly_varinc, axis=1)

    return monthly_varinc, monthly_varex
