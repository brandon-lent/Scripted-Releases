import os
import re
from github import Github
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Iterate over environment variable# Step 1: Setup Github API instance and retrieve repo
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

# Step 4: Generate release title with current date
current_date = datetime.now().strftime('%Y-%m-%d')

# Step 5: Provide release details
release_tag = next_tag
release_title = f'{current_date} - Pre-Release'
release_body = 'Description of release'
draft = False

# Step 6: Create new release
release = repo.create_git_release(release_tag, release_title, release_body, draft=draft)
