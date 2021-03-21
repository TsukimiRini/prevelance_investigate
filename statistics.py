import os
from git.repo import Repo
import json
import xlwt

# work_dir = "/Users/tannpopo/Documents/Study/ChangeLint/repos"
# work_dir = "/Users/tannpopo/Projects"
work_dir = "/home/repos"
row = 0
wb = xlwt.Workbook(encoding='utf-8')
newsheet = wb.add_sheet('sheet1', cell_overwrite_ok=True)
newsheet.write(row, 0, "repo_name")
newsheet.write(row, 1, "stars")
newsheet.write(row, 2, "total")
newsheet.write(row, 3, "cross")
newsheet.write(row, 4, "percent")


def check(repo_obj):
    global row

    repo_name = repo_obj["owner"]["login"] + "-" + repo_obj["name"]
    # print("="*8, "start to check repo ", repo_name, "="*8)
    commit_total = 0
    commit_cross = 0
    percent = 0

    repo = Repo(os.path.join(work_dir, repo_name))
    commits = list(repo.iter_commits())
    commit_total = len(commits)
    for idx, commit in enumerate(commits):
        xml_cnt = 0
        kot_jav_cnt = 0

        # if idx == len(commits)-1:
        for file in list(commit.stats.files):
            if len(file) > 4 and file[-4:] == '.xml':
                xml_cnt += 1
            elif len(file) > 3 and file[-3:] == '.kt' or len(
                    file) > 5 and file[-5:] == '.java':
                kot_jav_cnt += 1
        if xml_cnt >= 1 and kot_jav_cnt >= 1:
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

    # excel
    row += 1
    formula = 'HYPERLINK("{}", "{}")'.format(repo_obj["html_url"], repo_name_full)
    newsheet.write(row, 0, xlwt.Formula(formula))
    newsheet.write(row, 1, repo_obj["stargazers_count"])
    newsheet.write(row, 2, commit_total)
    newsheet.write(row, 3, commit_cross)
    newsheet.write(row, 4, percent)
    res = "{} Total: {}, Cross: {}, Percent: {}".format(
        repo_name_full, commit_total, commit_cross, percent)
    print(res)
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
    wb.save('stats_res.xlsx')


allRepos()