"""Calculations script

Example calculation:

# calculate yearly paid salary i.e. gross pay - (income tax + national insurance)
paid_salary = calculate_paid_salary(annual_salary, bands_order, INCOME_TAX_BANDS, NAT_INS_THRESH, NAT_INS_RATE)

# Calculate the monthly salary contribution
monthly_salary_contribution = paid_salary / PERIODS
"""
import pandas as pd
import numpy as np
import math
import holidays
import datetime

import calendar


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
        max_amount_ = pd.Series([fv(max_amount, increase_inflation, 12, y) for y in yearly_series.index],
                                name='max_amount')
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


def expand_yearly(values, name,
                  periods_until_retirement,
                  start_,
                  granularity,
                  freq
                  ):

    range_ = pd.date_range(start_,
                           start_
                           + pd.offsets.DateOffset(years=math.ceil(periods_until_retirement / granularity)),
                           inclusive='left',
                           freq=freq)

    if freq == 'D':
        granularity = [365 + (1 if calendar.isleap(y) else 0) for y in range_.to_series().dt.year.unique()[:-1]]

    periodic = pd.Series(np.repeat(values, (granularity)),
                                      name=name,
                                      index=range_)
    periodic = periodic.iloc[:periods_until_retirement]
    return periodic


def calculate_compound_savings(periodic_savings: pd.Series,
                               initial_savings,
                               interest_rate: float,
                               compounding_periods):
    # todo - account for variable interest rates
    # todo - fix compound in first period
    name_ = periodic_savings.name
    periodic_data = periodic_savings.reset_index(drop=False).set_index('index').copy()

    if pd.infer_freq(periodic_data.index) == 'D':
        periodic_data['m'] = periodic_data.index.to_series().dt.month
        periodic_data['y'] = periodic_data.index.to_series().dt.year
        data_monthly = periodic_data.groupby(['y', 'm']).sum()
    else:
        data_monthly = periodic_data

    data_monthly['total_contribution'] = data_monthly.cumsum().round(2).values
    data_monthly['total'] = (data_monthly['total_contribution'] + initial_savings)

    data_monthly['interest'] = 0
    data_monthly = data_monthly.reset_index()
    for idr, r in data_monthly.iterrows():
        if idr == 0:
            continue
        previous_month_end_balance = data_monthly.iloc[idr - 1, :]['total']
        previous_month_end_balance_with_interest = after_t_years(previous_month_end_balance, interest_rate,
                                                                 compounding_periods, 1 / compounding_periods)
        interest = previous_month_end_balance_with_interest - previous_month_end_balance
        data_monthly.iloc[idr - 1, data_monthly.columns.get_loc('total')] = previous_month_end_balance_with_interest
        data_monthly.iloc[idr, data_monthly.columns.get_loc('total')] = previous_month_end_balance_with_interest + \
                                                                        r[name_]
        data_monthly.iloc[idr, data_monthly.columns.get_loc('interest')] = interest
    data_monthly['cum_interest'] = data_monthly['interest'].cumsum()

    if pd.infer_freq(periodic_data.index) == 'D':
        data_monthly['index'] = data_monthly.apply(lambda r: datetime.datetime(year=int(r['y']), month=int(r['m']), day=28), axis=1)
        data_monthly['dim'] = data_monthly['index'].dt.daysinmonth
        data_monthly['index'] = data_monthly.apply(lambda r: r['index'].replace(day=r['dim']), axis=1)
        data_monthly = data_monthly.drop(columns=['dim'])

        periodic_data = periodic_data.drop(columns=['y', 'm'])
        periodic_data['total_contribution'] = periodic_data.cumsum().round(2).values
        periodic_data['total'] = (periodic_data['total_contribution'] + initial_savings)

        periodic_data = periodic_data.merge(data_monthly.set_index('index')[['interest']], how='left',
                                            left_index=True, right_index=True)
        periodic_data['interest'] = periodic_data['interest'].fillna(0)
        periodic_data['total'] = (periodic_savings + periodic_data['interest']).cumsum()

    return periodic_data


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


def pv(c, r, p, t):
    return c/pow((1 + r / p), p * t)


def fv(c, r, p, t):
    return c * (pow((1 + r / p), p * t))


def after_t_years(initial_investment, interest_rate_per_year, periods, years):
    return initial_investment * (pow((1 + interest_rate_per_year / periods), periods * years))


def interest_after_t_years(initial_investment, interest_rate_per_year, periods, years):
    return initial_investment * (pow((interest_rate_per_year / periods), periods * years))


def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

def get_next_business_day(day):
    ONE_DAY = datetime.timedelta(days=1)
    HOLIDAYS = holidays.UK()

    next_day = day
    while next_day.weekday() in holidays.WEEKEND or next_day in HOLIDAYS:
        next_day += ONE_DAY
    return next_day


def previous_business_day(day):
    ONE_DAY = datetime.timedelta(days=-1)
    HOLIDAYS = holidays.UK()

    prev_day = day + ONE_DAY
    while prev_day.weekday() in holidays.WEEKEND or prev_day in HOLIDAYS:
        prev_day += ONE_DAY
    return prev_day


def condition_transaction_date(periodic, day_transaction, next_business_day={}, prev_business_day={}):
    periodic['_m'] = periodic.index.to_series().dt.month
    periodic['_y'] = periodic.index.to_series().dt.year
    for col in periodic:
        if col in day_transaction and day_transaction[col] is not None:
            out_date = periodic.index.to_series().dt.day == day_transaction[col]
            if col in next_business_day and next_business_day[col]:
                out_dates = out_date[out_date].index.to_series().apply(get_next_business_day)
                out_date = periodic.index.to_series().isin(out_dates)
            periodic.loc[~out_date, col] = 0
        else:
            periodic[col] = periodic.groupby(['_y', '_m'])[col].transform(lambda g: g / len(g))
    periodic = periodic.drop(columns=['_m', '_y'])
    return periodic
