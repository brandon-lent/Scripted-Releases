import re
from enum import Enum

from github import RateLimitExceededException


# Maps the release version env variable which is defined by a GitHub action dropdown that runs this script
class ReleaseVersion(Enum):
    MAJOR = "Major"
    MINOR = "Minor"


def increment_release_tag_and_branch_from_version(latest_tag, release_version):
    """
    Expected release tag format: v1.0.0

    A major version represents a significant release, such as a new feature. We denote this by incrementing the major value in a tag.
    Example: v1.0.0 -> v2.0.0

    A minor release represents a smaller release, such as our regularly deployments that don't include new features.
    Example: v1.0.0 -> v1.2.0

    The above examples apply to release branches as well, the key difference is the branches are prefixed with 'release/portal/{{tag_version}}
    """
    tag_version = re.findall(r"\d+", latest_tag)
    current_major_version = int(tag_version[0])
    current_minor_version = int(tag_version[1])

    if release_version == ReleaseVersion.MAJOR.value:
        next_tag = f"v{current_major_version + 1}.0.0-rc1"
        new_branch = f"release/portal/v{current_major_version + 1}.0.0"
    elif release_version == ReleaseVersion.MINOR.value:
        next_tag = f"v{current_major_version}.{current_minor_version + 1}.0-rc1"
        new_branch = (
            f"release/portal/v{current_major_version}.{current_minor_version + 1}.0"
        )
    else:
        raise ValueError("RELEASE_VERSION not set. Action aborted.")

    return [next_tag, new_branch]


def get_latest_release_branch(release_name, repo):
    """
    Grabs the latest release branch and returns the entire branch name.

    Example with three branches:
    `release/portal/v1.0.0`, `release/portal/v2.0.0`, `release/portal/v2.1.0`

    Would return: `release/portal/v2.1.0`
    """
    branch_name_pattern = re.compile(fr'release/{release_name}/v\d+\.\d+\.\d+')
    for branch in repo.get_branches():
        print(branch)
    # Extract matching branches
    release_branches = [branch.name for branch in repo.get_branches() if re.match(branch_name_pattern, branch.name)]
    print(release_branches)
    # Sort the branches by version in descending order
    latest_branch = sorted(release_branches, key=lambda x: [int(num) for num in re.findall(r"\d+", x)])[-1]

    if not latest_branch:
        raise Exception("No release branches found")

    return latest_branch


def increment_release_candidate_tag(tag):
    """
    Increments the release candidate (rc) tag. This is used to update an existing release tag,
    so it is expected the -rc1 version is already created.

    Example output:
    `portal/v1.0.0-rc1` -> `portal/v1.0.0-rc2`
    """
    # Split the tag into its prefix and release candidate number
    prefix, rc_tag = tag.rsplit('-rc', 1)

    # Try to convert the rc part into an integer, increment and construct the new tag
    try:
        rc_num = int(rc_tag)
        new_rc = f"{prefix}-rc{rc_num + 1}"
    except ValueError:
        raise ValueError(f"Invalid RC tag in {tag}. Expected format: -rcN")
    return new_rc

