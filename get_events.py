import requests
import time
import json
import os

query_fmt = '''
query Q {
  search(query: "is:issue repo:%s/%s state:closed label:bug sort:created-desc", type: ISSUE, first: 100, %s) {
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

token = 'e7b88caf360ac34565c1553aed10676037395c54'
work_dir = "/home/repos"
# res_dir = "/Users/tannpopo/Documents/Study/ChangeLint/stats/events"
res_dir = "/home/yuailun/bug_introducing_commits"


def getQuery(owner, repo_name, after):
    return query_fmt % (owner, repo_name, after)


def getEventsOf(owner, repo_name):
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
            commits = event['node']['timelineItems']['nodes']
            if commits != []:
                for commit in commits:
                    commit_ = commit['commit']
                    if commit_ is None:
                        continue
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
    if evt_cnt != 0:
        with open(os.path.join(res_dir, repo_name + "_issue.json"), "w") as fd:
            fd.write(json.dumps(referencePairs, indent=2))
            with open("evet_list", "a") as list_fd:
                list_fd.write("{} {}\n".format(owner, repo_name))

    return evt_cnt


def allRepos():
    all_cnt = 0
    repo_list = "/home/yuailun/repo_list"
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