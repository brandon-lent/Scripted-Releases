# -*- coding: utf-8 -*-
import os
import unittest
from unittest.mock import MagicMock

from scripts.scripted_release.scripted_release_utils import (
    increment_release_tag_and_branch_from_version,
    get_latest_release_branch,
    extract_version,
    get_latest_release_tag,
    ReleaseLog,
    drop_release_candidate_string,
    increment_release_candidate_tag,
)


class ReleaseLogTests(unittest.TestCase):
    def setUp(self):
        self.filename = "test_release_log.txt"
        self.release_logger = ReleaseLog(self.filename)

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_append_release_line(self):
        # Append release lines
        version = "Version 1.0.0"
        self.release_logger.append_release_line(f"📝 Release Notes: {version}")
        self.release_logger.append_release_line("🔗 Tag Comparison: v1.0.0...v1.1.0")
        self.release_logger.append_release_line("✅ Created new branch: main")
        self.release_logger.append_release_line("✅ Created new tag: v1.1.0")

        # Verify that the file exists and contains the expected content
        self.assertTrue(os.path.exists(self.filename))
        with open(self.filename, "r") as file:
            file_content = file.read()
            self.assertIn("📝 Release Notes: Version 1.0.0", file_content)
            self.assertIn("🔗 Tag Comparison: v1.0.0...v1.1.0", file_content)
            self.assertIn("✅ Created new branch: main", file_content)
            self.assertIn("✅ Created new tag: v1.1.0", file_content)


class TestIncrementReleaseTagAndBranch(unittest.TestCase):
    def test_major_release(self):
        latest_tag = "portal/v1.0.0"
        release_version = "Major"

        result = increment_release_tag_and_branch_from_version(
            latest_tag, release_version, "portal"
        )

        self.assertEqual(result, ["portal/v2.0.0-rc1", "release/portal/v2.0.0"])

    def test_minor_release(self):
        latest_tag = "portal/v1.0.0"
        release_version = "Minor"

        result = increment_release_tag_and_branch_from_version(
            latest_tag, release_version, "portal"
        )

        self.assertEqual(result, ["portal/v1.1.0-rc1", "release/portal/v1.1.0"])

    def test_invalid_release_version(self):
        latest_tag = "v1.0.0"
        release_version = None

        with self.assertRaises(ValueError):
            increment_release_tag_and_branch_from_version(
                latest_tag, release_version, "portal"
            )


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
            BranchMock(name="feature/portal/new-feature"),
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
            BranchMock(name="portal/v1.0.0-rc1"),
            BranchMock(name="portal/v2.0.0-rc1"),
            BranchMock(name="portal/v2.1.0-rc1"),
        ]

        latest_tag = get_latest_release_tag("portal", self.repo)
        self.assertEqual(latest_tag.name, "portal/v2.1.0-rc1")

    def test_no_release_tags_found(self):
        self.repo.get_tags.return_value = []

        latest_tag = get_latest_release_tag(" portal", self.repo)
        self.assertIsNone(latest_tag)


class TestIncrementReleaseCandidateString(unittest.TestCase):
    def test_increment_release_candidate_tag(self):
        self.assertEqual(
            increment_release_candidate_tag("portal/v1.0.0-rc1"), "portal/v1.0.0-rc2"
        )
        self.assertEqual(
            increment_release_candidate_tag("portal/v1.0.0-rc99"), "portal/v1.0.0-rc100"
        )
        self.assertEqual(
            increment_release_candidate_tag("portal/v2.3.4-rc5"), "portal/v2.3.4-rc6"
        )

    def test_increment_non_rc_tag(self):
        with self.assertRaises(
                ValueError, msg="Invalid RC tag in portal/v1.0.0. Expected format: -rcN"
        ):
            increment_release_candidate_tag("portal/v1.0.0")
        with self.assertRaises(
                ValueError, msg="Invalid RC tag in portal/RC_test. Expected format: -rcN"
        ):
            increment_release_candidate_tag("portal/RC_test")


class DropReleaseCandidateTag(unittest.TestCase):
    def test_drop_release_candidate_tag(self):
        latest_tag = "portal/v1.0.0-rc1"
        expected_tag = "portal/v1.0.0"
        self.assertEqual(drop_release_candidate_string(latest_tag), expected_tag)

    def test_drop_release_candidate_tag_with_higher_rc_number(self):
        latest_tag = "portal/v1.0.0-rc9000"
        expected_tag = "portal/v1.0.0"
        self.assertEqual(drop_release_candidate_string(latest_tag), expected_tag)

    def test_drop_release_candidate_tag_with_invalid_tag_format(self):
        latest_tag = "tag_doesnt_match"
        self.assertRaises(ValueError, drop_release_candidate_string, latest_tag)


if __name__ == "__main__":
    unittest.main()
