import os
import re
from github import Github
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Step 1: Setup Github API instance and retrieve repo
access_token = os.getenv("ACCESS_TOKEN")
g = Github(access_token)
repo = g.get_repo("brandon-lent/Scripted-Releases-Test")

# Step 2: Get the latest release
latest_release = repo.get_latest_release()
latest_tag = latest_release.tag_name

# Step 3: Extract the version number and increment it
version_number = re.findall(r'\d+', latest_tag)
next_version_number = int(version_number[0]) + 1
next_tag = f'portal/v{next_version_number}.0.0-rc1'

print(next_tag)

# Step 4: Create new release branch
new_branch = f'release/portal/-v{next_version_number}.0.0'
try:
    repo.create_git_ref(ref=f'refs/heads/{new_branch}', sha=repo.get_branch('main').commit.sha)
except Exception as e:
    print("Failed to create new branch as it already exists")
    raise ValueError(f"Failed to create new branch {new_branch}: {str(e)} as it already exists")


# Step 5: Generate release title with current date
current_date = datetime.now().strftime('%Y-%m-%d')

# Step 6: Grab pull requests related to this change and append to release body
pull_requests = repo.get_pulls(base='main', state='closed', sort='created', direction='desc')
release_notes_from_pull_requests = "## Release Notes: \n"

for pr in pull_requests:
    pr_title = pr.title
    pr_url = pr.html_url
    release_notes_from_pull_requests += f"- {str.capitalize(pr_title)} {pr_url} \n"
    print(release_notes_from_pull_requests)


# Step 6: Provide release details
release_tag = next_tag
release_title = "test"
release_body = release_notes_from_pull_requests
draft = False


# Step 7: Attempt to create new release
release = repo.create_git_release(release_tag, release_title, release_body, draft=draft, target_commitish=new_branch)
release_url = release.html_url
print("📝 Release Notes can be found here: " + release_url)




