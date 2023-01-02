import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
import dash
from dash import html
from dash import dcc
import pickle
import os
import dash_bootstrap_components as dbc
import main as m
import plotly.figure_factory as ff
import plotly.express as px

def plot_pension(data_monthly, savings_goal):
    # wrangle outputs for plotting
    data_monthly_ = data_monthly[['net_salary_yearly', 'personal_pension_savings_total', 'workplace_pension_supplement_total']].copy()
    data_monthly_['total'] = data_monthly_['personal_pension_savings_total'] + data_monthly_['workplace_pension_supplement_total']
    data_monthly_['target'] = savings_goal
    total_saved = data_monthly_['total'].max()


    # plot and annotate outputs
    data_monthly_.plot()
    ax = plt.gca()
    at = AnchoredText(
        '\n'.join([
            f"£{round(total_saved, 2):,}",
            f"£{-data_monthly['personal_pension_savings'].max().round(2)} to £{-data_monthly['personal_pension_savings'].min().round(2)} per month",
        ]), prop=dict(size=12), frameon=True, loc='upper center')
    at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    ax.add_artist(at)
    plt.title('Pension savings')
    plt.show()

def generate_pension_fig(data_monthly, savings_goal):
    # wrangle outputs for plotting
    data_monthly_ = data_monthly[['net_salary_yearly', 'personal_pension_savings_total', 'workplace_pension_supplement_total']].copy()
    data_monthly_['total'] = data_monthly_['personal_pension_savings_total'] + data_monthly_['workplace_pension_supplement_total']
    data_monthly_['target'] = savings_goal
    total_saved = data_monthly_['total'].max()

    fig = px.line(data_monthly_)
    # fig.show()
    return fig


def plot_bars(varexinc: pd.DataFrame, months=1):
    fig = plt.figure(figsize=(8, 8), dpi=150)
    series = varexinc.iloc[:months, :]
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