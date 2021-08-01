#!python3.9
from datetime import date

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator


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


def common_style_settings(dates, n_days, y_max, format_func=None):
    x_labels = [d.strftime("%d/%m") for d in dates]
    for i in range(n_days - 1):
        if i % 7:
            x_labels[n_days-1 - i] = ''
    plt.xticks(range(n_days), x_labels, rotation=45)

    # plt.gca().get_yaxis().set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
    if format_func:
        plt.gca().get_yaxis().set_major_formatter(FuncFormatter(format_func))

    plt.gca().set_xlim(left=0, right=n_days)
    plt.gca().set_ylim(bottom=0, top=y_max * 1.05)

    plt.xlabel('Fecha')
    plt.ylabel('Cantidad')

    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)

    plt.minorticks_on()
    plt.gca().xaxis.set_tick_params(which='minor', bottom=False)
    plt.gca().xaxis.set_tick_params(which='major', pad=-2)

    plt.grid(which='major', axis='y', ls=':', lw=.5, c='gray')
    plt.grid(which='minor', axis='y', ls=':', lw=.3, c='gray')

    plt.legend(loc='upper left', ncol=1)

    plt.tight_layout()


def plot_accumulate_doses(labels, dates, numbers):
    plt.figure('Acumulados por dosis', (13, 6))
    plt.suptitle('Acumulados por dosis')

    n_days = len(dates)
    xs = range(n_days)
    plt.fill_between(xs, numbers[:, 1], label=labels[2], color='tab:blue', zorder=10)
    plt.fill_between(xs, numbers[:, 2], label=labels[3], color='tab:green', zorder=11)
    plt.fill_between(xs, numbers[:, 3], label=labels[4], color='tab:orange', zorder=12)

    common_style_settings(dates, n_days, numbers[:, 1].max(),
                          format_func=lambda x, p: f'{x*1e-6:1.1f} M' if x > 0 else '')

    plt.gca().spines['bottom'].set_zorder(100)
    plt.gca().spines['left'].set_zorder(100)


def plot_daily_doses(labels, dates, numbers):
    plt.figure('Dosis diarias', (13, 6))
    plt.suptitle('Dosis diarias')

    n_days = len(dates)
    xs = np.array(list(range(1, n_days)))
    width = .29
    colors = ['tab:blue', 'tab:green', 'tab:orange']
    dataset = np.array([(numbers[:, i] - np.roll(numbers[:, i], 1))[1:] for i in range(4)])
    for i in range(1, 4):
        plt.bar(xs + width * (i-2), dataset[i], width, label=labels[i+1], zorder=100,
                color=colors[i-1], edgecolor='k', linewidth=.5)

    plt.plot(xs, dataset[0], zorder=1, c='tab:red', label='Total diario')

    common_style_settings(dates, n_days, dataset[0].max(),
                          format_func=lambda x, p: f'{x*1e-3:1.0f} K' if x > 0 else '')


def plot_stacked_daily_doses(labels, dates, numbers):
    plt.figure('Dosis diarias (stack)', (13, 6))
    plt.suptitle('Dosis diarias')

    n_days = len(dates)
    xs = np.array(list(range(1, n_days)))
    width = .86
    dataset = np.array([(numbers[:, i] - np.roll(numbers[:, i], 1))[1:] for i in range(4)])
    plt.bar(xs, dataset[1], width, color='tab:blue', zorder=100, label=labels[2])
    plt.bar(xs, dataset[2], width, color='tab:green', zorder=100, label=labels[3],
            bottom=dataset[1])
    plt.bar(xs, dataset[3], width, color='tab:orange', zorder=100, label=labels[4],
            bottom=dataset[1] + dataset[2])

    plt.bar(xs, dataset[1:].sum(axis=0), width, fill=False, edgecolor='k', linewidth=.5, zorder=200)
    for i in range(n_days-1):
        plt.plot([xs[i] - width / 2, xs[i] + width / 2], [dataset[1][i]] * 2, c='k', lw=.5, zorder=200)
        plt.plot([xs[i] - width / 2, xs[i] + width / 2], [dataset[[1, 2], i].sum()] * 2, c='k', lw=.5, zorder=200)

    common_style_settings(dates, n_days, dataset[0].max(),
                          format_func=lambda x, p: f'{x*1e-3:1.0f} K' if x > 0 else '')


def plot_vaccination(filename):
    labels, dates, numbers = read_data_file(filename)
    plot_accumulate_doses(labels, dates, numbers)
    plot_daily_doses(labels, dates, numbers)
    plot_stacked_daily_doses(labels, dates, numbers)

    plt.show()


if __name__ == '__main__':
    plot_vaccination('vaccines.txt')
