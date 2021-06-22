from datetime import date

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


def read_data_file(filename):
    with open(filename) as f:
        labels = f.readline().strip().split('\t')
        dates, numbers = list(), list()
        for line in f.readlines():
            if line:
                data = line.strip().split('\t')
                dates.append(date.fromisoformat(data[0]))
                numbers.append(list(map(int, data[1:])))
    return labels, dates, np.array(numbers)


def plot_accumulate_doses(labels, dates, numbers):
    plt.figure('Acumulados por dosis', (13, 6))
    plt.suptitle('Acumulados por dosis')

    n_days = len(dates)
    xs = range(n_days)
    plt.fill_between(xs, numbers[:, 1], label=labels[2], zorder=1)
    plt.fill_between(xs, numbers[:, 2], label=labels[3], zorder=2)
    plt.fill_between(xs, numbers[:, 3], label=labels[4], zorder=3)

    daily_values = numbers[:, 0] - np.roll(numbers[:, 0], 1)
    daily_values = daily_values[1:]  # Discard 1st day
    xs = range(1, n_days)
    daily_bars = plt.bar(xs, daily_values, .5, zorder=10, label='Dosis diarias')
    for rect, value in zip(daily_bars, daily_values):
        plt.text(rect.get_x() + rect.get_width() / 2, rect.get_height(), f'{value:,}',
                 ha='center', va='bottom', fontsize='small')

    plt.xticks(range(n_days), [d.strftime("%d/%m") for d in dates], rotation=45)
    plt.gca().get_yaxis().set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
    plt.minorticks_on()
    plt.gca().xaxis.set_tick_params(which='minor', bottom=False)
    plt.gca().set_xlim(left=-0.05)
    plt.gca().set_ylim(bottom=0)
    plt.xlabel('Fecha')
    plt.ylabel('Cantidad')

    plt.axvline(x=n_days-1 - 14, ls='--', c='darkgray', zorder=0)

    plt.legend(loc='upper left')
    plt.grid(ls=':', lw=.4, c='gray')
    plt.tight_layout()


def plot_daily_doses(labels, dates, numbers):
    plt.figure('Dosis diarias', (13, 6))
    plt.suptitle('Dosis diarias')

    n_days = len(dates)
    xs = np.array(list(range(1, n_days)))
    width = .3
    for i in range(1, 4):
        values = (numbers[:, i] - np.roll(numbers[:, i], 1))[1:]
        plt.bar(xs + width * (i-2), values, width, label=labels[i+1], zorder=100)

    totals = (numbers[:, 0] - np.roll(numbers[:, 0], 1))[1:]
    plt.plot(xs, totals, marker='.', zorder=1, c='tab:red', label='Total diario')
    margin = totals.max() * .01
    for x, y in zip(xs, totals):
        plt.text(x, y + margin, f'{y:,}', ha='center', va='bottom', fontsize='small', zorder=100)

    plt.xticks(range(n_days), [d.strftime("%d/%m") for d in dates], rotation=45)
    plt.gca().get_yaxis().set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
    plt.minorticks_on()
    plt.gca().xaxis.set_tick_params(which='minor', bottom=False)
    plt.gca().set_xlim(left=-0.05)
    plt.gca().set_ylim(bottom=0, top=totals.max() * 1.1)
    plt.xlabel('Fecha')
    plt.ylabel('Cantidad')

    plt.axvline(x=n_days-1 - 14, ls='--', c='darkgray', zorder=0)

    plt.legend(loc='upper center', ncol=4)
    plt.grid(ls=':', lw=.4, c='gray')
    plt.tight_layout()


def plot_vaccination(filename):
    labels, dates, numbers = read_data_file(filename)
    plot_accumulate_doses(labels, dates, numbers)
    plot_daily_doses(labels, dates, numbers)

    plt.show()


if __name__ == '__main__':
    plot_vaccination('vaccines.txt')
