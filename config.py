import datetime
import os
import enum
import math

DIR = os.path.dirname(__file__)

PERIODS = 12
COMPOUNDING_PERIODS = 12

# user inputs
age_at_time_of_writing = 26  # Current age of the user
birthday = datetime.datetime(year=2022, month=11, day=10)
country = 'Scotland'

as_of = datetime.datetime(year=2022, month=12, day=29)
annual_salary = 42000  # Annual salary of the user

savings_loans = [
    'personal_pension_savings',
    'house_savings',
    'student_loan',
    'workplace_pension',
    'workplace_pension_supplement'
]

savings_loans_source = {
    'personal_pension_savings': 'net_salary',
    'house_savings': 'net_salary',
    'student_loan': 'gross_salary',
    'workplace_pension': 'gross_salary',
    'workplace_pension_supplement': 'gross_salary',
}

initial_balances = {
    'personal_pension_savings': 0,
    'house_savings': 10000,
    'student_loan': 120 * 12 * 3,
    'workplace_pension': 0,
    'workplace_pension_supplement': 912 * 2
}

retirement_age = 65  # Age at which the user wants to retire
savings_goal = 1e6  # Savings goal for retirement

savings_cost_factors = {
    'house_savings': 0.114/2,
    'personal_pension_savings': 0.114/2,
    'student_loan': 0.04,
    'workplace_pension': 0.028,
    'workplace_pension_supplement': 0.07  # at workplace_pension_supplement_limit = 3.5%
}

workplace_pension_supplement_limit = 0.035

#
savings_cost_factors['workplace_pension_overall'] = (savings_cost_factors['workplace_pension'] +
                                                        savings_cost_factors['workplace_pension_supplement'] *
                                                        (savings_cost_factors['workplace_pension'] / workplace_pension_supplement_limit))

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
salary_increase_promotion = 0.08
promotion_frequency_years = 5

# salary_decrease_role_change = 0
# role_change_frequency_years = 0
salary_decrease_role_change = -0.05
role_change_frequency_years = 10

# max_salary = 1 * 1e6
max_salary = 110 * 1e6

start_from = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
# start_from = datetime.datetime(year=2023, month=4, day=1, hour=6)

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

# calculated configurations
bands_order = list(INCOME_TAX_BANDS.keys())
current_age = age_at_time_of_writing + math.floor((datetime.datetime.now() - birthday).days / 365)

years_until_retirement = retirement_age - current_age
