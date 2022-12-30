import numpy as np
import pandas as pd

from calculations import calculate_paid_yearly_salary, expand_yearly_to_monthly, calculate_yearly_series


def get_salary_and_tax(annual_salary,
                       years_until_retirement,
                       salary_increase_inflation,
                       promotion_frequency_years,
                       salary_increase_promotion,
                       role_change_frequency_years,
                       salary_decrease_role_change,
                       max_salary,
                       start_from,
                       bands_order,
                       INCOME_TAX_BANDS,
                       NAT_INS_THRESH,
                       NAT_INS_RATE,
                       PERIODS,
                       ):
    # compile series of data - annual salary until retirement
    yearly_salary = pd.Series(np.repeat([annual_salary], years_until_retirement))

    # account for inflation/salary increase, promotions, job changes and a max salary cap
    yearly_salary = calculate_yearly_series(yearly_salary,
                                            salary_increase_inflation,
                                            promotion_frequency_years,
                                            salary_increase_promotion,
                                            role_change_frequency_years,
                                            salary_decrease_role_change,
                                            max_salary)

    # compile income on monthly basis, until retirement
    yearly_salary_monthly = expand_yearly_to_monthly(yearly_salary.values, 'salary_yearly',
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

    data_monthly = yearly_salary_monthly.reset_index()

    # wrangle monthly salary, savings contributions and prepare data for calculation total savings
    data_monthly['income_tax_paid_yearly'] = -yearly_paid_salary_monthly['income_tax_paid_yearly'].values
    data_monthly['nat_ins_paid_yearly'] = -yearly_paid_salary_monthly['nat_ins_paid_yearly'].values
    data_monthly['paid_salary_yearly'] = yearly_paid_salary_monthly['paid_salary_yearly'].values
    data_monthly['salary'] = data_monthly['salary_yearly'] / PERIODS
    data_monthly['income_tax_paid'] = data_monthly['income_tax_paid_yearly'] / PERIODS
    data_monthly['nat_ins_paid'] = data_monthly['nat_ins_paid_yearly'] / PERIODS
    data_monthly['paid_salary'] = data_monthly['paid_salary_yearly'] / PERIODS

    return data_monthly