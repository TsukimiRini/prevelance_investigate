import os
from git.repo import Repo
import json
from sys import platform
import csv
import seaborn as sns
import pandas as pd

# work_dir = "/Users/tannpopo/Documents/Study/ChangeLint/repos"
# work_dir = "/Users/tannpopo/Projects"
if platform == "darwin":
    # work_dir = "/Users/tannpopo/Documents/Study/ChangeLint/repo"
    work_dir = "/Users/tannpopo/Projects"
    csv_dir = "../csv"
    plot_dir = "../plots"
elif platform == "linux":
    work_dir = "/home/repos"
    csv_dir = "/home/yuailun/plot_data"
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
    repo_list = "/home/yuailun/repo_list"
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


def drawPlot():
    sns.set_theme(style="ticks", palette="pastel")
    data = pd.read_csv(os.path.join(csv_dir, "multi-lang-percent.csv"))
    plot = sns.histplot(data=data, y="percentage", binwidth=10, binrange=(0, 80), color="#7a95c4")
    # plot.set_ylim(bottom=0)
    ylabels = ['{:,.0f}'.format(x) + '%' for x in plot.get_yticks()]
    plot.set_yticklabels(ylabels)
    plot.set(xlabel="Number of repositories", ylabel="Percentage of multi-lang commits")
    fig = plot.get_figure()
    fig.savefig(os.path.join(plot_dir, "multi-lang-percent.png"))


if platform == "linux":
    allRepos()
elif platform == "darwin":
    drawPlot()