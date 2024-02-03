# -*- coding: utf-8 -*-
import os
from github import Github, GithubException
from dotenv import load_dotenv
from enum import Enum

from scripted_release_utils import (
    increment_release_tag_and_branch_from_version,
    get_latest_release_tag,
    get_latest_release_branch,
    increment_release_candidate_tag,
    ReleaseLog,
    drop_release_candidate_string,
    is_valid_commit_hash,
    cherry_pick_commits,
)

load_dotenv()

# Specifies the naming convention of the release. Ex: "release/portal/v1.0.0"
RELEASE_NAME = "portal"


# Maps to the release action env variable which is defined by a GitHub action dropdown that runs this script
class ReleaseAction(Enum):
    CREATE_RELEASE = "Create release"
    UPDATE_RELEASE = "Update release"
    FINALIZE_RELEASE = "Finalize release"
    HOTFIX = "Hotfix"


# Setup GitHub API instance and retrieve repo
access_token = os.getenv("GITHUB_TOKEN")
repo_name = os.getenv("GITHUB_REPOSITORY")
g = Github(access_token)
repo = g.get_repo(repo_name)

# Log items to file
release_logger = ReleaseLog("release_log.txt")


def create_release():
    release_version = os.getenv("RELEASE_VERSION")

    try:
        latest_release_tag = get_latest_release_tag(RELEASE_NAME, repo)
    except ValueError:
        print(
            "No matching release pattern found. Attempting to create the first release via script."
        )
        latest_release_tag = None

    if not latest_release_tag:
        # Create a base release, tag, and branch if no release exists in repository. This should only run once.
        new_branch = repo.create_git_ref(
            f"refs/heads/release/{RELEASE_NAME}/v0.1.0",
            repo.get_branch("main").commit.sha,
        )

        release_naming_pattern = f"{RELEASE_NAME}/v0.1.0-rc1"
        new_release = repo.create_git_release(
            name=release_naming_pattern,
            tag=release_naming_pattern,
            draft=False,
            message="🎉 This is the first release! 🎉",
            target_commitish=new_branch.object.sha,
            generate_release_notes=True,
        )

    else:
        new_tag, new_branch = increment_release_tag_and_branch_from_version(
            latest_release_tag.name, release_version, RELEASE_NAME
        )

        try:
            repo.create_git_ref(
                ref=f"refs/heads/{new_branch}", sha=repo.get_branch("main").commit.sha
            )
        except Exception as e:
            # If this occurs, it is most likely a reference error, such as the branch/tag already existing.
            raise ValueError(f"❌ Failed to create new branch {new_branch}: {str(e)}")

        # Provide release details
        release_tag = new_tag
        release_title = release_tag
        draft = False

        # Attempt to create new release
        new_release = repo.create_git_release(
            release_tag,
            release_title,
            draft=draft,
            message="",
            target_commitish=new_branch,
            generate_release_notes=True,
        )

    release_logger.append_release_line(
        f"📝 **Release Notes can be found here:** {new_release.html_url}"
    )


def update_release():
    commit_hashes_input = os.getenv("COMMIT_HASHES").strip()

    # Get relevant Github details
    latest_tag = get_latest_release_tag(RELEASE_NAME, repo)
    latest_release_branch = get_latest_release_branch(RELEASE_NAME, repo)
    incremented_tag = increment_release_candidate_tag(latest_tag.name)

    if commit_hashes_input:
        # List of inputted commit hashes
        commit_hashes = [
            commit_hash.strip() for commit_hash in commit_hashes_input.split(",")
        ]
        # List of invalid commit hashes
        invalid_hashes = [
            commit_hash
            for commit_hash in commit_hashes
            if not is_valid_commit_hash(commit_hash, repo)
        ]
        if invalid_hashes:
            raise ValueError(f"Invalid commit hashes provided: {invalid_hashes}")

        # Create a temporary branch to cherry-pick commits, based on the latest release branch
        temp_branch_name = f"temp-{incremented_tag}"
        repo.create_git_ref(ref=f"refs/heads/{temp_branch_name}", sha=repo.get_branch(latest_release_branch).commit.sha)

        # Cherry-pick commits to release branch
        cherry_pick_commits(commit_hashes, temp_branch_name)

        # Create a new git tag and ref using the new latest_release_branch
        newly_created_tag = repo.create_git_tag(
            incremented_tag,
            f"Release Candidate tag {incremented_tag} created",
            repo.get_branch(temp_branch_name).commit.sha,
            type="commit",
        )

        ref = repo.create_git_ref(
            f"refs/tags/{newly_created_tag.tag}", sha=repo.get_branch(temp_branch_name).commit.sha,
        )

        try:
            repo.merge(
                latest_release_branch,
                ref.object.sha,
                "Merge changes from newly created (cherrypick)tag to release branch",
            )
        except GithubException as e:
            print(f"Merge unsuccessful. An error occurred: {str(e)}")
        finally:
            print(f"Deleting temporary branch {temp_branch_name}")
            # repo.get_branch(temp_branch_name).delete()

    else:
        # Get the latest release branch object
        branch = repo.get_branch(latest_release_branch)
        # Attempt to create a new git tag, ref, and merge changes
        main_branch = repo.get_branch("main")
        newly_created_tag = repo.create_git_tag(
            incremented_tag,
            f"Release Candidate tag {incremented_tag} created",
            main_branch.commit.sha,
            type="commit",
        )

        ref = repo.create_git_ref(
            f"refs/tags/{newly_created_tag.tag}", sha=main_branch.commit.sha
        )

        try:
            repo.merge(
                branch.name,
                ref.object.sha,
                "Merge changes from newly created tag to release branch",
            )
        except GithubException as e:
            print(f"Merge unsuccessful. An error occurred: {str(e)}")

    compare_tags_url = f"{repo.html_url}/compare/{latest_tag.name}...{incremented_tag}"
    release_logger.append_release_line(f"🔗 **Tag Comparison:** {compare_tags_url}")


def finalize_release():
    latest_release_tag = get_latest_release_tag(RELEASE_NAME, repo)

    finalized_release_name = drop_release_candidate_string(latest_release_tag.name)

    # Get the latest GitTag object if name matches.
    tag = next(
        (tag for tag in repo.get_tags() if tag.name == latest_release_tag.name), None
    )

    new_release = repo.create_git_release(
        name=finalized_release_name,
        tag=finalized_release_name,
        draft=False,
        message="",
        target_commitish=tag.commit.sha,
        generate_release_notes=True,
    )

    release_logger.append_release_line(
        f"📝 **Release Notes can be found here:** {new_release.html_url}"
    )


def hotfix():
    # To be implemented in #3316
    print("\n🚀 Starting scripted releases 'hotfix' action")
    pass


release_action = os.getenv("RELEASE_ACTION")

release_logger.append_release_line(
    f"\n🏁 Started scripted release using release action: {release_action} 🏁"
)

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
