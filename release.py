import os

from github import Github
from dotenv import load_dotenv
from enum import Enum

from scripted_releases_utils import generate_release_notes, increment_release_tag_and_branch_from_version

load_dotenv()


# Maps to the release action env variable which is defined by a GitHub action dropdown that runs this script
class ReleaseAction(Enum):
    CREATE_RELEASE = "Create release"
    UPDATE_RELEASE = "Update release"
    FINALIZE_RELEASE = "Finalize release"
    HOTFIX = "Hotfix"


# Setup GitHub API instance and retrieve repo
access_token = os.getenv("ACCESS_TOKEN")
repo_name = os.getenv("REPO_NAME")
g = Github(access_token)
print(repo_name)
repo = g.get_repo(repo_name)


def create_release():
    release_version = os.getenv("RELEASE_VERSION")

    latest_release = repo.get_latest_release()
    latest_tag = latest_release.tag_name
    next_tag, new_branch = increment_release_tag_and_branch_from_version(latest_tag, release_version)

    try:
        repo.create_git_ref(ref=f'refs/heads/{new_branch}', sha=repo.get_branch('main').commit.sha)
    except Exception as e:
        # If this occurs, it is most likely a reference error, such as the branch/tag already existing.
        raise ValueError(f"❌ Failed to create new branch {new_branch}: {str(e)}")

    # Grab pull requests related to this change and append to release body
    pull_requests = repo.get_pulls(base=latest_tag, head=next_tag, state='closed', sort='created', direction='desc')

    release_notes_from_pull_requests = generate_release_notes(pull_requests, repo)

    # Provide release details
    release_tag = next_tag
    release_title = f"portal/{release_tag}"
    release_body = release_notes_from_pull_requests
    draft = False

    # Attempt to create new release
    release = repo.create_git_release(release_tag, release_title, release_body, draft=draft,
                                      target_commitish=new_branch, generate_release_notes=True)
    release_url = release.html_url
    compare_release_url = f"{repo.html_url}/compare/{latest_release.tag_name}...{release.tag_name}"
    print(f"✅ Created new branch: {new_branch}")
    print(f"✅ Created new tag: {next_tag}")
    print(f"✅ Release Notes title: {release_title}")
    print("------")
    print("🔗 Release Notes: " + release_url)
    print("🔗 Tag Comparison: " + compare_release_url)

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
