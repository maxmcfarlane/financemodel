# from config import *
import matplotlib.pyplot as plt
import pandas as pd
import pickle
import config as cfg
import savings_loans as snl
import var_inputs
# from plot import *
import plot
from salary_calculation import get_salary_and_tax
from varexinc_calculation import get_varexinc, get_compounding_exp

DAYS = 365
MONTHS = 12


def combine_by_month(df, sum_all=False):
    periodic_salary_tax_data_ = df.copy()
    periodic_salary_tax_data_['_m'] = df.index.to_series().dt.month
    periodic_salary_tax_data_['_y'] = df.index.to_series().dt.year

    periodic_salary_tax_data_monthly = periodic_salary_tax_data_.groupby(['_y', '_m'])

    periodic_salary_tax_data_monthly = periodic_salary_tax_data_monthly[[c for c in periodic_salary_tax_data_.columns
                                                                         if c not in ['_y', '_m']]]

    periodic_salary_tax_data_monthly = periodic_salary_tax_data_monthly \
        .aggregate(lambda g: sum(g) if sum_all else max(g) if all(g >= 0) else min(g) if all(g <= 0) else sum(g))

    periodic_salary_tax_data_monthly['date/time'] = periodic_salary_tax_data_ \
        .reset_index().groupby(['_y', '_m'])['date/time'] \
        .aggregate(lambda g: max(g))
    periodic_salary_tax_data_monthly = periodic_salary_tax_data_monthly.set_index('date/time')
    return periodic_salary_tax_data_monthly



def check_savings_loan_completion(periodic_compounding_exp, target_amount):
    periodic_compounding_exp_ = periodic_compounding_exp.copy()
    snl_achieved = {}
    for name, target in target_amount.items():
        target_date = snl.target_date.get(name, cfg.from_date)
        if target is None:
            if target_date is not None:
                periodic_compounding_exp_.loc[target_date:, name] = 0
                periodic_compounding_exp_.loc[target_date:, name + '_interest'] = 0
                periodic_compounding_exp_.loc[target_date:, name + '_total'] = periodic_compounding_exp_.loc[:target_date, name + '_total'].max()
            snl_achieved[name] = {'total': target,
                                  'achieved': True,
                                  'date_achieved': None,
                                  'on_time': True}
            continue
        periodic_compounding_exp_.loc[periodic_compounding_exp_[name + '_total'] > target, name] = 0
        periodic_compounding_exp_.loc[periodic_compounding_exp_[name + '_total'] > target, name + '_interest'] = 0

        _diff = (periodic_compounding_exp_[name + '_total'] > target).diff().fillna(False)
        if True in _diff.values:
            date_achieved = _diff[_diff].index.to_series().squeeze()
            total = periodic_compounding_exp_.loc[date_achieved, name + '_total']
            periodic_compounding_exp_.loc[periodic_compounding_exp_[name + '_total'] > target, name + '_total'] = total
            snl_achieved[name] = {'total': total,
                                  'achieved': True,
                                  'date_achieved': date_achieved,
                                  'on_time': date_achieved <= (target_date if target_date is not None else cfg.from_date)}
        else:
            total = periodic_compounding_exp_.loc[:, name + '_total'].max()
            snl_achieved[name] = {'total': total,
                                  'achieved': False,
                                  'date_achieved': None,
                                  'on_time': False}

    return periodic_compounding_exp_, pd.DataFrame(snl_achieved).T


