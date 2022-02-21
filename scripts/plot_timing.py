DESC='''Timing plots

By AA
'''

import logging
import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib.ticker import AutoMinorLocator
import matplotlib.ticker as mticker
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import numpy as np
import pandas as pd
from pdb import set_trace
import re
import seaborn as sns
import sqlite3
import sys

import plot

FORMAT="%(levelname)s:%(funcName)s:%(message)s"
INFINITY=100000000

# global options

fontSize=plot.FONT_TABLE['17']

rc('font', size=fontSize['small'])          # controls default text sizes
rc('axes', titlesize=fontSize['Large'])     # fontsize of the axes title
rc('axes', labelsize=fontSize['Large'])    # fontsize of the x and y labels
rc('xtick', labelsize=fontSize['small'])    # fontsize of the tick labels
rc('ytick', labelsize=fontSize['small'])    # fontsize of the tick labels
rc('legend', fontsize=fontSize['large'])    # legend fontsize
rc('figure', titlesize=fontSize['Large'])  # fontsize of the figure title
rc('text',usetex=True)
rc('font',**{'family':'serif','serif':['Computer Modern Roman']})

pd.options.display.float_format = '{:.10g}'.format

def n_vs_time(df, threshold_interval):
    # initiate plots
    fig = plot.initiate_plot(24,6)
    gs = plot.subplot_grids(fig,1,3)
    fig.suptitle(f'Threshold interval $\\theta={threshold_interval}$')

    ax = fig.add_subplot(gs[0,0])
    plot.set_plot_theme(ax)
    plot.set_grid(ax)
    plot.set_minor_tics(ax)

    sns.lineplot(data = df[df.interval==threshold_interval],
            x='nodes',
            y='time',
            palette = plot.MATHEMATICA[0:3],
            hue='Edge probability',
            ax=ax
            )

    ax.set_xlabel('Number of nodes $n$')
    ax.set_ylabel('Time (seconds)')

    #ax.legend(bbox_to_anchor=[1.05,1],frameon=False)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ## ymax=ax.get_yticks()[-1]
    ## ax.set_ylim([0,ymax])

    # per query plot
    ax = fig.add_subplot(gs[0,1])
    plot.set_plot_theme(ax)
    plot.set_grid(ax)
    plot.set_minor_tics(ax)

    sns.lineplot(data = df[df.interval==threshold_interval],
            x='nodes',
            y='time_query',
            palette = plot.MATHEMATICA[0:3],
            hue='Edge probability',
            ax=ax
            )

    ax.set_xlabel('Number of nodes $n$')
    ax.set_ylabel('Time/query (seconds)')

    ax.set_xscale('log')
    ax.set_yscale('log')
    ## ymax=ax.get_yticks()[-1]
    ## ax.set_ylim([0,ymax])

    # number of queries
    ax = fig.add_subplot(gs[0,2])
    plot.set_plot_theme(ax)
    plot.set_grid(ax)
    plot.set_minor_tics(ax)

    sns.lineplot(data = df[df.interval==threshold_interval],
            x='nodes',
            y='queries',
            palette = plot.MATHEMATICA[0:3],
            hue='Edge probability',
            ax=ax
            )

    ax.set_xlabel('Number of nodes $n$')
    ax.set_ylabel('Number of queries')

    ax.set_xscale('log')
    ax.set_yscale('log')
    plt.savefig('n_vs_time.pdf',bbox_inches='tight')
    return

def theta_vs_time(df, nodes):
    # initiate plots
    fig = plot.initiate_plot(24,6)
    gs = plot.subplot_grids(fig,1,3)
    fig.suptitle(f'Number of nodes $n={nodes}$')

    ax = fig.add_subplot(gs[0,0])
    plot.set_plot_theme(ax)
    plot.set_grid(ax)
    plot.set_minor_tics(ax)

    sns.lineplot(data = df[df.nodes==nodes],
            x='interval',
            y='time',
            palette = plot.MATHEMATICA[0:3],
            hue='Edge probability',
            ax=ax
            )

    ax.set_xlabel('Threshold interval $\\theta$')
    ax.set_ylabel('Time (seconds)')

    ax.set_yscale('log')
    ## ymax=ax.get_yticks()[-1]
    ## ax.set_ylim([0,ymax])

    # per query plot
    ax = fig.add_subplot(gs[0,1])
    plot.set_plot_theme(ax)
    plot.set_grid(ax)
    plot.set_minor_tics(ax)

    sns.lineplot(data = df[df.nodes==nodes],
            x='interval',
            y='time_query',
            palette = plot.MATHEMATICA[0:3],
            hue='Edge probability',
            ax=ax
            )

    ax.set_xlabel('Threshold interval $\\theta$')
    ax.set_ylabel('Time/query (seconds)')

    #ax.legend(bbox_to_anchor=[1.05,1],frameon=False)
    ax.set_yscale('log')
    ## ymax=ax.get_yticks()[-1]
    ## ax.set_ylim([0,ymax])

    # number of queries
    ax = fig.add_subplot(gs[0,2])
    plot.set_plot_theme(ax)
    plot.set_grid(ax)
    plot.set_minor_tics(ax)

    sns.lineplot(data = df[df.nodes==nodes],
            x='interval',
            y='queries',
            palette = plot.MATHEMATICA[0:3],
            hue='Edge probability',
            ax=ax
            )

    ax.set_xlabel('Threshold interval $\\theta$')
    ax.set_ylabel('Number of queries')

    #ax.legend(bbox_to_anchor=[1.05,1],frameon=False)
    ax.set_yscale('log')
    plt.savefig('theta_vs_time.pdf',bbox_inches='tight')
    plt.clf()
    return


def main():
    conn = sqlite3.connect('../results/results.db')
    df = pd.read_sql('SELECT * FROM greedy_timing', conn)
    df['time'] = df.greedy_time + df.gsqrd_time
    df['time_query'] = df.time/df.queries
    df = df.rename(columns = {'probability': 'Edge probability'})
    n_vs_time(df, 0.5)
    theta_vs_time(df, 500)
    conn.close()

if __name__=='__main__':
    main()
