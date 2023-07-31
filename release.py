
from github import Github
import os

# Using an access token
g = Github(os.getenv('GITHUB_TOKEN'))

# Then play with your Github objects:
repo = g.get_repo(os.getenv('REPO_NAME'))

tag = "v1.0.0"
release_name = "Release 1.0.0"
body = "This is the release description"
prerelease = False
draft = False

release = repo.create_git_release(tag, release_name, body, draft, prerelease)
