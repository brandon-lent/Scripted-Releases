import os
import re
from github import Github
from git import Repo
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
next_tag = f'v{next_version_number}.0.0'

# Step 4: Create new release branch
new_branch = f'pre-release-{next_version_number}'
repo.create_git_ref(ref=f'refs/heads/{new_branch}', sha=repo.get_branch('main').commit.sha)

# Step 5: Generate release title with current date
current_date = datetime.now().strftime('%Y-%m-%d')

# Step 6: Provide release details
release_tag = next_tag
release_title = f'{current_date} - Pre-Release'
release_body = 'Description of release'
draft = False


# Step 7: Create new release
release = repo.create_git_release(release_tag, release_title, release_body, draft=draft, target_commitish=new_branch)
release_url = release.html_url

print("📝 Release Notes can be found here: " + release_url)
