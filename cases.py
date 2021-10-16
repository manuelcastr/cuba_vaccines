#!python3.9
from datetime import date

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, AutoMinorLocator, FixedLocator


def read_data_file(filename):
    with open(filename, encoding='utf-8') as f:
        labels = f.readline().strip().split('\t')
        dates, numbers = list(), list()
        for line in f.readlines():
            if line.strip():
                data = line.strip().split('\t')
                dates.append(date.fromisoformat(data[0]))
                numbers.append(list(map(int, data[1:])))
    return np.array(labels), np.array(dates), np.array(numbers)


def common_style_settings(dates, n_days, y_max, y_label='', format_func=None, first_date=0,
                          auto_y=5, legend=True, loc='upper left'):
    x_labels = [d.strftime("%d/%m") for d in dates]
    for i in range(n_days - 1):
        if i % 7:
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
    plt.xticks(tick_positions, use_labels[tick_positions], rotation=45)
    plt.gca().set_xticks(range(n_days), minor=True)
    y_minor = AutoMinorLocator(auto_y)
    plt.gca().yaxis.set_minor_locator(y_minor)
    if format_func:
        plt.gca().get_yaxis().set_major_formatter(FuncFormatter(format_func))

    plt.gca().set_xlim(left=0, right=n_days)
    plt.gca().set_ylim(bottom=0, top=y_max * 1.05)

    plt.xlabel('Fecha')
    plt.ylabel(y_label, rotation=0)
    plt.gca().yaxis.set_label_coords(-0.015, 1)

    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)

    plt.gca().xaxis.set_tick_params(which='minor', width=.6)
    plt.gca().xaxis.set_tick_params(which='major', pad=-2)

    plt.grid(which='major', axis='y', ls=':', lw=.5, c='gray')
    plt.grid(which='minor', axis='y', ls=':', lw=.3, c='gray')

    if legend:
        plt.legend(loc=loc, ncol=1)

    plt.tight_layout()


def plot_daily_cases(labels, dates, numbers):
    plt.figure('cov-Casos_activos', (13, 6))
    plt.suptitle('Casos diarios y activos')

    n_days = len(dates)
    xs = range(n_days)
    plt.plot(xs, numbers[:, 0], label=labels[0], color='tab:orange', marker='.', lw=2)
    plt.plot(xs, numbers[:, 1], label=labels[1], color='tab:red', lw=2)

    common_style_settings(dates, n_days, numbers[:, 1].max(), '',
                          format_func=lambda x, p: f'{x*1e-3:1.0f} mil' if x > 0 else ''),

    plt.gca().spines['bottom'].set_zorder(100)
    plt.gca().spines['left'].set_zorder(100)


def plot_accumulated_cases(dates, numbers):
    plt.figure('cov-Casos_acumulados', (13, 6))
    plt.suptitle('Casos acumulados')

    n_days = len(dates)
    xs = range(n_days)
    plt.plot(xs, numbers, color='tab:red', lw=2)

    common_style_settings(dates, n_days, numbers.max(), '',
                          format_func=lambda x, p: f'{x*1e-3:1.0f} mil' if x > 0 else '',
                          auto_y=2, legend=False)

    plt.gca().spines['bottom'].set_zorder(100)
    plt.gca().spines['left'].set_zorder(100)


def plot_daily_deaths(labels, dates, numbers):
    plt.figure('cov-Fallecidos_diarios', (13, 6))
    plt.suptitle('Fallecidos diarios y acumulado')

    n_days = len(dates)
    xs = range(n_days)
    plt.plot(xs, numbers[:, 1], label=labels[1], color='tab:red', lw=2)

    common_style_settings(dates, n_days, numbers[:, 1].max(), '',
                          format_func=lambda x, p: f'{x*1e-3:1.0f} mil' if x > 0 else '',
                          legend=False)
    plt.gca().spines['bottom'].set_zorder(100)
    plt.gca().spines['left'].set_zorder(100)
    ax1: plt.Axes = plt.gca()
    ax1.minorticks_off()
    ax1.grid(False)

    ax2: plt.Axes = ax1.twinx()
    ax2.plot(xs, numbers[:, 0], label=labels[0], color='tab:orange', marker='.', lw=2)
    ax2.set_ylim(0, numbers[:, 0].max() * 5)
    y2_max = round(numbers[:, 0].max(), -2)
    ax2.yaxis.set_ticks([0, y2_max])
    ax2.yaxis.set_ticklabels(['', str(y2_max)])
    ax2.yaxis.set_minor_locator(FixedLocator(np.linspace(0, y2_max, 6)[1:]))
    ax2.grid(which='major', axis='y', ls=':', lw=.5, c='gray')
    ax2.grid(which='minor', axis='y', ls=':', lw=.3, c='gray')
    ax2.spines['top'].set_visible(False)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    plt.legend(lines2 + lines1, labels2 + labels1, loc='upper left', ncol=1)

    plt.tight_layout()


