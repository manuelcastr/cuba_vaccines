#!python3.9
import pathlib
from datetime import date

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, AutoMinorLocator


def read_data_file(filename):
    with open(filename) as f:
        labels = f.readline().strip().split('\t')
        dates, numbers = list(), list()
        for line in f.readlines():
            if line.strip():
                data = line.strip().split('\t')
                dates.append(date.fromisoformat(data[0]))
                numbers.append(list(map(int, data[1:])))
    return labels, dates, np.array(numbers)


def common_style_settings(fig: plt.Figure, dates, n_days, y_max, y_label='',
                          format_func=None, first_date=0, span=7, ncol=1):
    axes: plt.Axes = fig.gca()
    x_labels = [d.strftime("%d/%m") for d in dates]
    for i in range(n_days - 1):
        if i % span:
            x_labels[n_days-1 - i] = ''
    if first_date != 0:
        x_labels[0] = ''
        x_labels[first_date] = dates[first_date].strftime("%d/%m")
        x_labels[first_date+1] = ''
        x_labels[first_date+2] = ''
    use_labels = np.array(x_labels)
    no_labels = [1, 2]
    if first_date in no_labels:
        no_labels.remove(first_date)
    use_labels[no_labels] = ''
    tick_positions = np.where(x_labels)[0]
    axes.set_xticks(tick_positions, use_labels[tick_positions], rotation=45)
    # axes.set_xticks(range(n_days), minor=True)
    y_minor = AutoMinorLocator(5)
    axes.yaxis.set_minor_locator(y_minor)
    if format_func:
        axes.get_yaxis().set_major_formatter(FuncFormatter(format_func))

    axes.set_xlim(left=0, right=n_days)
    axes.set_ylim(bottom=0, top=y_max * 1.05)

    plt.xlabel('Fecha')
    plt.ylabel(y_label, rotation=0)
    axes.yaxis.set_label_coords(-0.015, 1)

    axes.spines['right'].set_visible(False)
    axes.spines['top'].set_visible(False)

    axes.xaxis.set_tick_params(which='minor', width=.6)
    axes.xaxis.set_tick_params(which='major', pad=-2)

    axes.grid(which='major', axis='y', ls=':', lw=.5, c='gray')
    axes.grid(which='minor', axis='y', ls=':', lw=.3, c='gray')

    axes.legend(loc='upper left', ncol=ncol).set_zorder(500)

    fig.tight_layout()


def plot_accumulate_doses(labels, dates, numbers, suptitle='Acumulados por dosis'):
    fig: plt.Figure = plt.figure(suptitle, (13, 6))
    plt.suptitle(suptitle)

    n_days = len(dates)
    xs = range(n_days)
    fig.gca().fill_between(xs, numbers[:, 1], label=labels[0],
                           color='tab:blue', zorder=10, edgecolor='k', lw=.6)
    # fig.gca().fill_between(xs, numbers[:, 2], label=labels[1],
    #                        color='tab:green', zorder=11, edgecolor='k', lw=.3)
    # fig.gca().fill_between(xs, numbers[:, 3], label=labels[2],
    #                        color='tab:orange', zorder=12, edgecolor='k', lw=.3)
    fig.gca().fill_between(xs, numbers[:, 4], label=labels[3],
                           color=(.88, .39, .0), zorder=11, edgecolor='k', lw=.6)  # color=(.88, .39, .0)
    fig.gca().fill_between(xs, numbers[:, 5], label=labels[4],
                           color='tab:red', zorder=13, edgecolor='k', lw=.6)

    common_style_settings(fig, dates, n_days, numbers[:, 1].max(), 'Millones',
                          format_func=lambda x, p: f'{x*1e-6:1.1f} M' if x > 0 else '',
                          span=14)

    plt.gca().spines['bottom'].set_zorder(100)
    plt.gca().spines['left'].set_zorder(100)

    return fig


def plot_daily_doses(labels, dates, numbers, suptitle='Dosis diarias'):
    fig: plt.Figure = plt.figure(suptitle, (13, 6))
    fig.suptitle(suptitle)

    n_days = len(dates)
    xs = np.array(list(range(1, n_days))) + .08
    width = .19
    colors = ['tab:blue', 'tab:green', 'tab:orange', (.88, .39, .0), 'tab:red']
    dataset = np.array([(numbers[:, i] - np.roll(numbers[:, i], 1))[1:] for i in range(6)])[1:]
    uniques = (numbers[:, -1] - numbers[:, -2])
    uniques = (uniques - np.roll(uniques, 1))[1:]
    dataset[0] -= uniques
    dataset[-1] = uniques
    for i in range(5):
        plt.bar(xs + width * (i-3), dataset[i], width, label=labels[i], zorder=100,
                color=colors[i], edgecolor='k', linewidth=.5)

    common_style_settings(fig, dates, n_days, dataset.max(), 'Miles',
                          format_func=lambda x, p: f'{x*1e-3:1.0f} K' if x > 0 else '',
                          first_date=1, ncol=2)
    return fig


