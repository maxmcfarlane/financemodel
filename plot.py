import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.offsetbox import AnchoredText


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