def plot_condition_vs_actives(labels, dates, numbers):
    daily = numbers[:, 0]
    deaths = numbers[:, 1]
    serious = numbers[:, 2]
    critical = numbers[:, 3]

    def percent(a, b):
        return np.round(a / b * 100, 2)

    plt.figure('cov-Porcientos_respecto_casos', (13, 6))
    plt.suptitle('Porciento de seriedad en casos diarios')

    n_days = len(dates)
    xs = range(n_days)
    d_percent = percent(deaths, daily)
    plt.plot(xs, d_percent, label=labels[0], color='black', lw=2)
    s_percent = percent(serious, daily)
    plt.plot(xs, s_percent, label=labels[1], color='tab:orange', lw=2)
    c_percent = percent(critical, daily)
    plt.plot(xs, c_percent, label=labels[2], color='tab:red', lw=2)

    common_style_settings(dates, n_days, max(d_percent.max(), s_percent.max(), c_percent.max()), '',
                          format_func=lambda x, p: f'{x:1.1f} %' if x > 0 else '', auto_y=2,
                          legend=True, loc='best')


def plot_tests_vs_cases(labels, dates, numbers):
    samples = numbers[:, 0]
    cases = numbers[:, 1]

    plt.figure('cov-Muestras_realizadas', (13, 6))
    plt.suptitle('Muestras realizadas y casos positivos')

    n_days = len(dates)
    xs = range(n_days)
    plt.plot(xs, samples, label=labels[0], color='tab:green', lw=2)
    plt.plot(xs, cases, label=labels[1], color='tab:red', lw=2)

    common_style_settings(dates, n_days, samples.max(), '',
                          format_func=lambda x, p: f'{x*1e-3:1.0f} mil' if x > 0 else '', auto_y=2,
                          legend=True, loc='upper left')


def plot_tests_positivity(labels, dates, numbers):
    samples = numbers[:, 0]
    cases = numbers[:, 1]

    plt.figure('cov-Positividad_muestras', (13, 6))
    plt.suptitle('Positividad de muestras')

    n_days = len(dates)
    xs = range(n_days)
    positives = np.round(cases / samples * 100, 2)
    plt.plot(xs, positives, label=labels[0], color='tab:red', lw=2)

    common_style_settings(dates, n_days, positives.max(), '',
                          format_func=lambda x, p: f'{x:1.1f} %' if x > 0 else '', auto_y=2,
                          legend=False, loc='upper left')


def plot_situation(filename, daily_labels=None, deaths_labels=None):
    column_labels, dates, numbers = read_data_file(filename)
    labels = column_labels[2:4] if not daily_labels else daily_labels
    plot_daily_cases(labels, dates, numbers[:, 1:3])
    plot_accumulated_cases(dates, numbers[:, 3])
    labels = column_labels[5:7] if not deaths_labels else deaths_labels
    plot_daily_deaths(labels, dates, numbers[:, 4:6])
    plot_condition_vs_actives(column_labels[[6, 7, 8]], dates, numbers[:, [1, 4, 6, 7]])
    plot_tests_vs_cases(column_labels[[1, 2]], dates, numbers[:, :2])
    plot_tests_positivity(column_labels[[1, 2]], dates, numbers[:, :2])
    plt.show()


if __name__ == '__main__':
    DAILY_LABELS = ['Casos diarios', 'Activos']
    DEATHS_LABELS = ['Fallecidos diarios', 'Acumulado']
    plot_situation('cases.txt',
                   daily_labels=DAILY_LABELS,
                   deaths_labels=DEATHS_LABELS)
