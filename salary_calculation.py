import datetime
import math
import numpy as np
import pandas as pd

from calculations import calculate_paid_yearly_salary, expand_yearly, calculate_yearly_series, condition_transaction_date
import config as cfg

def get_salary_and_tax(volume: int,
                       granularity: int,
                       years: int,
                       freq,
                       annual_salary: int,
                       pay_day: int,
                       savings_loans_day: dict,
                       salary_increase_inflation: float,
                       promotion_frequency_years: int,
                       salary_increase_promotion: float,
                       role_change_frequency_years: int,
                       salary_decrease_role_change: float,
                       max_salary: int,
                       from_date: datetime,
                       bands_order: list,
                       INCOME_TAX_BANDS: dict,
                       NAT_INS_THRESH: int,
                       NAT_INS_RATE: float,
                       ) -> pd.DataFrame:
    """

    :param annual_salary:
    :param months_until_retirement:
    :param salary_increase_inflation:
    :param promotion_frequency_years:
    :param salary_increase_promotion:
    :param role_change_frequency_years:
    :param salary_decrease_role_change:
    :param max_salary:
    :param from_date:
    :param bands_order:
    :param INCOME_TAX_BANDS:
    :param NAT_INS_THRESH:
    :param NAT_INS_RATE:
    :param MONTH_PERIODS:
    :return:
    """


    # compile series of data - annual salary until retirement
    yearly_salary = pd.Series(np.repeat([annual_salary], math.ceil(years)))

    # account for inflation/salary increase, promotions, job changes and a max salary cap
    yearly_salary = calculate_yearly_series(yearly_salary,
                                            salary_increase_inflation,
                                            promotion_frequency_years,
                                            salary_increase_promotion,
                                            role_change_frequency_years,
                                            salary_decrease_role_change,
                                            max_salary)


    # compile income on periodic basis, until retirement
    salary = expand_yearly(yearly_salary.values, 'gross_salary_yearly',
                           volume,
                           from_date,
                           granularity=granularity,
                           freq=freq)

    # calculate paid salary based on national insurance and income tax deductions
    yearly_paid_salary = calculate_paid_yearly_salary(yearly_salary,
                                                      bands_order,
                                                      INCOME_TAX_BANDS,
                                                      NAT_INS_THRESH,
                                                      NAT_INS_RATE)

    periodic_salary_tax = []
    for idc, col in yearly_paid_salary.iteritems():
        periodic = expand_yearly(col.values, idc,
                                 volume,
                                 from_date,
                                 granularity=granularity,
                                 freq=freq)
        periodic_salary_tax.append(periodic)

    yearly_paid_salary_monthly = pd.concat(periodic_salary_tax, axis=1)

    periodic_data = pd.DataFrame(salary)

    # wrangle monthly salary, savings contributions and prepare data for calculation total savings
    periodic_data['income_tax_paid_yearly'] = -yearly_paid_salary_monthly['income_tax_paid_yearly'].values
    periodic_data['nat_ins_paid_yearly'] = -yearly_paid_salary_monthly['nat_ins_paid_yearly'].values
    periodic_data['net_salary_yearly'] = yearly_paid_salary_monthly['net_salary_yearly'].values

    salary_cols = cfg.SALARY_COLS + cfg.TAX_COLS

    for c in salary_cols:
        periodic_data[c] = periodic_data[f'{c}_yearly'] / 12

    if not freq == 'M':
        salary_cols = sum([list(map(lambda c: c + y, salary_cols)) for y in ['', '_yearly']], [])
        periodic_data = condition_transaction_date(periodic_data, {**savings_loans_day,
                                                   **{k: pay_day for k in salary_cols}})

    return periodic_data