def generate_table_data():
    years = cfg.days_until_retirement / DAYS

    # calculate salary and tax through time
    periodic_salary_tax = get_salary_and_tax(
        cfg.days_until_retirement,  # volume,
        DAYS,  # granularity,
        years,
        'D',  # freq,
        cfg.annual_salary,
        cfg.pay_day,
        snl.savings_loans_day,
        cfg.salary_increase_inflation,
        cfg.promotion_frequency_years,
        cfg.salary_increase_promotion,
        cfg.role_change_frequency_years,
        cfg.salary_decrease_role_change,
        cfg.max_salary,
        cfg.from_date,
        cfg.bands_order,
        cfg.INCOME_TAX_BANDS,
        cfg.NAT_INS_THRESH,
        cfg.NAT_INS_RATE,
    )

    # calculate savings and loan amounts through time
    periodic_compounding_exp = get_compounding_exp(
        periodic_salary_tax,
        snl.source,
        snl.cost_factors,
        snl.interest,
        snl.initial_balances,
        snl.names,
        cfg.interest_rate,
        cfg.COMPOUNDING_PERIODS,
        snl.target_amount,
    )

    periodic_compounding_exp_capped, snl_achieved = check_savings_loan_completion(periodic_compounding_exp,
                                                                                  snl.target_amount)

    periodic_salary_tax_saving_loan_data = pd.concat([periodic_salary_tax, periodic_compounding_exp_capped], axis=1)

    periodic_salary_tax_saving_loan_data.index.names = ['date/time']

    periodic_salary_tax_data_monthly = combine_by_month(periodic_salary_tax_saving_loan_data)

    return periodic_salary_tax_saving_loan_data, periodic_salary_tax_data_monthly, years

    #
    # return daily, monthly, periodic_salary_tax_saving_loan_data, income, expenditure, periodic_salary_tax_data_monthly, \
    #        income_monthly, expenditure_monthly, daily_balance, monthly_balance


def generate_with_varinvex(periodic_salary_tax_saving_loan_data, years):

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
        var_inputs.varinc_prev_business_day,
        cfg.varex_varin_increase_inflation,
        var_inputs.varex_max,
        var_inputs.varex_end,
        var_inputs.varinc_end,
        var_inputs.varinc_inflation,
        var_inputs.varinc_in,
        cfg.from_date,
    )
    # ------------------------------------------------------------------------------------------------------------------

    income = periodic_salary_tax_saving_loan_data[[]].merge(periodic_varinc, left_index=True, right_index=True)
    expenditure = periodic_salary_tax_saving_loan_data[
        []] \
        .merge(periodic_varex, left_index=True, right_index=True)

    income_monthly = combine_by_month(periodic_varinc, sum_all=True)
    expenditure_monthly = combine_by_month(periodic_varex, sum_all=True)

    daily = pd.concat([
        periodic_salary_tax_saving_loan_data[cfg.GROSS_SALARY + cfg.TAX_COLS + snl.get_savings() + snl.get_loans()],
        income,
        expenditure,
    ], axis=1)
    monthly = combine_by_month(daily, sum_all=True)

    daily_balance = pd.DataFrame({'balance': daily.sum(axis=1).cumsum()}) + cfg.balance
    monthly_balance = pd.DataFrame({'balance': monthly.sum(axis=1).cumsum()}) + cfg.balance

    return daily, monthly, income, expenditure, income_monthly, expenditure_monthly, daily_balance, monthly_balance


