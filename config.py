import datetime
import math
import os

import pandas as pd

from calculations import diff_month, get_previous_business_day

DIR = os.path.dirname(__file__)

PERIODS = 12
COMPOUNDING_PERIODS = 12

# user inputs
age_at_time_of_writing = 26  # Current age of the user
birthday = datetime.datetime(year=2022, month=11, day=10)
country = 'Scotland'

# as_of = datetime.datetime(year=2022, month=12, day=29)
# start_from = datetime.datetime(year=2023, month=1, day=1, hour=1)
start_from = {'year': 2022, 'month': 12, 'day': 24, 'prev_business_day': True}
end_on = {'year': 2025, 'month': 12, 'day': 28, 'prev_business_day': True}
balance = 1289.24
annual_salary = 42000  # Annual salary of the user
pay_day = 24
savings_factor = 0.114

monthly_daily = False

retirement_age = 65  # Age at which the user wants to retire
# retirement_age = 30  # Age at which the user wants to retire
pension_goal = 1e6  # Savings goal for retirement

# default inputs
# inflation_rate = 0
inflation_rate = 0.03
# interest_rate = 0.03  # Annual interest rate of the savings account
interest_rate = inflation_rate  # Annual interest rate of the savings account
# salary_increase_inflation = 0.03
salary_increase_inflation = inflation_rate
# varex_varin_increase_inflation = 0.03
varex_varin_increase_inflation = inflation_rate


def set_inflation_rate(
        inflation_rate_,
        interest_rate_,
        salary_increase_inflation_,
        varex_varin_increase_inflation_,
        assume_inflation=True
):
    global inflation_rate, interest_rate, salary_increase_inflation, varex_varin_increase_inflation
    if assume_inflation:
        inflation_rate = inflation_rate_
        # interest_rate = 0.03  # Annual interest rate of the savings account
        interest_rate = inflation_rate  # Annual interest rate of the savings account
        # salary_increase_inflation = 0.03
        salary_increase_inflation = inflation_rate
        # varex_varin_increase_inflation = 0.03
        varex_varin_increase_inflation = inflation_rate
    else:
        inflation_rate = inflation_rate_
        # interest_rate = 0.03  # Annual interest rate of the savings account
        interest_rate = interest_rate_  # Annual interest rate of the savings account
        # salary_increase_inflation = 0.03
        salary_increase_inflation = salary_increase_inflation_
        # varex_varin_increase_inflation = 0.03
        varex_varin_increase_inflation = varex_varin_increase_inflation_


def set_promotion_rate(
        promotion_frequency_years_,
):
    global promotion_frequency_years
    promotion_frequency_years = promotion_frequency_years_




# salary_increase_promotion = 0
# promotion_frequency_years = 0
salary_increase_promotion = 0.07
promotion_frequency_years = 5

# salary_decrease_role_change = 0
# role_change_frequency_years = 0
salary_decrease_role_change = -0.05
role_change_frequency_years = 10

# max_salary = 1 * 1e6
# max_salary = 110 * 1e6
max_salary = 95 * 1e3

# start_from = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)

GROSS_SALARY = ['gross_salary']
SALARY_COLS = ['gross_salary', 'net_salary']
YEARLY_SALARY_COLS = ['gross_salary_yearly', 'net_salary_yearly']
TAX_COLS = ['income_tax_paid', 'nat_ins_paid']
YEARLY_TAX_COLS = ['income_tax_paid_yearly', 'nat_ins_paid_yearly']

# periodically updated, locked inputs
if country == 'Scotland':
    NAT_INS_THRESH = 242
    NAT_INS_RATE = 0.1325
    INCOME_TAX_BANDS = {
        12.571: 0,
        14.732: 0.19,
        25.688: 0.2,
        43.662: 0.21,
        150: 0.41
    }
else:
    # todo - account for other countries (process will likely change)
    NAT_INS_THRESH = 242
    NAT_INS_RATE = 0.1325
    INCOME_TAX_BANDS = {
        12.571: 0,
        14.732: 0.19,
        25.688: 0.2,
        43.662: 0.21,
        150: 0.41
    }

from_date = datetime.datetime(year=start_from['year'], month=start_from['month'], day=start_from['month'])
to_date = datetime.datetime(year=end_on['year'], month=end_on['month'], day=end_on['month'])

if start_from['prev_business_day']:
    from_date = get_previous_business_day(from_date)
if end_on['prev_business_day']:
    to_date = get_previous_business_day(to_date)

# calculated configurations
bands_order = list(INCOME_TAX_BANDS.keys())
current_age = age_at_time_of_writing + math.floor((from_date - birthday).days / 365)

years_until_retirement = retirement_age - current_age
months_until_retirement = diff_month(
    birthday + pd.offsets.DateOffset(years=retirement_age - age_at_time_of_writing),
    from_date
)
days_until_retirement = (birthday + pd.offsets.DateOffset(years=retirement_age - age_at_time_of_writing) -
                         from_date).days + 1

retirement_date = birthday + datetime.timedelta(days=days_until_retirement)

days_until_end = (to_date - from_date).days + 1


def set_from_date(from_date_):
    global from_date, days_until_end
    from_date = from_date_
    days_until_end = (to_date - from_date).days + 1


def set_to_date(to_date_):
    global to_date, days_until_end
    to_date = to_date_
    days_until_end = (to_date - from_date).days + 1

