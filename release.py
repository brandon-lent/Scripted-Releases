import os
import re
from github import Github
from dotenv import load_dotenv
from datetime import datetime
from enum import Enum

load_dotenv()

# Maps to the release action env variable which is ultimately defined by a GitHub action dropdown
class ReleaseAction(Enum):
    CREATE_RELEASE = "Create release"
    UPDATE_RELEASE = "Update release"
    FINALIZE_RELEASE = "Finalize release"


def create_release():
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

    # Step 4: Create new release branch
    new_branch = f'release/portal/v{next_version_number}.0.0'
    try:
        repo.create_git_ref(ref=f'refs/heads/{new_branch}', sha=repo.get_branch('main').commit.sha)
    except Exception as e:
        raise ValueError(f"❌ Failed to create new branch {new_branch}: {str(e)}")


    # Step 5: Generate release title with current date
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Step 6: Grab pull requests related to this change and append to release body
    pull_requests = repo.get_pulls(base='main', state='closed', sort='created', direction='desc')
    release_notes_from_pull_requests = "## Release Notes: \n"

    for pr in pull_requests:
        pr_title = pr.title
        pr_url = pr.html_url
        release_notes_from_pull_requests += f"- {str.capitalize(pr_title)} {pr_url} \n"


    # Step 6: Provide release details
    release_tag = next_tag
    release_title = "test"
    release_body = release_notes_from_pull_requests
    draft = False


    # Step 7: Attempt to create new release
    release = repo.create_git_release(release_tag, release_title, release_body, draft=draft, target_commitish=new_branch)
    release_url = release.html_url
    print(f"✅ Created new branch: {new_branch}")
    print(f"✅ Created new tag: {next_tag}")
    print("------")
    print("📝 Release Notes can be found here: " + release_url)


def update_release():
    # Step 1: Setup Github API instance and retrieve repo
    access_token = os.getenv("ACCESS_TOKEN")
    g = Github(access_token)
    repo = g.get_repo("brandon-lent/Scripted-Releases-Test")

    # Step 2: Get the latest release
    latest_release = repo.get_latest_release()
    latest_tag = latest_release.tag_name

    # Step 3: Extract the version number
    version_number = re.findall(r'\d+', latest_tag)
    next_version_number = int(version_number[0]) + 1

    # # Increment the RC number by 1
    next_rc_number = int(latest_tag[-1]) + 1
    print(next_rc_number)

    # Step 4: Create new release candidate branch
    release_branch = f'release/portal-v{next_version_number}.0.0'
    try:
        repo.create_git_ref(ref=f'refs/heads/{release_branch}', sha=latest_release.target_commitish)
    except Exception as e:
        print("Failed to create new branch as it already exists")
        raise ValueError(f"Failed to create new branch {release_branch}: {str(e)} as it already exists")

    # Step 5: Merge code changes to the release candidate branch
    main_branch = repo.get_branch('main')
    repo.merge(main_branch.commit.sha, release_branch)

    # Step 6: Create new tag for the release candidate
    rc_tag = f'portal/v{next_version_number}.0.0-rc{next_rc_number}'
    repo.create_git_tag_and_release(
        tag=rc_tag,
        tag_message="Release candidate for version {next_version_number}.0.0",
        release_name=f"Release Candidate {next_version_number}.0.0",
        release_message="Release candidate for the upcoming version",
        object=repo.get_branch(release_branch).commit.sha,
        type="commit"
    )

    print(f"🔄 Code changes merged into the release candidate branch: {release_branch}")
    print(f"🏷️ Release candidate tag created: {rc_tag}")

def finalize_release():
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
else:
    raise ValueError("No release action selected. Action aborted.")


