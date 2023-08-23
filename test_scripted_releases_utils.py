import unittest
from unittest.mock import MagicMock

from scripted_releases_utils import increment_release_candidate_tag, increment_release_tag_and_branch_from_version, \
    get_latest_release_branch, get_latest_release_tag, extract_version


class TestIncrementReleaseTagAndBranch(unittest.TestCase):
    def test_major_release(self):
        latest_tag = "v1.0.0"
        release_version = "Major"

        result = increment_release_tag_and_branch_from_version(
            latest_tag, release_version
        )

        self.assertEqual(result, ["v2.0.0-rc1", "release/portal/v2.0.0"])

    def test_minor_release(self):
        latest_tag = "v1.0.0"
        release_version = "Minor"

        result = increment_release_tag_and_branch_from_version(
            latest_tag, release_version
        )

        self.assertEqual(result, ["v1.1.0-rc1", "release/portal/v1.1.0"])

    def test_invalid_release_version(self):
        latest_tag = "v1.0.0"
        release_version = None

        with self.assertRaises(ValueError):
            increment_release_tag_and_branch_from_version(latest_tag, release_version)


class BranchMock:
    def __init__(self, name):
        self.name = name


class TestGetLatestReleaseBranch(unittest.TestCase):

    def setUp(self):
        self.repo = MagicMock()
        self.repo.get_branches.return_value = [
            BranchMock(name="release/portal/v1.0.0"),
            BranchMock(name="release/portal/v1.1.0"),
            BranchMock(name="release/portal/v2.0.0"),
            BranchMock(name="release/other/v1.0.0"),
            BranchMock(name="feature/portal/new-feature")
        ]
        self.release_name = "portal"

    def test_get_latest_release_branch(self):
        latest_branch = get_latest_release_branch(self.release_name, self.repo)
        self.assertEqual(latest_branch, "release/portal/v2.0.0")

    def test_get_latest_release_branch_with_larger_numbers(self):
        self.repo.get_branches.return_value = [
            BranchMock(name="release/portal/v100.0.0"),
            BranchMock(name="release/portal/v250.0.0"),
            BranchMock(name="release/portal/v500.0.0"),
        ]
        latest_branch = get_latest_release_branch(self.release_name, self.repo)
        self.assertEqual(latest_branch, "release/portal/v500.0.0")

    def test_get_latest_release_branch_with_minor_increment(self):
        self.repo.get_branches.return_value = [
            BranchMock(name="release/portal/v100.0.0"),
            BranchMock(name="release/portal/v100.1.0"),
            BranchMock(name="release/portal/v100.2.0"),
        ]
        latest_branch = get_latest_release_branch(self.release_name, self.repo)
        self.assertEqual(latest_branch, "release/portal/v100.2.0")

    def test_get_latest_release_branch_no_versions(self):
        self.release_name = "nonexistent"
        with self.assertRaises(Exception):
            get_latest_release_branch(self.release_name, self.repo)


class TestExtractVersion(unittest.TestCase):
    def test_extract_version(self):
        tag1 = "portal/v1.0.0-rc1"
        version1 = extract_version(tag1)
        self.assertEqual(version1, "1.0.0")

        tag2 = "portal/v2.5.1-rc3"
        version2 = extract_version(tag2)
        self.assertEqual(version2, "2.5.1")

        tag3 = "non-matching-tag"
        version3 = extract_version(tag3)
        self.assertIsNone(version3)


class TestGetLatestReleaseTag(unittest.TestCase):
    def setUp(self):
        self.repo = MagicMock()

    def test_get_latest_release_tag(self):
        self.repo.get_tags.return_value = [
            BranchMock(name='portal/v1.0.0-rc1'),
            BranchMock(name='portal/v2.0.0-rc1'),
            BranchMock(name='portal/v2.1.0-rc1')
        ]

        latest_tag = get_latest_release_tag('portal', self.repo)
        self.assertEqual(latest_tag.name, 'portal/v2.1.0-rc1')

    def test_no_release_tags_found(self):
        self.repo.get_tags.return_value = []

        latest_tag = get_latest_release_tag(' portal', self.repo)
        self.assertIsNone(latest_tag)


class TestIncrementReleaseCandidateString(unittest.TestCase):

    def test_increment_release_candidate_tag(self):
        self.assertEqual(increment_release_candidate_tag("portal/v1.0.0-rc1"), "portal/v1.0.0-rc2")
        self.assertEqual(increment_release_candidate_tag("portal/v1.0.0-rc99"), "portal/v1.0.0-rc100")
        self.assertEqual(increment_release_candidate_tag("portal/v2.3.4-rc5"), "portal/v2.3.4-rc6")

    def test_increment_non_rc_tag(self):
        with self.assertRaises(ValueError, msg="Invalid RC tag in portal/v1.0.0. Expected format: -rcN"):
            increment_release_candidate_tag("portal/v1.0.0")
        with self.assertRaises(ValueError, msg="Invalid RC tag in portal/RC_test. Expected format: -rcN"):
            increment_release_candidate_tag("portal/RC_test")


if __name__ == "__main__":
    unittest.main()