def solve_savings_loans(periodic_salary_tax, years, balance_proportion=0.01):

    periodic_salary_tax = periodic_salary_tax.copy()

    def check():
        # calculate savings and loan amounts through time
        periodic_compounding_exp = get_compounding_exp(
            periodic_salary_tax,
            snl.source,
            snl.cost_factors,
            snl.interest,
            snl.initial_balances,
            snl.names,
            cfg.interest_rate,
            cfg.COMPOUNDING_PERIODS,
            snl.target_amount,
        )

        periodic_compounding_exp_capped, snl_achieved = check_savings_loan_completion(periodic_compounding_exp,
                                                                                      snl.target_amount)

        periodic_salary_tax_saving_loan_data = pd.concat([periodic_salary_tax, periodic_compounding_exp_capped], axis=1)

        periodic_salary_tax_saving_loan_data.index.names = ['date/time']

        # periodic_salary_tax_data_monthly = combine_by_month(periodic_salary_tax_saving_loan_data)

        daily, monthly, income, expenditure, income_monthly, expenditure_monthly, daily_balance, monthly_balance = \
            generate_with_varinvex(periodic_salary_tax_saving_loan_data, years)

        balance_okay = ((daily_balance['balance'] < 0).sum() / len(daily_balance)) <= balance_proportion
        daily_balance.plot()
        plt.show()
        return balance_okay, snl_achieved
        # return True, snl_achieved

    balance_okay, snl_achieved = check()

    def get_targets():
        targets_not_achieved = snl_achieved.index[snl_achieved['on_time'].apply(lambda c: not c)].tolist()
        aggregate_targets = list(set(filter(lambda t: '+' in t, targets_not_achieved)))

        targets = sum([[a for name in a.split('+') if snl.variable[name]] for a in aggregate_targets], [])
        controls = sum([[name for name in a.split('+') if snl.variable[name]] for a in aggregate_targets], [])

        controls_targets = sum([[(name, a) for name in a.split('+') if snl.variable[name]] for a in aggregate_targets], [])
        unobtainable = list(set(aggregate_targets) - set(targets))

        targets = list((set(targets_not_achieved) - set(aggregate_targets)).union(set(controls_targets)))
        unobtainable = set(unobtainable).union(set([t for t in targets if not snl.variable[t if not isinstance(t, tuple) else t[0]]]))

        targets = set(targets) - unobtainable

        unobtainable_ = [t for t in targets if snl.target_date[t if not isinstance(t, tuple) else t[1]] > periodic_salary_tax.index.max()]

        unobtainable = unobtainable.union(set(unobtainable_))

        targets = set(targets) - unobtainable
        return targets

    targets = get_targets()

    while len(targets) > 0:

        print('-'*40)
        print(f'Targets not satisfied: {targets}')
        print('-'*40)
        for target in targets:
            if isinstance(target, tuple):
                control = target[0]
                target = target[1]
            else:
                control = target
            savings_factor = snl.cost_factors[control] if snl.cost_factors[control] is not None else 0
            print(f"\t{target} total:    {round(snl_achieved.T.to_dict()[target]['total'], 2)}")
            print(f"\t{target} achieved by:    {snl_achieved.T.to_dict()[target]['date_achieved']}")
            print(f"\t{control} factor:    {round(savings_factor, 2)}")
            snl.set_cost_factor(
                control,
                savings_factor + 0.01
                )
            savings_factor = snl.cost_factors[control] if snl.cost_factors[control] is not None else 0
            print(f"\tnew {control} factor:    {round(savings_factor, 2)}")
            print('\t'+'-'*40)
        balance_okay, snl_achieved_new = check()
        snl_achieved = snl_achieved_new
        targets = get_targets()

    final_cost_factors = snl.cost_factors
    balance_okay, snl_achieved_new = check()

    print()


def solve():
    years = cfg.days_until_retirement / DAYS

    # calculate salary and tax through time
    periodic_salary_tax = get_salary_and_tax(
        cfg.days_until_retirement,  # volume,
        DAYS,  # granularity,
        years,
        'D',  # freq,
        cfg.annual_salary,
        cfg.pay_day,
        snl.savings_loans_day,
        cfg.salary_increase_inflation,
        cfg.promotion_frequency_years,
        cfg.salary_increase_promotion,
        cfg.role_change_frequency_years,
        cfg.salary_decrease_role_change,
        cfg.max_salary,
        cfg.from_date,
        cfg.bands_order,
        cfg.INCOME_TAX_BANDS,
        cfg.NAT_INS_THRESH,
        cfg.NAT_INS_RATE,
    )

    solve_savings_loans(periodic_salary_tax, years)


