import os
from textwrap import wrap
from git.repo import Repo
import json
import csv
import seaborn as sns
import pandas as pd
import sys
from matplotlib import pyplot
import numpy as np

if sys.argv[1] == "plot":
    csv_dir = "../csv"
    plot_dir = "../plots"
elif sys.argv[1] == "data":
    work_dir = sys.argv[2]
    csv_dir = "../csv"
    repo_list = sys.argv[3]
row = 0

commit_cnt = 0
changed_files_cnt = 0
all_commit_cnt = 0
all_changed_cnt = 0

percent_coll = []


def check(repo_obj):
    global row
    global commit_cnt
    global changed_files_cnt
    global all_commit_cnt
    global all_changed_cnt

    repo_name = repo_obj["owner"]["login"] + "-" + repo_obj["name"]
    # print("="*8, "start to check repo ", repo_name, "="*8)
    commit_total = 0
    commit_cross = 0
    percent = 0

    shas = set()
    repo = Repo(os.path.join(work_dir, repo_name))
    for b in repo.remote().fetch():
        if '/' not in b.name:
            continue
        print("start to check branch {} of {}".format(b.name, repo_name))
        branch_name = b.name.split('/')[1]
        repo.git.checkout('-B', branch_name, b.name)
        commits = list(repo.iter_commits())
        for idx, commit in enumerate(commits):
            if str(commit) in shas:
                continue
            else:
                shas.add(str(commit))
            if len(commit.parents) > 1:
                continue
            commit_total += 1
            xml_cnt = 0
            kot_jav_cnt = 0
            all_commit_cnt += 1

            # if idx == len(commits)-1:
            file_list = list(commit.stats.files)
            all_changed_cnt += len(file_list)
            for file in file_list:
                if len(file) > 4 and file[-4:] == '.xml':
                    xml_cnt += 1
                elif len(file) > 3 and file[-3:] == '.kt' or len(
                        file) > 5 and file[-5:] == '.java':
                    kot_jav_cnt += 1
            if xml_cnt >= 1 and kot_jav_cnt >= 1:
                commit_cnt += 1
                changed_files_cnt += len(file_list)
                commit_cross += 1
        #     break
        # diff_index = commit.diff(commits[idx+1])

        # for diff_item in diff_index:
        #     if diff_item.a_path[-4:] == '.xml':
        #         xml_cnt += 1
        #     elif diff_item.a_path[-3:] == '.kt' or diff_item.a_path[-5:] == '.java':
        #         kot_jav_cnt += 1
        # if xml_cnt >= 1 and kot_jav_cnt >= 1:
        #     commit_cross += 1

    percent = float(commit_cross) / commit_total
    repo_name_full = repo_obj["full_name"]

    res = "{} Total: {}, Cross: {}, Percent: {}".format(
        repo_name_full, commit_total, commit_cross, percent)
    print(res)
    percent_coll.append((repo_obj["full_name"], percent * 100))
    # print("="*8, "check repo ", repo_name, "completed", "="*8)
    return commit_total, commit_cross, percent


def allRepos():
    with open(repo_list) as list_fd:
        json_obj = json.load(list_fd)
        assert (len(json_obj) == 100)
        for repo in json_obj:
            assert (os.path.exists(
                os.path.join(work_dir,
                             repo["owner"]["login"] + "-" + repo["name"])))
            check(repo)

    with open(os.path.join(csv_dir, "multi-lang-percent.csv"), "w",
              newline="") as fd:
        csv_writer = csv.writer(fd,
                                delimiter=',',
                                quotechar='"',
                                quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(["repo", "percentage"])
        for i in percent_coll:
            csv_writer.writerow([i[0], i[1]])


def show_values_on_bars(axs, h_v="v", space=0.4):
    def _show_on_single_plot(ax):
        if h_v == "v":
            for p in ax.patches:
                _x = p.get_x() + p.get_width() / 2
                _y = p.get_y() + p.get_height()
                value = int(p.get_height())
                ax.text(_x, _y, value, ha="center")
        elif h_v == "h":
            for p in ax.patches:
                _x = p.get_x() + p.get_width() + float(space)
                _y = p.get_y() + p.get_height() - 8
                value = int(p.get_width())
                if value == 0:
                    continue
                ax.text(_x, _y, value, ha="left")

    if isinstance(axs, np.ndarray):
        for idx, ax in np.ndenumerate(axs):
            _show_on_single_plot(ax)
    else:
        _show_on_single_plot(axs)


def drawPlot():
    sns.set_theme(style="ticks", palette="pastel")
    data = pd.read_csv(os.path.join(csv_dir, "multi-lang-percent.csv"))
    fig, ax = pyplot.subplots(figsize=(6, 3))
    plot = sns.histplot(data=data,
                        y="percentage",
                        binwidth=10,
                        binrange=(0, 90),
                        color="#7a95c4",
                        ax=ax)
    # plot.set(ymargin=3)
    # plot.set_ylim(bottom=0)
    plot.set_yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90])
    ylabels = ['{:,.0f}'.format(x) + '%' for x in plot.get_yticks()]
    plot.set_yticklabels(ylabels)
    plot.set_xlabel(xlabel="Number of repositories", fontsize=13, weight='bold', wrap=True)
    plot.set_ylabel(ylabel="Percentage of multi-lang commits", fontsize=13, weight='bold', wrap=True)
    show_values_on_bars(plot, 'h', 0.3)
    fig.tight_layout()
    fig.subplots_adjust(left=0.15)
    fig = plot.get_figure()
    fig.savefig(os.path.join(plot_dir, "multi-lang-percent.png"), dpi=300)


if sys.argv[1] == "data":
    allRepos()
elif sys.argv[1] == "plot":
    drawPlot()