import os
import json

from github import Github, UnknownObjectException

def main():
    """
    Small helper script used to update to latest releases
    of corpus repos.

    If releases are not found, defaults to the last commit
    on `master`.
    """
    ACCESS_TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN", "")
    if ACCESS_TOKEN:
        client = Github(ACCESS_TOKEN)
    else:
        client = Github()


    status = []
    corpus = json.load(open("corpus.json"))
    for repo_name, sha in corpus.items():
        diff_url = ""
        repo = client.get_repo(repo_name)
        try:
            latest_release = repo.get_latest_release()
            latest_commit_sha = latest_release.target_commitish
            if latest_commit_sha == repo.default_branch:
                default_branch = repo.get_branch(repo.default_branch)
                latest_commit_sha = default_branch.commit.sha
        except UnknownObjectException:
            print(f'{repo_name} has no release data.  retreiving latest SHA from "{repo.default_branch}"')
            default_branch = repo.get_branch(repo.default_branch)
            latest_commit_sha = default_branch.commit.sha
        should_update = latest_commit_sha != sha
        if should_update:
            compared = repo.compare(sha, latest_commit_sha)
            diff_url = compared.html_url
        status.append([
            repo.full_name,
            should_update,
            sha,
            latest_commit_sha,
            diff_url,
        ])

    new_corpus = dict()
    for row in status:
        new_corpus[row[0]] = row[3]
    json.dump(new_corpus, open("corpus.json", "w"), indent=2)


if __name__ == "__main__":
    main()