if __name__ == '__main__':
    # solve()
    # daily, monthly, periodic_salary_tax_saving_loan_data, income, expenditure, \
    # periodic_salary_tax_data_monthly, income_monthly, expenditure_monthly, \
    # daily_balance, monthly_balance = \
    #     generate_table_data()

    years = cfg.days_until_retirement / DAYS

    # calculate salary and tax through time
    periodic_salary_tax = get_salary_and_tax(
        cfg.days_until_retirement,  # volume,
        DAYS,  # granularity,
        years,
        'D',  # freq,
        cfg.annual_salary,
        cfg.pay_day,
        snl.savings_loans_day,
        cfg.salary_increase_inflation,
        cfg.promotion_frequency_years,
        cfg.salary_increase_promotion,
        cfg.role_change_frequency_years,
        cfg.salary_decrease_role_change,
        cfg.max_salary,
        cfg.from_date,
        cfg.bands_order,
        cfg.INCOME_TAX_BANDS,
        cfg.NAT_INS_THRESH,
        cfg.NAT_INS_RATE,
    )

    periodic_salary_tax = periodic_salary_tax.copy()

    # calculate savings and loan amounts through time
    periodic_compounding_exp = get_compounding_exp(
        periodic_salary_tax,
        snl.source,
        snl.cost_factors,
        snl.interest,
        snl.initial_balances,
        snl.names,
        cfg.interest_rate,
        cfg.COMPOUNDING_PERIODS,
        snl.target_amount,
    )

    periodic_compounding_exp_capped, snl_achieved = check_savings_loan_completion(periodic_compounding_exp,
                                                                                  snl.target_amount)

    periodic_salary_tax_saving_loan_data = pd.concat([periodic_salary_tax, periodic_compounding_exp_capped], axis=1)

    periodic_salary_tax_saving_loan_data.index.names = ['date/time']

    periodic_salary_tax_data_monthly = combine_by_month(periodic_salary_tax_saving_loan_data)

    daily, monthly, income, expenditure, income_monthly, expenditure_monthly, daily_balance, monthly_balance = \
        generate_with_varinvex(periodic_salary_tax_saving_loan_data, years)

    # ------------------------------------------------------------------------------------------------------------------

    # fig = px.line(data_monthly)
    # fig.show()

    pension_fig = plot.generate_pension_fig(periodic_salary_tax_data_monthly, cfg.pension_goal)
    balance_fig = plot.generate_balance_fig(daily, monthly, cfg.balance)
    loan_fig, _ = plot.generate_loan_figs(periodic_salary_tax_saving_loan_data[snl.get_loans()],
                                     periodic_salary_tax_saving_loan_data[snl.get_loan_totals()])
    savings_fig, _ = plot.generate_savings_figs(periodic_salary_tax_saving_loan_data[snl.get_savings()],
                                           periodic_salary_tax_saving_loan_data[snl.get_savings_totals()])

    pickle.dump((
        pension_fig,
        daily, monthly,
        periodic_salary_tax_data_monthly,
        balance_fig,
        loan_fig,
        savings_fig,
    ), open('./cache.p', 'wb'))

    # ------------------------------------------------------------------------------------------------------------------

    salary_tax_monthly = periodic_salary_tax_data_monthly[cfg.GROSS_SALARY + cfg.TAX_COLS + snl.get_savings() + snl.get_loans()]
    all = pd.concat([salary_tax_monthly, income_monthly, expenditure_monthly], axis=1)

    plot.plot_bars(all, months=1)
    # ------------------------------------------------------------------------------------------------------------------

    expenditure_categories = expenditure.iloc[:0, :0]
    for k in var_inputs.varex_categories:
        expenditure_categories[k] = expenditure[var_inputs.varex_categories[k]].sum(axis=1)
    expenditure_categories = periodic_salary_tax_saving_loan_data[
        ['index', 'income_tax_paid', 'nat_ins_paid', 'personal_pension_savings',
         'student_loan', 'workplace_pension']].merge(
        expenditure_categories.reset_index(), on='index').set_index('index')

    income_categories = income.iloc[:0, :0]
    for k in var_inputs.varinc_categories:
        income_categories[k] = income[var_inputs.varinc_categories[k]].sum(axis=1)
    income_categories = periodic_salary_tax_saving_loan_data[['index', 'gross_salary']] \
        .merge(income_categories.reset_index(), on='index') \
        .set_index('index')

    all_categories = pd.concat([income_categories, expenditure_categories], axis=1)

    plot.plot_bars(all_categories, months=2)

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
    # mortality_age = 95
    # months_of_retirement = (mortality_age - cfg.retirement_age) * 12
    # retirement_funds_per_month = cfg.total_saved / months_of_retirement

    # npv_savings_total = -npf.pv(cfg.interest_rate / 12, months_until_retirement, 0, cfg.total_saved)
