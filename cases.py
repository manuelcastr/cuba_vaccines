#!python3.9
import pathlib
from datetime import date

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.ticker import AutoMinorLocator, FuncFormatter, FixedLocator


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


def common_style_settings(figure: plt.Figure, dates, n_days, y_max, y_label='',
                          format_func=None, auto_y=5, legend=True, loc='upper left',
                          span=28):
    x_dates = [d.strftime("%d/%m/%y") for d in dates]
    x_labels = [''] * len(x_dates)
    for i in range(len(x_labels) - 1, 0, -span):
        x_labels[i] = x_dates[i]
    x_labels[0] = x_dates[0]
    for i in range(1, 4):
        if x_labels[i]:
            x_labels[i] = '\n'

    use_labels = np.array(x_labels)
    tick_positions = np.where(x_labels)[0]
    use_labels = use_labels[tick_positions]

    axes = figure.gca()

    axes.set_xticks(tick_positions, use_labels, rotation=45, fontsize='small')
    y_minor = AutoMinorLocator(auto_y)
    axes.yaxis.set_minor_locator(y_minor)
    if format_func:
        axes.get_yaxis().set_major_formatter(FuncFormatter(format_func))

    axes.set_xlim(left=0, right=n_days)
    axes.set_ylim(bottom=0, top=y_max * 1.05)

    axes.set_xlabel('Fecha')
    axes.set_ylabel(y_label, rotation=0)
    axes.yaxis.set_label_coords(-0.015, 1)

    axes.spines['right'].set_visible(False)
    axes.spines['top'].set_visible(False)

    axes.xaxis.set_tick_params(which='minor', width=.6)
    axes.xaxis.set_tick_params(which='major', pad=-2)

    axes.grid(which='major', axis='y', ls=':', lw=.5, c='gray')
    axes.grid(which='minor', axis='y', ls=':', lw=.3, c='gray')

    if legend:
        axes.legend(loc=loc, ncol=1)

    figure.tight_layout()


def plot_daily_cases(labels, dates, numbers, suptitle='Casos diarios y activos', **kwargs):
    fig: plt.Figure = plt.figure(suptitle, (13, 6))
    fig.suptitle(suptitle)

    n_days = len(dates)
    xs = range(n_days)
    fig.gca().plot(xs, numbers[:, 0], label=labels[0], color='tab:orange', marker='.', lw=2)
    fig.gca().plot(xs, numbers[:, 1], label=labels[1], color='tab:red', lw=2)

    y_max = numbers[:, 1].max()
    if y_max // 10**4:
        label_format_func = lambda x, p: f'{x*1e-3:1.0f} mil' if x > 0 else ''  # noqa
    else:
        label_format_func = None

    common_style_settings(fig, dates, n_days, y_max, '',
                          format_func=label_format_func,
                          **kwargs),

    fig.gca().spines['bottom'].set_zorder(100)
    fig.gca().spines['left'].set_zorder(100)
    return fig


def plot_accumulated_cases(dates, numbers, suptitle='Casos acumulados'):
    fig: plt.Figure = plt.figure(suptitle, (13, 6))
    fig.suptitle(suptitle)

    n_days = len(dates)
    xs = range(n_days)
    fig.gca().plot(xs, numbers, color='tab:red', lw=2)

    def label_format_func(x, p):
        if x > 0:
            if x // 1e+6:
                return f'{x*1e-6:1.1f} M'
            elif x // 1e+4:
                return f'{x * 1e-3:1.0f} mil'
            else:
                return str(x)
        return ''

    common_style_settings(fig, dates, n_days, numbers.max(), '',
                          format_func=label_format_func,
                          auto_y=2, legend=False)

    fig.gca().spines['bottom'].set_zorder(100)
    fig.gca().spines['left'].set_zorder(100)

    return fig


def plot_daily_deaths(labels, dates, numbers, suptitle='Fallecidos diarios y acumulado'):
    fig: plt.Figure = plt.figure(suptitle, (13, 6))
    fig.suptitle(suptitle)

    n_days = len(dates)
    xs = range(n_days)
    fig.gca().plot(xs, numbers[:, 1], label=labels[1], color='tab:red', lw=2)

    common_style_settings(fig, dates, n_days, numbers[:, 1].max(), '',
                          format_func=lambda x, p: f'{x*1e-3:1.0f} mil' if x > 0 else '',
                          legend=False)
    fig.gca().spines['bottom'].set_zorder(100)
    fig.gca().spines['left'].set_zorder(100)
    ax1: plt.Axes = fig.gca()
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
    fig.gca().legend(lines2 + lines1, labels2 + labels1, loc='upper left', ncol=1)

    fig.tight_layout()

    return fig


