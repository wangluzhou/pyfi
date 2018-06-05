import matplotlib.pyplot as plt
import matplotlib as mpl


def init():
    mpl.rcParams["axes.unicode_minus"] = False
    plt.rcParams["font.sans-serif"] = ["SimHei"]
    plt.rcParams["axes.unicode_minus"] = False


def line_graph(series_list, title, legend_list):
    """df_list的时间轴得一样"""
    init()
    fig = plt.figure(figsize=(16, 6))
    ax = plt.subplot(111)
    ax.set_title(title, fontsize=18)
    ax.grid(axis="both", linestyle='--')
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(True)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.tick_params(axis='both', labelsize=16)
    ax_list = [{}] * len(series_list)
    for i in range(len(series_list)):
        ax.plot(series_list[i].index.values, series_list[i].values, lw=2., linestyle="-")
    ax.legend(legend_list, fontsize=16, loc=1)
    fig.savefig(title + ".jpg")


def double_lines(series1, series2, lgd1="First", lgd2="Second", title="", colors=["r", "c"], figname=""):
    """快速画出双线对比图"""
    init()
    fig = plt.figure(figsize=(16, 9))
    ax1 = plt.subplot(111)
    ax1.set_title(title, fontsize=18)
    ax1.grid(axis="both", linestyle='--')
    ax1.spines["top"].set_visible(False)
    ax1.spines["bottom"].set_visible(True)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_visible(True)
    ax1.tick_params(axis='both', labelsize=16)
    ax1.plot(series1.index.values, series1.values, color=colors[0])
    ax1.legend([lgd1], fontsize=16, loc=1)
    ax2 = ax1.twinx()
    ax2.plot(series2.index.values, series2.values, color=colors[1])
    ax2.legend([lgd2], fontsize=16, loc=2)
    ax2.tick_params(axis='both', labelsize=16)
    if figname is not "":
        fig.savefig(figname)
    plt.show()
