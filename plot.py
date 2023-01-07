import datetime

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
from matplotlib.offsetbox import AnchoredText


def generate_loan_figs(loans, totals):
    # wrangle outputs for plotting
    totals_ = (-1 * (totals.clip(upper=0)))
    totals_.plot()
    plt.title('Loan totals')
    plt.show()

    loans_ = (-loans).drop_duplicates()
    loans_.plot.bar()
    plt.title('Repayments')

    # plt.show()

    fig_totals = px.scatter(totals_)

    fig_repayments = px.bar(loans_)

    return fig_totals, fig_repayments


def generate_savings_figs(savings, totals):
    # wrangle outputs for plotting
    totals.plot()
    plt.title('Savings totals')
    plt.show()

    savings_ = (-savings).drop_duplicates()
    savings_.plot.bar()
    plt.title('Payments')

    # plt.show()

    fig_totals = px.scatter(totals)

    fig_payments = px.bar(savings_)

    return fig_totals, fig_payments


def generate_pension_fig(data_monthly, savings_goal):
    data_monthly_ = data_monthly[['personal_pension_savings_total', 'workplace_pension_supplement_total']].copy()
    data_monthly_ = abs(data_monthly_)
    data_monthly_['total'] = data_monthly_.sum(axis=1)
    data_monthly_['target'] = savings_goal
    total_saved = data_monthly_['total'].max()


    # plot and annotate outputs
    data_monthly_.plot()
    ax = plt.gca()
    range_ = abs(data_monthly[['personal_pension_savings', 'workplace_pension']].sum(axis=1).loc[data_monthly[['personal_pension_savings', 'workplace_pension']].sum(axis=1)!=0])
    at = AnchoredText(
        '\n'.join([
            f"£{round(total_saved, 2):,}",
            f"£{round(range_.min(), 2)} to £{round(range_.max(), 2)} per month",
        ]), prop=dict(size=12), frameon=True, loc='upper left')
    at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    ax.add_artist(at)
    plt.title('Pension savings')
    plt.legend(data_monthly_.columns.to_list(), loc='lower right')
    plt.show()

    fig = px.line(data_monthly_)
    # fig.show()
    return fig

def generate_balance_fig(daily, monthly, balance,
                         from_=datetime.datetime.now(), to_=datetime.datetime.now() + datetime.timedelta(days=365)):

    daily.loc[:to_, :].sum(axis=1).plot()
    monthly.loc[:to_, :].sum(axis=1).plot()
    plt.show()
    daily_trace = (balance + (daily.loc[from_:to_, :].sum(axis=1).cumsum()))
    daily_trace.name = 'daily'
    monthly_trace = (balance + (monthly.loc[from_:to_, :].sum(axis=1).cumsum()))
    monthly_trace.name = 'monthly'

    fig = px.line(
        pd.DataFrame(daily_trace).merge(pd.DataFrame(monthly_trace), how='left', left_index=True, right_index=True),
    )
    fig.update_traces(connectgaps=True)
    return fig


def plot_bars(varexinc: pd.DataFrame, months=1):
    fig = plt.figure(figsize=(8, 8), dpi=150)
    series = varexinc.iloc[1:months+1, :]
    series.T.sort_values(by=series.index[0], ascending=False).T.plot.bar(
        ax=plt.gca()
    )
    ax = plt.gca()
    at = AnchoredText(
        '\n'.join([f"{series.iloc[i].name.date()} left: £{round(series.iloc[i].sum(), 2):,}" for i in range(months)])
        , prop=dict(size=12), frameon=True, loc='upper center')
    at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    ax.add_artist(at)
    plt.legend(loc=6, prop={'size': 6})
    plt.title('\n'.join([f'{series.T.columns[i]}' for i in range(months)]))
    plt.show()