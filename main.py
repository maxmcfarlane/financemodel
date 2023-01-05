import math

import matplotlib.pyplot as plt
import numpy_financial as npf
import datetime
import pandas as pd
from matplotlib.offsetbox import AnchoredText

# from config import *
import config as cfg
from plot import *
from calculations import diff_month
from salary_calculation import get_salary_and_tax
import var_inputs
from varexinc_calculation import get_varexinc, get_compounding_exp

DAYS = 365
MONTHS = 12


def combine(df, sum_all=False):
    periodic_salary_tax_data_ = df.copy()
    periodic_salary_tax_data_['_m'] = df.index.to_series().dt.month
    periodic_salary_tax_data_['_y'] = df.index.to_series().dt.year
    periodic_salary_tax_data_monthly = periodic_salary_tax_data_ \
        .groupby(['_y', '_m']) \
        [[c for c in periodic_salary_tax_data_.columns if c not in ['_y', '_m']]] \
        .aggregate(lambda g: sum(g) if sum_all else max(g) if all(g >= 0) else min(g) if all(g <= 0) else sum(g))
    periodic_salary_tax_data_monthly['date/time'] = periodic_salary_tax_data_ \
        .reset_index() \
        .groupby(['_y', '_m']) \
        ['date/time'] \
        .aggregate(lambda g: max(g))
    periodic_salary_tax_data_monthly = periodic_salary_tax_data_monthly.set_index('date/time')
    return periodic_salary_tax_data_monthly


def generate_table_data():
    years = cfg.days_until_retirement / DAYS

    periodic_salary_tax = get_salary_and_tax(
        cfg.days_until_retirement,  # volume,
        DAYS,  # granularity,
        years,
        'D',  # freq,
        cfg.annual_salary,
        cfg.pay_day,
        cfg.savings_loans_day,
        cfg.salary_increase_inflation,
        cfg.promotion_frequency_years,
        cfg.salary_increase_promotion,
        cfg.role_change_frequency_years,
        cfg.salary_decrease_role_change,
        cfg.max_salary,
        cfg.start_from,
        cfg.bands_order,
        cfg.INCOME_TAX_BANDS,
        cfg.NAT_INS_THRESH,
        cfg.NAT_INS_RATE,
    )

    periodic_compounding_exp = get_compounding_exp(
        [
            dict(
                target=saving_loan,
                source=periodic_salary_tax[cfg.savings_loans_source[saving_loan]],
                factor=cfg.savings_cost_factors[saving_loan],
                initial=cfg.initial_balances[saving_loan]
            )
            for saving_loan in cfg.savings_loans
        ],
        cfg.interest_rate,
        cfg.COMPOUNDING_PERIODS,
    )

    periodic_salary_tax_data = pd.concat([periodic_salary_tax, periodic_compounding_exp], axis=1)

    periodic_salary_tax_data.index.names = ['date/time']

    periodic_varinc, periodic_varex = get_varexinc(
        cfg.days_until_retirement,  # volume,
        DAYS,  # granularity,
        years,
        'D',  # freq,
        var_inputs.varex,
        var_inputs.varinc,
        var_inputs.varex_inflation,
        var_inputs.varex_out,
        var_inputs.varex_next_business_day,
        cfg.varex_varin_increase_inflation,
        var_inputs.varex_max,
        var_inputs.varex_end,
        var_inputs.varinc_inflation,
        var_inputs.varinc_in,
        cfg.start_from,
    )
    # ------------------------------------------------------------------------------------------------------------------

    income = periodic_salary_tax_data[[]].merge(periodic_varinc, left_index=True, right_index=True)
    expenditure = periodic_salary_tax_data[
        []] \
        .merge(periodic_varex, left_index=True, right_index=True)

    periodic_salary_tax_data_monthly = combine(periodic_salary_tax_data)
    income_monthly = combine(periodic_varinc, sum_all=True)
    expenditure_monthly = combine(periodic_varex, sum_all=True)

    return periodic_salary_tax_data, income, expenditure,  periodic_salary_tax_data_monthly, income_monthly, expenditure_monthly



if __name__ == '__main__':
    periodic_salary_tax_data, income, expenditure,\
        periodic_salary_tax_data_monthly, income_monthly, expenditure_monthly = generate_table_data()

    # ------------------------------------------------------------------------------------------------------------------

    plot_pension(periodic_salary_tax_data, cfg.savings_goal)

    # fig = px.line(data_monthly)
    # fig.show()

    generate_pension_fig(periodic_salary_tax_data, cfg.savings_goal)

    # ------------------------------------------------------------------------------------------------------------------

    salary_tax_monthly = periodic_salary_tax_data_monthly[cfg.GROSS_SALARY + cfg.TAX_COLS + cfg.get_savings() + cfg.get_loans()]
    all = pd.concat([salary_tax_monthly, income_monthly, expenditure_monthly], axis=1)

    plot_bars(all, months=1)
    # ------------------------------------------------------------------------------------------------------------------

    expenditure_categories = expenditure.iloc[:0, :0]
    for k in var_inputs.varex_categories:
        expenditure_categories[k] = expenditure[var_inputs.varex_categories[k]].sum(axis=1)
    expenditure_categories = periodic_salary_tax_data[['index', 'income_tax_paid', 'nat_ins_paid', 'personal_pension_savings',
                                           'student_loan', 'workplace_pension']].merge(
        expenditure_categories.reset_index(), on='index').set_index('index')

    income_categories = income.iloc[:0, :0]
    for k in var_inputs.varinc_categories:
        income_categories[k] = income[var_inputs.varinc_categories[k]].sum(axis=1)
    income_categories = periodic_salary_tax_data[['index', 'gross_salary']] \
        .merge(income_categories.reset_index(), on='index') \
        .set_index('index')

    all_categories = pd.concat([income_categories, expenditure_categories], axis=1)

    plot_bars(all_categories, months=2)

    # ------------------------------------------------------------------------------------------------------------------

    income['total'] = income.sum(axis=1)
    expenditure['total'] = expenditure.sum(axis=1)
    total = income[['total']].merge(expenditure[['total']], left_index=True, right_index=True,
                                    suffixes=['_income', '_expenditure'])
    total['net'] = total['total_income'] + total['total_expenditure']
    # total['balance'] = total['net'].cumsum()
    total.iloc[:12 * 1, :].plot.bar()
    # ax = plt.gca()
    # at = AnchoredText(
    #     f"£{round(total_saved, 2):,}", prop=dict(size=12), frameon=True, loc='upper center')
    # at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    # ax.add_artist(at)
    plt.show()
    # ------------------------------------------------------------------------------------------------------------------

    # infer insights from outputs
    mortality_age = 95
    months_of_retirement = (mortality_age - cfg.retirement_age) * 12
    retirement_funds_per_month = cfg.total_saved / months_of_retirement



    npv_savings_total = -npf.pv(cfg.interest_rate / 12, months_until_retirement, 0, cfg.total_saved)


