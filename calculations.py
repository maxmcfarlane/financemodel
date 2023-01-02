"""Calculations script

Example calculation:

# calculate yearly paid salary i.e. gross pay - (income tax + national insurance)
paid_salary = calculate_paid_salary(annual_salary, bands_order, INCOME_TAX_BANDS, NAT_INS_THRESH, NAT_INS_RATE)

# Calculate the monthly salary contribution
monthly_salary_contribution = paid_salary / PERIODS
"""
import pandas as pd
import numpy as np
import datetime


def calculate_income_tax(annual_salary, bands_order, bands):
    tax_paid = []
    paid_salary = []
    lower_band = 0
    for band in bands_order:
        taxed_salary = max([min([band * 1e3, annual_salary]) - lower_band * 1e3, 0])
        tax_paid_ = taxed_salary * bands[band]
        tax_paid.append(tax_paid_)
        paid_salary_ = taxed_salary - tax_paid_
        paid_salary.append(paid_salary_)
        lower_band = band

    return sum(tax_paid)


def calculate_yearly_series(yearly_series: pd.Series,
                            increase_inflation: float = 0,
                            periodic_increase_years: int = 1,
                            periodic_increase_amount: float = 0,
                            periodic_decrease_years: int = 1,
                            periodic_decrease_amount: float = 0,
                            max_amount: float = 9 * 1e9,
                            inflate_max_amount=True  # increase max amount to Future Value
                            ):
    """

    :param yearly_series:
    :param increase_inflation:
    :param periodic_increase_years:
    :param periodic_increase_amount:
    :param periodic_decrease_years:
    :param periodic_decrease_amount:
    :param max_amount:
    :param inflate_max_amount: True will inflate values to Future Value, assuming maximum value is set as NPV
    :return:
    """


    yearly_series = yearly_series.copy()
    if inflate_max_amount:
        max_amount_ = calculate_compound_savings(pd.Series([max_amount] * len(yearly_series), name='max_amount'), 0,
                                                 increase_inflation, 1)
        max_amount_['max_amount'] = max_amount_['max_amount'] + max_amount_['interest']
        max_amount_ = max_amount_['max_amount']
    else:
        max_amount_ = pd.Series([max_amount] * len(yearly_series), name='max_amount')

    for y in yearly_series.items():
        if y[0] == 0:
            continue

        neg = y[1] < 0

        increase = increase_inflation
        if y[0] % periodic_increase_years == 0:
            increase += periodic_increase_amount
        if y[0] % periodic_decrease_years == 0:
            increase += periodic_decrease_amount

        yearly_series.iloc[y[0]] = min([yearly_series.iloc[y[0] - 1] * (1 + increase) * (-1 if neg else 1),
                                        max_amount_[y[0]] * (-1 if neg else 1)]) * (-1 if neg else 1)
    return yearly_series


def calculate_paid_yearly_salary(yearly_salary,
                                 bands_order,
                                 INCOME_TAX_BANDS,
                                 NAT_INS_THRESH,
                                 NAT_INS_RATE,
                                 ):
    records = yearly_salary.apply(
        lambda annual_salary_: _calculate_paid_salary(annual_salary_, bands_order, INCOME_TAX_BANDS, NAT_INS_THRESH,
                                                      NAT_INS_RATE))

    return pd.DataFrame.from_records(records)


def expand_yearly_to_monthly(values, name,
                             years,
                             start_
                             ):
    monthly = pd.Series(np.repeat(values, (12)),
                                      name=name,
                                      index=pd.date_range(start_,
                                                          start_
                                                          + pd.offsets.DateOffset(years=years),
                                                          freq='m'))
    return monthly


def calculate_compound_savings(monthly_savings: pd.Series,
                               initial_savings,
                               interest_rate: float,
                               compounding_periods):
    # todo - account for variable interest rates
    # todo - fix compound in first period
    name_ = monthly_savings.name
    data_monthly = monthly_savings.reset_index().iloc[:, 1:].copy()
    data_monthly['total_contribution'] = monthly_savings.cumsum().round(2)
    data_monthly['total'] = data_monthly['total_contribution'] + initial_savings
    data_monthly['interest'] = data_monthly['total'].apply(lambda v: interest_after_t_years(v, interest_rate, compounding_periods, 1 / compounding_periods))
    for idr, r in data_monthly.iterrows():
        if idr == 0:
            continue
        previous_month_end_balance = data_monthly.iloc[idr - 1, :]['total']
        previous_month_end_balance_with_interest = after_t_years(previous_month_end_balance, interest_rate, compounding_periods, 1 / compounding_periods)
        interest = previous_month_end_balance_with_interest - previous_month_end_balance
        data_monthly.iloc[idr - 1, data_monthly.columns.get_loc('total')] = previous_month_end_balance_with_interest
        data_monthly.iloc[idr, data_monthly.columns.get_loc('total')] = previous_month_end_balance_with_interest + \
                                                                        r[name_]
        data_monthly.iloc[idr, data_monthly.columns.get_loc('interest')] = interest
    return data_monthly


def calculate_national_insurance(national_insurance_band, annual_salary, national_insurance_rate):
    nat_ins_free = national_insurance_band * 52
    nat_ins_taxed = annual_salary - nat_ins_free
    nat_ins_paid = national_insurance_rate * nat_ins_taxed
    return nat_ins_paid


def _calculate_paid_salary(annual_salary, bands_order, bands,
                           national_insurance_band, national_insurance_rate):
    income_tax_paid = calculate_income_tax(annual_salary, bands_order, bands)

    nat_ins_paid = calculate_national_insurance(national_insurance_band, annual_salary, national_insurance_rate)

    tax_paid = income_tax_paid + nat_ins_paid

    paid_salary_yearly = annual_salary - tax_paid

    return {'net_salary_yearly':paid_salary_yearly, 'income_tax_paid_yearly':income_tax_paid, 'nat_ins_paid_yearly':nat_ins_paid}


def after_t_years(initial_investment, interest_rate, periods, years):
    return initial_investment * (pow((1 + interest_rate / periods), periods * years))


def interest_after_t_years(initial_investment, interest_rate, periods, years):
    return initial_investment * (pow((interest_rate / periods), periods * years))
