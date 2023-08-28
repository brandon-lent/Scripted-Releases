import re
from enum import Enum
from packaging import version

from github.Repository import Repository


# Maps the release version env variable which is defined by a GitHub action dropdown that runs this script
class ReleaseVersion(Enum):
    MAJOR = "Major"
    MINOR = "Minor"


class ReleaseLog:
    def __init__(self, filename):
        self.filename = filename
        self.create_log_file()

    def create_log_file(self):
        with open(self.filename, "w"):
            pass

    def append_release_line(self, release_line):
        with open(self.filename, "a") as file:
            file.write(release_line + "\n")


def increment_release_tag_and_branch_from_version(latest_tag, release_version, release_name):
    """
    Expected release tag format: portal/v1.0.0

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
        next_tag = f"{release_name}/v{current_major_version + 1}.0.0-rc1"
        new_branch = f"release/{release_name}/v{current_major_version + 1}.0.0"
    elif release_version == ReleaseVersion.MINOR.value:
        next_tag = f"{release_name}/v{current_major_version}.{current_minor_version + 1}.0-rc1"
        new_branch = (
            f"release/{release_name}/v{current_major_version}.{current_minor_version + 1}.0"
        )
    else:
        raise ValueError("RELEASE_VERSION not set. Action aborted.")

    return [next_tag, new_branch]


def get_latest_release_branch(release_name, repo):
    """
    Grabs the latest release branch and returns a Branch object.

    Example with three branches:
    `release/portal/v1.0.0`, `release/portal/v2.0.0`, `release/portal/v2.1.0`

    Would return: `release/portal/v2.1.0`
    """
    branch_name_pattern = re.compile(fr'release/{release_name}/v\d+\.\d+\.\d+')

    # Extract matching branches
    release_branches = [branch.name for branch in repo.get_branches() if
                        re.match(branch_name_pattern, str(branch.name))]

    # Sort the branches by version in descending order
    latest_branch = sorted(release_branches, key=lambda x: [int(num) for num in re.findall(r"\d+", x)])[-1]

    if not latest_branch:
        raise Exception("No release branches found")

    return latest_branch


def extract_version(tag_name):
    """Extracts the version number from the tag name"""
    pattern = r"portal/v(\d+(?:\.\d+)*)-rc\d+"
    match = re.match(pattern, tag_name)
    if match:
        return match.group(1)
    return None


def get_latest_release_tag(release_name, repo: Repository):
    """
    Grabs the latest release tag and returns the GitTag object.

    Example with three tags:
    `portal/v1.0.0-rc1`, `portal/v2.0.0-rc1`, `portal/v2.1.0-rc1`

    Would return:
    `portal/v2.1.0-rc1`
    """

    release_candidate_tags = []
    latest_tag = None

    # Retrieve all tags matching the release candidate pattern
    for tag in repo.get_tags():
        if tag.name.startswith(f"{release_name}/") and "-rc" in tag.name:
            release_candidate_tags.append(tag)

    try:
        # Sort the tags by version number and select the latest one
        latest_tag = max(release_candidate_tags, key=lambda t: version.parse(extract_version(t.name)))
    except ValueError:
        print("No release tags found")

    return latest_tag


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
