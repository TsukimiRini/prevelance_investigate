import requests
import time
import json
import os
from git.repo import Repo
import re
import sys

query_fmt = '''
query Q {
  search(query: "repo:%s/%s state:closed label:bug sort:created-desc", type: ISSUE, first: 100, %s) {
    issueCount
    pageInfo {
      endCursor
      hasNextPage
    }
    edges {
      cursor
      node {
        ... on Issue {
          url
          number
          createdAt
          closedAt
          labels(first:100) {
            edges{
              node{
                name
              }
            }
          }
          timelineItems(first: 100, itemTypes: REFERENCED_EVENT) {
            nodes {
              ... on ReferencedEvent {
                commit {
                  message
                  url
                  committedDate
                  oid
                }
              }
            }
          }
        }
      }
    }
  }
}
'''

token = sys.argv[1]
work_dir = sys.argv[2]
res_dir = sys.argv[3]
repo_list = sys.argv[4]


def getQuery(owner, repo_name, after):
    return query_fmt % (owner, repo_name, after)


def getEventsOf(owner, repo_name):
    fix_commits = []
    # res = requests.get("https://api.github.com/repos/{}/{}/events".format(owner, repo_name))
    referencePairs = {}
    after = ""
    id = 0
    evt_cnt = 0
    while True:
        request = requests.post(
            'https://api.github.com/graphql',
            json={'query': getQuery(owner, repo_name, after)},
            headers={"Authorization": "Bearer %s" % token})
        result = request.json()
        # result = json.dumps(result['data'], indent=2)
        # with open("repo_name_" + str(id), "w") as fd:
        #     fd.write(result)
        #     break

        if 'errors' in result:
            print(result)
            return 1

        search = result['data']['search']
        edges = search['edges']

        for event in edges:
            if len(event['node']) == 0:
                continue
            commits = event['node']['timelineItems']['nodes']
            if commits != []:
                for commit in commits:
                    commit_ = commit['commit']
                    if commit_ is None:
                        continue
                    if 'fix' in commit_['message']:
                        fix_commits.append(commit_['oid'])
                    referencePairs[event['node']['number']] = {
                        "creationdate":
                        event['node']['createdAt'].replace('T', " ").replace(
                            'Z', " +0000"),
                        "resolutiondate":
                        event['node']['closedAt'].replace('T', " ").replace(
                            'Z', " +0000"),
                        "hash":
                        commit_['oid'],
                        "commitdate":
                        commit_['committedDate'].replace('T', " ").replace(
                            'Z', " +0000"),
                    }
                    evt_cnt += 1

        # print("Issue count:", search['issueCount'], "number of edges:",
        #       len(search['edges']))

        # print("PageInfo:", search['pageInfo'], "cursor:",
        #       search['edges'][-1]['cursor'], "\n")

        if not search['pageInfo']['hasNextPage']:
            print("{}/{} done with {} commits, issue count {}".format(
                owner, repo_name, evt_cnt, search['issueCount']))
            break

        after = 'after: "%s"' % search['edges'][-1]['cursor']
        time.sleep(1)
        id += 1

    repo = Repo(os.path.join(work_dir, owner + '-' + repo_name))
    commits = list(repo.iter_commits())
    for idx, commit in enumerate(commits):
        if 'fix' in commit.message and str(commit) not in fix_commits:
            res = re.search(r'[+-]\d{2}:', str(commit.committed_datetime))
            referencePairs[str(commit)] = {
                "creationdate":
                str(commit.committed_datetime)[:res.start()] + " +0000",
                "resolutiondate":
                str(commit.committed_datetime)[:res.start()] + " +0000",
                "hash":
                str(commit),
                "commitdate":
                str(commit.committed_datetime)[:res.start()] + " +0000",
            }
            evt_cnt += 1
    print("{}/{} find {} fix commits in total".format(owner, repo_name,
                                                      evt_cnt))
    if evt_cnt != 0:
        with open(os.path.join(res_dir, repo_name + "_issue.json"), "w") as fd:
            fd.write(json.dumps(referencePairs, indent=2))
            with open("evet_list", "a") as list_fd:
                list_fd.write("{} {}\n".format(owner, repo_name))

    return evt_cnt


def allRepos():
    all_cnt = 0
    fd = open("evet_list", "w")
    fd.close()
    with open(repo_list) as list_fd:
        json_obj = json.load(list_fd)
        assert (len(json_obj) == 100)
        for repo in json_obj:
            assert (os.path.exists(
                os.path.join(work_dir,
                             repo["owner"]["login"] + "-" + repo["name"])))
            all_cnt += getEventsOf(repo['owner']['login'], repo['name'])

    print("all repos done, {} commits found".format(all_cnt))


allRepos()
# getEventsOf('TeamNewPipe', "NewPipe")