def plot_stacked_daily_doses(labels, dates, numbers, suptitle='Dosis diarias '):
    fig: plt.Figure = plt.figure(suptitle, (13, 6))
    fig.suptitle(suptitle)
    axes = fig.gca()

    n_days = len(dates)
    xs = np.array(list(range(1, n_days)))
    width = .86
    dataset = np.array([(numbers[:, i] - np.roll(numbers[:, i], 1))[1:] for i in range(6)])[1:]
    uniques = (numbers[:, -2] - numbers[:, -3])
    uniques = (uniques - np.roll(uniques, 1))[1:]
    dataset[0] -= uniques
    dataset[-2] = uniques
    axes.bar(xs, dataset[0], width, color='tab:blue', zorder=100, label=labels[0])
    axes.bar(xs, dataset[1], width, color='tab:green', zorder=100, label=labels[1],
             bottom=dataset[0])
    axes.bar(xs, dataset[2], width, color='tab:orange', zorder=100, label=labels[2],
             bottom=dataset[0] + dataset[1])
    axes.bar(xs, dataset[3], width, color=(.88, .39, .0), zorder=100, label=labels[3],
             bottom=dataset[0] + dataset[1] + dataset[2])
    axes.bar(xs, dataset[4], width, color='tab:red', zorder=100, label=labels[4],
             bottom=dataset[0] + dataset[1] + dataset[2] + dataset[3])

    axes.bar(xs, dataset.sum(axis=0), width, fill=False, edgecolor='k', linewidth=.5, zorder=200)
    for i in range(n_days-1):
        axes.plot([xs[i] - width / 2, xs[i] + width / 2], [dataset[0, i]] * 2, c='k', lw=.5, zorder=200)
        axes.plot([xs[i] - width / 2, xs[i] + width / 2], [dataset[[0, 1], i].sum()] * 2, c='k', lw=.5, zorder=200)
        if uniques[i]:
            axes.plot([xs[i] - width / 2, xs[i] + width / 2], [dataset[[0, 1, 2], i].sum()] * 2, c='k', lw=.5, zorder=201)
        if numbers[i, -1]:
            axes.plot([xs[i] - width / 2, xs[i] + width / 2], [dataset[[0, 1, 2, 3], i].sum()] * 2, c='k', lw=.5, zorder=202)

    common_style_settings(fig, dates, n_days, dataset.sum(axis=0).max(), 'Miles',
                          format_func=lambda x, p: f'{x*1e-3:1.0f} K' if x > 0 else '',
                          first_date=1, ncol=2, span=14)
    return fig


def report_vaccination(filename, accum_labels=None, daily_labels=None,
                       images_path=None, show=True):
    column_labels, dates, numbers = read_data_file(filename)
    labels = accum_labels if accum_labels else column_labels[2:]
    fig_accum = plot_accumulate_doses(labels, dates, numbers)
    labels = daily_labels if daily_labels else column_labels[2:]
    # n = 61
    # fig_daily = plot_daily_doses(labels, dates[-n:], numbers[-n:, ])
    fig_stack = plot_stacked_daily_doses(labels, dates, numbers)

    if images_path:
        images_path = pathlib.Path(images_path)
        fig_accum.savefig(images_path / 'vac-Acumulados_dosis.png')
        # fig_daily.savefig(images_path / 'vac-Dosis_diarias_recientes.png')
        fig_stack.savefig(images_path / 'vac-Dosis_diarias.png')

    if show:
        plt.show()

    plt.close('all')
    plt.show()


if __name__ == '__main__':
    ACCUMULATED_LABELS = ['Primera dosis', 'Segunda dosis', 'Tercera dosis',
                          'Esquema completo', 'Refuerzo']
    DAILY_DOSES_LABELS = ['Primera dosis', 'Segunda dosis', 'Tercera dosis',
                          'Dosis única', 'Refuerzo']
    report_vaccination('vaccines.txt',
                       accum_labels=ACCUMULATED_LABELS,
                       daily_labels=DAILY_DOSES_LABELS,
                       images_path='./',
                       show=False)