def plot_condition_vs_actives(labels, dates, numbers,
                              suptitle='Porciento de seriedad en casos diarios',
                              **kwargs):
    daily = numbers[:, 0]
    deaths = numbers[:, 1]
    serious = numbers[:, 2]
    critical = numbers[:, 3]

    def percent(a, b):
        return np.round(a / b * 100, 2)

    fig: plt.Figure = plt.figure(suptitle, (13, 6))
    fig.suptitle(suptitle)

    n_days = len(dates)
    xs = np.arange(n_days)
    d_percent = percent(deaths, daily)
    fig.gca().plot(xs, d_percent, label=labels[0], color='black', lw=2)
    fig.gca().plot(xs, d_percent.cumsum() / (xs + 1), color='black', lw=1.5, ls=':')
    s_percent = percent(serious, daily)
    fig.gca().plot(xs, s_percent, label=labels[1], color='tab:orange', lw=2)
    fig.gca().plot(xs, s_percent.cumsum() / (xs + 1), color='tab:orange', lw=1.5, ls=':')
    c_percent = percent(critical, daily)
    fig.gca().plot(xs, c_percent, label=labels[2], color='tab:red', lw=2)
    fig.gca().plot(xs, c_percent.cumsum() / (xs + 1), color='tab:red', lw=1.5, ls=':')

    common_style_settings(fig, dates, n_days,
                          max(d_percent.max(), s_percent.max(), c_percent.max()), '',
                          format_func=lambda x, p: f'{x:1.1f} %' if x > 0 else '', auto_y=2,
                          legend=True, loc='best', **kwargs)
    return fig


def plot_tests_vs_cases(labels, dates, numbers,
                        suptitle='Muestras realizadas y casos positivos', **kwargs):
    samples = numbers[:, 0]
    cases = numbers[:, 1]

    fig: plt.Figure = plt.figure(suptitle, (13, 6))
    fig.suptitle(suptitle)

    n_days = len(dates)
    xs = np.arange(n_days)
    fig.gca().plot(xs, samples, label=labels[0], color='tab:green', lw=2)
    # fig.gca().plot(xs, samples.cumsum() / (xs + 1),color='tab:green', lw=1.5, ls=':')
    fig.gca().plot(xs, cases, label=labels[1], color='tab:red', lw=2)

    common_style_settings(fig, dates, n_days, samples.max(), '',
                          format_func=lambda x, p: f'{x*1e-3:1.0f} mil' if x > 0 else '', auto_y=2,
                          legend=True, **kwargs)

    return fig


def plot_tests_positivity(labels, dates, numbers, suptitle='Positividad de muestras', **kwargs):
    samples = numbers[:, 0]
    cases = numbers[:, 1]

    fig: plt.Figure = plt.figure(suptitle, (13, 6))
    fig.suptitle(suptitle)

    n_days = len(dates)
    xs = np.arange(n_days)
    positives = np.round(cases / samples * 100, 2)
    fig.gca().plot(xs, positives, label=labels[0], color='tab:red', lw=2)
    # fig.gca().plot(xs, positives.cumsum() / (xs + 1), color='tab:red', lw=1.5, ls=':')

    common_style_settings(fig, dates, n_days, positives.max(), '',
                          format_func=lambda x, p: f'{x:1.1f} %' if x > 0 else '', auto_y=2,
                          legend=False, loc='upper left', **kwargs)
    return fig


def report_situation(filename, daily_labels=None, deaths_labels=None,
                     images_path=None, show=True):
    column_labels, dates, numbers = read_data_file(filename)
    labels = column_labels[2:4] if not daily_labels else daily_labels
    fig_daily_full = plot_daily_cases(labels, dates, numbers[:, 1:3], span=28)
    n = 90
    fig_daily_last = plot_daily_cases(labels[-n:], dates[-n:], numbers[-n:, 1:3],
                                      f'Casos diarios y activos (últimos {n} días)',
                                      loc='best', span=7)

    fig_accum = plot_accumulated_cases(dates, numbers[:, 3])

    labels = column_labels[5:7] if not deaths_labels else deaths_labels
    fig_deaths = plot_daily_deaths(labels, dates, numbers[:, 4:6])

    fig_condition = plot_condition_vs_actives(column_labels[[5, 7, 8]],
                                              dates[-n:], numbers[-n:, [1, 4, 6, 7]],
                                              f'Porciento de seriedad en casos diarios (últimos {n} días)',
                                              span=7)
    fig_tests = plot_tests_vs_cases(column_labels[[1, 2]], dates[-n:], numbers[-n:, :2],
                                    f'Muestras realizadas y casos positivos (últimos {n} días)',
                                    span=7, loc='best')
    fig_positivity = plot_tests_positivity(column_labels[[1, 2]], dates[-n:], numbers[-n:, :2],
                                           f'Positividad de muestras (últimos {n} días)',
                                           span=7)

    if images_path:
        images_path = pathlib.Path(images_path)
        fig_daily_full.savefig(images_path / 'cov-Casos_activos.png')
        fig_daily_last.savefig(images_path / 'cov-Casos_activos_reciente.png')
        fig_accum.savefig(images_path / 'cov-Casos_acumulados.png')
        fig_deaths.savefig(images_path / 'cov-Fallecidos_acumulados.png')
        fig_condition.savefig(images_path / 'cov-Condicion_casos_recientes.png')
        fig_tests.savefig(images_path / 'cov-Muestras_recientes.png')
        fig_positivity.savefig(images_path / 'cov-Positividad_recientes.png')

    if show:
        plt.show()

    plt.close('all')


if __name__ == '__main__':
    DAILY_LABELS = ['Casos diarios', 'Activos']
    DEATHS_LABELS = ['Fallecidos diarios', 'Acumulado']
    report_situation('cases.txt',
                     daily_labels=DAILY_LABELS,
                     deaths_labels=DEATHS_LABELS,
                     images_path='./',
                     show=False)
