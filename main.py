import pandas as pd
import datetime
import math
import numpy_financial as npf
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
import numpy as np
from calculations import calculate_paid_yearly_salary, expand_yearly_to_monthly, calculate_yearly_series, calculate_compound_savings, interest_after_t_years

PERIODS = 12
COMPOUNDING_PERIODS = 12

# user inputs
age_at_time_of_writing = 26  # Current age of the user
birthday = datetime.datetime(year=2022, month=11, day=10)
country = 'Scotland'

annual_salary = 42000  # Annual salary of the user
initial_personal_savings = 10000
initial_student_loan_paid = 120*12*3
initial_workplace_pension = 912*2
workplace_pension_amount = 0.028
employer_pension_contribution = 0.07  # at 3.5% contribution

retirement_age = 65  # Age at which the user wants to retire
save_factor = 0.15
student_loan_factor = 0.04
savings_goal = 1e6  # Savings goal for retirement

# variable expenditure
varex = {
    'phone': -39.90,
    'crossfit': -90,
    'rent': -895,
    'DVLA': -1.75,
    'electricity': -83.35,
    'gas': -80,
    'zwift': -12.99,
    'specsavers': -21,
    'pcp': -201.41,
    'council tax': -150,
    'internet': -36,
    'work phone': -6,
    'spotify': -16.99,
    'monzo premium': -15,
    'credit ladder': -8,
    'headspace': -10,
    'mum loan': -168,
    'klarna': -147.7,
    'amazon prime': -7.99,
    'google drive': -2.49,

    'groceries': -280,
    'fuel': -175,
    'eating out': -100,
    'entertainment': -100,
    'transport': -20,
    'personal care': -20,
    #      xmas,rp,lm,
    'gifts': -((500+75+30*7+30*3)/12),
    '': 0,

}
varex_max = {
    'phone': -75,
    'crossfit': -120,
    'rent': -1350,
    'DVLA': -5,
    'electricity': -150,
    'zwift': -15,
    'specsavers': -40,
    'pcp': -750,
    'council tax': -250,
    'internet': -50,
    'work phone': -15,
    'spotify': -25,
    'monzo premium': -20,
    'credit ladder': -8,
    'headspace': -20,
    'mum loan': -168,

}
varex_end = {
    'phone': None,
    'crossfit': None,
    'rent': None,
    'DVLA': None,
    'electricity': None,
    'zwift': None,
    'specsavers': None,
    'pcp': None,
    'council tax': None,
    'internet': None,
    'work phone': None,
    'spotify': None,
    'monzo premium': None,
    'credit ladder': None,
    'headspace': None,
    'klarna': datetime.datetime(year=2023, month=1, day=8),
    'mum loan': datetime.datetime(year=2025, month=2, day=1),
}
varex_inflation = {
    'phone': True,
    'crossfit': True,
    'rent': True,
    'DVLA': True,
    'electricity': True,
    'zwift': True,
    'specsavers': True,
    'pcp': True,
    'council tax': True,
    'internet': True,
    'work phone': True,
    'spotify': True,
    'monzo premium': True,
    'credit ladder': True,
    'headspace': True,
    'mum loan': True
}

# variable income
varinc = {
    'spotify': 2.50*3,
    'rebecca': 340,
    'mum loan': 170,
}
varinc_end = {
    'spotify': None,
    'rebecca': None,
    'mum loan': datetime.datetime(year=2025, month=2, day=1),
}
varinc_inflation = {
    'spotify': True,
    'rebecca': True,
    'mum loan': False,
}
# default inputs
inflation_rate = 0
# inflation_rate = 0.03
# interest_rate = 0.03  # Annual interest rate of the savings account
interest_rate = inflation_rate  # Annual interest rate of the savings account
# salary_increase_inflation = 0.03
salary_increase_inflation = inflation_rate
# varex_varin_increase_inflation = 0.03
varex_varin_increase_inflation = inflation_rate

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

