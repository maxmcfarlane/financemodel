import datetime
import os
import pandas as pd

import config as cfg

names = [
    'workplace_pension',
    'student_loan',
    'healthcare_offset_loan',
    'underpaid_tax_loan',
    'personal_pension_savings',
    'house_savings',
    'workplace_pension_supplement',
]

interest = {
    'workplace_pension': True,
    'student_loan': True,
    'healthcare_offset_loan': False,
    'underpaid_tax_loan': False,
    'personal_pension_savings': True,
    'house_savings': True,
    'workplace_pension_supplement': True,
}

source = {
    'workplace_pension': 'gross_salary',
    'student_loan': 'gross_salary',
    'healthcare_offset_loan': 'gross_salary',
    'underpaid_tax_loan': 'gross_salary',
    'personal_pension_savings': 'net_salary',
    'house_savings': 'net_salary',
    'workplace_pension_supplement': 'gross_salary',
}

type_ = {
    'workplace_pension': 'savings',
    'student_loan': 'loan',
    'healthcare_offset_loan': 'loan',
    'underpaid_tax_loan': 'loan',
    'personal_pension_savings': 'savings',
    'house_savings': 'savings',
    'workplace_pension_supplement': 'aggregated_savings',
}

savings_loans_day = {
    'workplace_pension': cfg.pay_day,
    'student_loan': cfg.pay_day,
    'healthcare_offset_loan': cfg.pay_day,
    'underpaid_tax_loan': cfg.pay_day,
    'personal_pension_savings': cfg.pay_day + 1,
    'house_savings': cfg.pay_day + 1,
    'workplace_pension_supplement': cfg.pay_day,
}

initial_balances = {
    'workplace_pension': 0,
    'student_loan': -25000 + 120 * 12 * 3,
    'healthcare_offset_loan': 0,
    'underpaid_tax_loan': 0,
    'personal_pension_savings': 0,
    'house_savings': 10000,
    'workplace_pension_supplement': 912 * 2
}

cost_factors = {
    'workplace_pension': 0.028,
    'student_loan': 0.0362,
    'healthcare_offset_loan': 343.30 / 42000,
    'underpaid_tax_loan': 151.4025 / (42000 / 12),
    'workplace_pension_supplement': 0.07,  # at workplace_pension_supplement_limit = 3.5%

    'house_savings': 0.1,  # savings_factor/2,  # 0.114/2
    'personal_pension_savings': 0.1,  # savings_factor/2,  # 0.114/2
    # 'house_savings': None,  # savings_factor/2,  # 0.114/2
    # 'personal_pension_savings': None,  # savings_factor/2,  # 0.114/2
}

variable = {
    'workplace_pension': False,
    'student_loan': False,
    'healthcare_offset_loan': False,
    'underpaid_tax_loan': False,
    'workplace_pension_supplement': False,  # at workplace_pension_supplement_limit = 3.5%

    'house_savings': True,  # savings_factor/2,  # 0.114/2
    'personal_pension_savings': True,  # savings_factor/2,  # 0.114/2
    # 'house_savings': None,  # savings_factor/2,  # 0.114/2
    # 'personal_pension_savings': None,  # savings_factor/2,  # 0.114/2
}

target_amount = {
    'workplace_pension': None,
    'student_loan': 0,
    'healthcare_offset_loan': None,
    'underpaid_tax_loan': None,
    'workplace_pension_supplement': None,  # at workplace_pension_supplement_limit = 3.5%

    'house_savings': 15 * 1e3,  # savings_factor/2,  # 0.114/2
    'personal_pension_savings': None,  # savings_factor/2,  # 0.114/2
    'personal_pension_savings+workplace_pension_supplement': cfg.pension_goal,  # savings_factor/2,  # 0.114/2
}

