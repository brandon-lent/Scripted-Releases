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
