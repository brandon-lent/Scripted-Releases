import inspect
import os
import re
from datetime import datetime

from github import Github
from dotenv import load_dotenv
from enum import Enum

load_dotenv()


# Maps to the release action env variable which is defined by a GitHub action dropdown that runs this script
class ReleaseAction(Enum):
    CREATE_RELEASE = "Create release"
    UPDATE_RELEASE = "Update release"
    FINALIZE_RELEASE = "Finalize release"
    HOTFIX = "Hotfix"


# Maps the release version env variable which is defined by a GitHub action dropdown that runs this script
class ReleaseVersion(Enum):
    MAJOR = "Major"
    MINOR = "Minor"


# Setup GitHub API instance and retrieve repo
access_token = os.getenv("ACCESS_TOKEN")
repo_name = os.getenv("REPO_NAME")
g = Github(access_token)
print(repo_name)
repo = g.get_repo(repo_name)


def create_release():
    release_version = os.getenv("RELEASE_VERSION")

    # Get the latest release
    latest_release = repo.get_latest_release()
    latest_tag = latest_release.tag_name

    tag_version = re.findall(r'\d+', latest_tag)
    current_major_version = int(tag_version[0])
    current_minor_version = int(tag_version[1])

    if release_version == ReleaseVersion.MAJOR.value:
        next_tag = f'v{current_major_version + 1}.0.0-rc1'
        new_branch = f'release/portal/v{current_major_version + 1}.0.0'
    elif release_version == ReleaseVersion.MINOR.value:
        next_tag = f'v{current_major_version}.{current_minor_version + 1}.0-rc1'
        new_branch = f'release/portal/v{current_major_version}.{current_minor_version + 1}.0'
    else:
        raise ValueError("RELEASE_VERSION not set. Action aborted.")

    try:
        repo.create_git_ref(ref=f'refs/heads/{new_branch}', sha=repo.get_branch('main').commit.sha)
    except Exception as e:
        # If this occurs, it is most likely a reference error, such as the branch already existing.
        raise ValueError(f"❌ Failed to create new branch {new_branch}: {str(e)}")

    # Grab pull requests related to this change and append to release body
    pull_requests = repo.get_pulls(base='main', state='closed', sort='created', direction='desc')
    release_notes_from_pull_requests = "## Release Notes: \n"

    for pr in pull_requests:
        pr_title = pr.title
        pr_url = pr.html_url
        release_notes_from_pull_requests += f"- {str.capitalize(pr_title)} {pr_url} \n"

    # Provide release details
    release_tag = next_tag
    release_title = f"portal/{release_tag}"
    release_body = release_notes_from_pull_requests
    draft = False

    # Attempt to create new release
    release = repo.create_git_release(release_tag, release_title, release_body, draft=draft,
                                      target_commitish=new_branch)
    release_url = release.html_url
    print(f"✅ Created new branch: {new_branch}")
    print(f"✅ Created new tag: {next_tag}")
    print(f"✅ Release Notes title: {release_title}")
    print("------")
    print("📝 Release Notes can be found here: " + release_url)


def update_release():
    # To be implemented in #3314
    print("\n🚀 Starting scripted releases 'update_release' action")
    pass


def finalize_release():
    # To be implemented in #3315
    print("\n🚀 Starting scripted releases 'finalize_release' action")
    pass


def hotfix():
    # To be implemented in #3316
    print("\n🚀 Starting scripted releases 'hotfix' action")
    pass


release_action = os.getenv("RELEASE_ACTION")

print(f"\n🏁 Starting scripted release using release action: {release_action} 🏁")
print("------")

if release_action == ReleaseAction.CREATE_RELEASE.value:
    create_release()
elif release_action == ReleaseAction.UPDATE_RELEASE.value:
    update_release()
elif release_action == ReleaseAction.FINALIZE_RELEASE.value:
    finalize_release()
elif release_action == ReleaseAction.HOTFIX.value:
    hotfix()
else:
    raise ValueError("No release action selected. Action aborted.")