target_date = {
    'workplace_pension': None,
    'student_loan': None,
    'healthcare_offset_loan': None,
    'underpaid_tax_loan': datetime.datetime(year=2023, month=4, day=1),
    'workplace_pension_supplement': None,  # at workplace_pension_supplement_limit = 3.5%

    'house_savings': datetime.datetime(year=2024, month=6, day=28),  # savings_factor/2,  # 0.114/2
    'personal_pension_savings': None,  # savings_factor/2,  # 0.114/2
    'personal_pension_savings+workplace_pension_supplement': cfg.from_date +
                                                             datetime.timedelta(days=cfg.days_until_retirement - 1),
    # savings_factor/2,  # 0.114/2
}

workplace_pension_supplement_limit = 0.035

#
cost_factors['workplace_pension_supplement'] = cost_factors['workplace_pension'] + \
                                               min([cost_factors['workplace_pension'] * 2,
                                                    cost_factors['workplace_pension_supplement']])

savings_loans = pd.Series()
settings = pd.DataFrame()


def compile_settings():
    global \
        names, \
        savings_loans, \
        settings, \
        interest, \
        source, \
        type_, \
        savings_loans_day, \
        initial_balances, \
        cost_factors, \
        variable, \
        target_amount, \
        target_date
    settings = pd.concat([
        pd.Series(interest, name='interest'),
        pd.Series(source, name='source'),
        pd.Series(type_, name='type_'),
        pd.Series(savings_loans_day, name='savings_loans_day'),
        pd.Series(initial_balances, name='initial_balances'),
        pd.Series(cost_factors, name='cost_factors'),
        pd.Series(variable, name='variable'),
        pd.Series(target_amount, name='target_amount'),
        pd.Series(target_date, name='target_date'),
    ], axis=1)
    savings_loans = pd.Series(names, name='savings_loans')


compile_settings()


def uncompile_settings(settings_, savings_loans_):
    global \
        names, \
        interest, \
        source, \
        type_, \
        savings_loans_day, \
        initial_balances, \
        cost_factors, \
        variable, \
        target_amount, \
        target_date
    interest = settings_['interest'].to_dict()
    source = settings_['source'].to_dict()
    type_ = settings_['type_'].to_dict()
    savings_loans_day = settings_['savings_loans_day'].to_dict()
    initial_balances = settings_['initial_balances'].to_dict()
    cost_factors = settings_['cost_factors'].to_dict()
    variable = settings_['variable'].to_dict()
    target_amount = settings_['target_amount'].to_dict()
    target_date = settings_['target_date'].to_dict()
    names = savings_loans_.to_list()


def write_settings():
    global settings, savings_loans
    savings_loans.to_json('./savings_loans.json') if settings is not None else None
    settings.to_json('./settings.json') if settings is not None else None


if not os.path.exists('./savings_loans.json') or not os.path.exists('./settings.json'):
    write_settings()


def read_settings():
    global settings, savings_loans
    savings_loans = pd.read_json('./savings_loans.json', typ='series')
    settings = pd.read_json('./settings.json')


def settings_out(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        compile_settings()
        write_settings()
        return func
    return wrapper


if os.path.exists('./savings_loans.json') and os.path.exists('./settings.json'):
    read_settings()
    uncompile_settings(settings, savings_loans)


@settings_out
def set_cost_factor(n, v):
    global cost_factors
    cost_factors.update({n: v})


@settings_out
def set_savings_factor(
        savings_factor_,
):
    global savings_factor, cost_factors
    savings_factor = savings_factor_
    cost_factors.update(
        {
            'house_savings': (savings_factor / 2) if savings_factor_ is not None else None,  # 0.114/2
            'personal_pension_savings': (savings_factor / 2) if savings_factor_ is not None else None,  # 0.114/2
        }
    )


def get_savings():
    return list([k for k, v in type_.items() if v == 'savings'])


def get_savings_totals():
    return list([k + '_total' for k, v in type_.items() if v == 'savings'])


def get_loans():
    return list([k for k, v in type_.items() if v == 'loan'])


def get_loan_totals():
    return list([k + '_total' for k, v in type_.items() if v == 'loan'])
