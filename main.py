import math

import matplotlib.pyplot as plt
import numpy_financial as npf
import pandas as pd
from matplotlib.offsetbox import AnchoredText

# from config import *
import config as cfg
from plot import *
from salary_calculation import get_salary_and_tax
from var_inputs import *
from varexinc_calculation import get_varexinc, get_compounding_exp


def generate_table_data(inflation_rate_=cfg.inflation_rate):
    print()
    monthly_salary_tax = get_salary_and_tax(cfg.annual_salary,
                                            cfg.years_until_retirement,
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
                                            cfg.PERIODS)

    monthly_compounding_exp = get_compounding_exp(
        [
            dict(
                target=saving_loan,
                source=monthly_salary_tax[cfg.savings_loans_source[saving_loan]],
                factor=cfg.savings_cost_factors[saving_loan],
                initial=cfg.initial_balances[saving_loan]
            )
            for saving_loan in cfg.savings_loans
        ],
        cfg.interest_rate,
        cfg.COMPOUNDING_PERIODS,
    )

    data_monthly = pd.concat([monthly_salary_tax, monthly_compounding_exp], axis=1)

    data_monthly = data_monthly.rename(columns={'index': 'date/time'})
    data_monthly = data_monthly.set_index('date/time')

    return data_monthly



if __name__ == '__main__':
    data_monthly = generate_table_data()

    # ------------------------------------------------------------------------------------------------------------------

    plot_pension(data_monthly, cfg.savings_goal)
    generate_pension_fig(data_monthly, cfg.savings_goal)
    print()
    # ------------------------------------------------------------------------------------------------------------------

    monthly_varinc, monthly_varex = get_varexinc(
        varex,
        varinc,
        varex_inflation,
        cfg.varex_varin_increase_inflation,
        varex_max,
        varex_end,
        varinc_inflation,
        cfg.years_until_retirement,
        cfg.start_from,
    )
    # ------------------------------------------------------------------------------------------------------------------

    income = data_monthly[['index', 'gross_salary']].merge(monthly_varinc.reset_index(), on='index').set_index('index')
    expenditure = data_monthly[
        ['index', 'income_tax_paid', 'nat_ins_paid', 'personal_pension_savings', 'student_loan', 'workplace_pension']] \
        .merge(monthly_varex.reset_index(), on='index').set_index('index')
    all = pd.concat([income, expenditure], axis=1)

    plot_bars(all, months=2)
    # ------------------------------------------------------------------------------------------------------------------

    expenditure_categories = expenditure.iloc[:0, :0]
    for k in varex_categories:
        expenditure_categories[k] = expenditure[varex_categories[k]].sum(axis=1)
    expenditure_categories = data_monthly[['index', 'income_tax_paid', 'nat_ins_paid', 'personal_pension_savings',
                                           'student_loan', 'workplace_pension']].merge(
        expenditure_categories.reset_index(), on='index').set_index('index')

    income_categories = income.iloc[:0, :0]
    for k in varinc_categories:
        income_categories[k] = income[varinc_categories[k]].sum(axis=1)
    income_categories = data_monthly[['index', 'gross_salary']] \
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


    def diff_month(d1, d2):
        return (d1.year - d2.year) * 12 + d1.month - d2.month


    months_until_retirement = diff_month(
        cfg.birthday + pd.offsets.DateOffset(years=cfg.retirement_age - cfg.age_at_time_of_writing),
        datetime.datetime.now())

    npv_savings_total = -npf.pv(cfg.interest_rate / 12, months_until_retirement, 0, cfg.total_saved)

    print()
