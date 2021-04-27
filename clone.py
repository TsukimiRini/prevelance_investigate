import os
from git.repo import Repo
from git import rmtree
import git
import json
import requests
import sys

work_dir = sys.argv[1]
json_file_pos = sys.argv[2]

app_cnt = 0
repos_coll = []


def cloneRepos(json_file):
    global app_cnt
    download_path = os.path.join(work_dir, "repos")
    with open(os.path.join(work_dir, json_file)) as json_fd:
        load_dict = json.load(json_fd)
        for idx, item in enumerate(load_dict["items"]):
            if app_cnt == 100:
                print(8 * '=', "100 application cloned", 8 * '=')
                return
            clone_url = item["clone_url"]
            name = item["full_name"]
            author = item["owner"]["login"]
            repo_name = author + "-" + item["name"]
            if os.path.exists(
                    os.path.join(work_dir, json_file_pos + "not_app_list")):
                with open(
                        os.path.join(work_dir, json_file_pos + "not_app_list"),
                        'r+') as not_app_list:
                    lines = [line.strip() for line in not_app_list.readlines()]
                    found = False
                    for line in lines:
                        if line == repo_name.strip():
                            found = True
                            break
                if found:
                    continue
            if os.path.exists(os.path.join(download_path, repo_name)) is False:
                Repo.clone_from(clone_url,
                                to_path=os.path.join(download_path, repo_name))
            if os.path.exists(os.path.join(download_path, repo_name, "app")):
                print("repo {} cloned".format(name))
                app_cnt += 1
                repos_coll.append(item)
                # with open(os.path.join(work_dir, json_file_pos + "repo_list"),
                #           'w') as repo_list:
                #     repo_list.write(repo_name + "\n")
            else:
                with open(
                        os.path.join(work_dir, json_file_pos + "not_app_list"),
                        'a') as not_app_list:
                    not_app_list.write(repo_name + "\n")
                rmtree(os.path.join(download_path, repo_name))
                cmd = "rm -rf " + os.path.join(download_path, repo_name)
                os.system(cmd)
                print("repo {} added to blacklist".format(repo_name))


def ifRepoIsApp(repo_name):
    url = "https://api.github.com/search/code?q=path:/app repo:" + repo_name + "&access_token=31bc0a7a8417052bfeeba0913a080547a94937fc"
    header = {'Accept': "application/vnd.github.mercy-preview+json"}
    res = requests.get(url, headers=header)
    res = json.loads(res.text)
    print("{} is being checked".format(repo_name))
    try:
        if len(res["items"]) == 0:
            return False
    except:
        print(res)
    else:
        print("repo {} is an app".format(repo_name))
    return True


class Progress(git.remote.RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        res = "update({}, {}, {}, {})".format(op_code, cur_count, max_count,
                                              message)
        print(res)


for i in range(10):
    page = i + 1
    json_file = json_file_pos + "android-java-repo-p" + str(page)
    cloneRepos(json_file)
    if app_cnt >= 100:
        repo_dump = json.dumps(repos_coll)
        with open(os.path.join(work_dir, json_file_pos + "repo_list"),
                  'w') as repo_list:
            repo_list.write(repo_dump)
        break

# ifRepoIsApp("CymChad/BaseRecyclerViewAdapterHelper")