if __name__ == '__main__':
    # calculated configurations
    bands_order = list(INCOME_TAX_BANDS.keys())
    current_age = age_at_time_of_writing + math.floor((datetime.datetime.now() - birthday).days/365)

    def diff_month(d1, d2):
        return (d1.year - d2.year) * 12 + d1.month - d2.month

    months_until_retirement = diff_month(birthday + pd.offsets.DateOffset(years=retirement_age-age_at_time_of_writing),
        datetime.datetime.now())

    years_until_retirement = retirement_age - current_age

    # compile series of data - annual salary until retirement
    yearly_salary = pd.Series(np.repeat([annual_salary], years_until_retirement))

    yearly_varex = pd.DataFrame({k: pd.Series(np.repeat([v], years_until_retirement)) for k, v in varex.items()})
    yearly_varinc = pd.DataFrame({k: pd.Series(np.repeat([v], years_until_retirement)) for k, v in varinc.items()})

    for idc, col in yearly_varex.iteritems():
        if varex_inflation.get(idc, True):
            yearly_col = calculate_yearly_series(col, varex_varin_increase_inflation, max_amount=varex_max.get(idc, varex[idc]),
                                                 inflate_max_amount=True)
            yearly_varex[idc] = yearly_col

    for idc, col in yearly_varinc.iteritems():
        if varinc_inflation.get(idc, False):
            yearly_col = calculate_yearly_series(col, varex_varin_increase_inflation)
            yearly_varinc[idc] = yearly_col

    # yearly_var = pd.concat([yearly_varex, yearly_varinc], axis=1)

    # account for inflation/salary increase, promotions, job changes and a max salary cap
    yearly_salary = calculate_yearly_series(yearly_salary,
                                            salary_increase_inflation,
                                            promotion_frequency_years,
                                            salary_increase_promotion,
                                            role_change_frequency_years,
                                            salary_decrease_role_change,
                                            max_salary)


    # compile income on monthly basis, until retirement
    yearly_salary_monthly = expand_yearly_to_monthly(yearly_salary.values, 'salary',
                             years_until_retirement,
                             start_from)


    # calculate paid salary based on national insurance and income tax deductions
    yearly_paid_salary = calculate_paid_yearly_salary(yearly_salary,
                                                      bands_order,
                                                      INCOME_TAX_BANDS,
                                                      NAT_INS_THRESH,
                                                      NAT_INS_RATE)

    monthly_salary_tax = []
    for idc, col in yearly_paid_salary.iteritems():
        monthly = expand_yearly_to_monthly(col.values, idc,
                                 years_until_retirement,
                                 start_from)
        monthly_salary_tax.append(monthly)

    yearly_paid_salary_monthly = pd.concat(monthly_salary_tax, axis=1)

    monthly_varex = []
    for idc, col in yearly_varex.iteritems():
        monthly = expand_yearly_to_monthly(col.values, idc,
                                 years_until_retirement,
                                 start_from)
        if varex_end.get(idc, None) is not None:
            monthly.loc[varex_end.get(idc, None):] = 0
        monthly_varex.append(monthly)

    monthly_varex = pd.concat(monthly_varex, axis=1)

    monthly_varinc = []
    for idc, col in yearly_varinc.iteritems():
        monthly = expand_yearly_to_monthly(col.values, idc,
                                 years_until_retirement,
                                 start_from)
        monthly_varinc.append(monthly)

    monthly_varinc = pd.concat(monthly_varinc, axis=1)

    data_monthly = yearly_salary_monthly.reset_index()

    # wrangle monthly salary, savings contributions and prepare data for calculation total savings
    data_monthly['salary_monthly'] = data_monthly['salary'] / 12
    data_monthly['paid_salary'] = yearly_paid_salary_monthly['paid_salary'].values
    data_monthly['income_tax_paid'] = -yearly_paid_salary_monthly['income_tax_paid'].values
    data_monthly['nat_ins_paid'] = -yearly_paid_salary_monthly['nat_ins_paid'].values
    data_monthly['paid_salary_monthly'] = data_monthly['paid_salary'] / PERIODS
    data_monthly['income_tax_paid_monthly'] = data_monthly['income_tax_paid'] / PERIODS
    data_monthly['nat_ins_paid_monthly'] = data_monthly['nat_ins_paid'] / PERIODS

    data_monthly['personal_savings'] = data_monthly['paid_salary_monthly'] * save_factor
    data_monthly['student_loan'] = data_monthly['paid_salary_monthly'] * student_loan_factor
    data_monthly['workplace_pension'] = data_monthly['salary_monthly'] * (workplace_pension_amount +
                                                                          employer_pension_contribution * (workplace_pension_amount/0.035))

    # calculate total compound savings based on constant interest rate
    for c, initial in [('personal_savings', initial_personal_savings),
                       ('student_loan', initial_student_loan_paid),
                       ('workplace_pension', initial_workplace_pension)]:

        total = calculate_compound_savings(data_monthly[c], initial, interest_rate, COMPOUNDING_PERIODS)
        data_monthly[f'{c}_total'] = total['total']

    # wrangle outputs for plotting
    data_monthly_ = data_monthly[['index', 'personal_savings_total', 'workplace_pension_total']].copy()
    data_monthly_['total'] = data_monthly_['personal_savings_total'] + data_monthly_['workplace_pension_total']
    data_monthly_['target'] = savings_goal
    total_saved = data_monthly_['total'].max()
    data_monthly_ = data_monthly_.set_index('index')

    # plot and annotate outputs
    data_monthly_.plot()
    ax = plt.gca()
    at = AnchoredText(
        f"£{round(total_saved, 2):,}", prop=dict(size=12), frameon=True, loc='upper center')
    at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    ax.add_artist(at)
    plt.show()

    income = data_monthly[['index', 'salary_monthly']].merge(monthly_varinc.reset_index(), on='index').set_index('index')
    expenditure = data_monthly[['index', 'income_tax_paid_monthly', 'nat_ins_paid_monthly']].merge(monthly_varex.reset_index(), on='index').set_index('index')
    all = pd.concat([income, expenditure], axis=1)
    fig = plt.figure(figsize=(8, 8), dpi=150)
    series = all.iloc[:2, :]
    series.T.sort_values(by=series.index[0], ascending=False).T.plot.bar(
        ax=plt.gca()
    )
    ax = plt.gca()
    at = AnchoredText(
        f"{series.iloc[0].name.date()} left: £{round(series.iloc[0].sum(), 2):,}\n"
        f"{series.iloc[1].name.date()} left: £{round(series.iloc[1].sum(), 2):,}", prop=dict(size=12), frameon=True, loc='upper center')
    at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    ax.add_artist(at)
    plt.legend(loc=6, prop={'size': 6})
    plt.title(f'{series.T.columns[0]}')
    plt.show()
    series.iloc[0].sort_values(ascending=False)
    income['total'] = income.sum(axis=1)
    expenditure['total'] = expenditure.sum(axis=1)
    total = income[['total']].merge(expenditure[['total']], left_index=True, right_index=True, suffixes=['_income', '_expenditure'])
    total['net'] = total['total_income'] + total['total_expenditure']
    # total['balance'] = total['net'].cumsum()
    total.iloc[:12*1, :].plot.bar()
    # ax = plt.gca()
    # at = AnchoredText(
    #     f"£{round(total_saved, 2):,}", prop=dict(size=12), frameon=True, loc='upper center')
    # at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    # ax.add_artist(at)
    plt.show()

    # infer insights from outputs
    mortality_age = 95
    months_of_retirement = (mortality_age - retirement_age) * 12
    retirement_funds_per_month = total_saved / months_of_retirement
    npv_savings_total = -npf.pv(interest_rate/12, months_until_retirement, 0, total_saved)

    print()
