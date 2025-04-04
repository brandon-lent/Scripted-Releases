# Scripted Releases

![Scripted Releases](https://img.shields.io/badge/version-1.0.0-blue)
![GitHub Actions](https://img.shields.io/badge/github-actions-2088FF)
![License](https://img.shields.io/badge/license-MIT-orange)

A powerful GitHub Actions workflow designed to streamline your software release process. Scripted Releases eliminates manual errors, ensures consistency across releases, and saves valuable development time by automating version control, changelog generation, and deployment workflows directly in your GitHub repository.

## 📋 Overview

Scripted Releases automates the entire release lifecycle with four primary GitHub Actions workflows:

- **Create Release** - Generate new release branches with proper versioning
- **Update Release** - Add changes to existing releases with clear change tracking
- **Finalize Release** - Promote release candidates to production

## ✨ Features

- **Semantic Versioning** - Automatic version incrementation following semver principles
- **Branch Management** - Automated creation and maintenance of release branches
- **Release Notes** - Automatically generated changelogs with meaningful diffs
- **Tagging System** - Structured tag creation for release candidates and production releases
- **GitHub Integration** - Seamless integration with GitHub Releases

## 🚀 Getting Started

### Installation

1. Add the workflow files to your repository in the `.github/workflows/` directory
2. Configure the workflows according to your project needs

### Basic Usage

Trigger the workflows from the GitHub Actions tab in your repository:

1. **Create Release** - Select the workflow and choose minor or major release type
2. **Update Release** - Run when you need to add changes to an existing release
3. **Finalize Release** - Execute when ready to promote to production

## 📖 Detailed Usage

### Create Release

**Purpose**: Create a release branch and release notes with auto-incrementing tags.

**Inputs**:
- `release-type` - Dropdown to select `minor` or `major` release type

**Behavior**:

For a **minor** release:
1. Identifies latest tag (e.g., v1.0.0)
2. Creates new tag: v1.1.0-rc1
3. Creates branch: release/portal/v1.1.0

For a **major** release:
1. Identifies latest tag (e.g., v1.0.0)
2. Creates new tag: v2.0.0-rc1
3. Creates branch: release/portal/v2.0.0

**Result**:
- New release branch created
- Release notes generated comparing latest production tag to new RC
- GitHub release created with the tag and notes

### Update Release

**Purpose**: Add new changes to an existing release.

**Behavior**:
1. Identifies the latest release candidate branch
2. Increments the RC number (e.g., rc1 → rc2)
3. Generates diff between previous RC and new RC
4. Merges changes into the release branch

**Result**:
- Updated release branch
- New RC tag created
- Release notes showing changes since previous RC

### Finalize Release

**Purpose**: Promote a release candidate to production.

**Behavior**:
1. Identifies the latest release candidate tag
2. Creates a new tag without the RC suffix
3. Generates comprehensive release notes

**Result**:
- Production tag created (e.g., v1.1.0)
- Final release notes comparing previous production release to new release
- GitHub release marked as latest


## 📝 Examples

### Major Release Workflow

Starting with tag **v1.0.0**:

1. **Create Release**:
   - Trigger the "Create Release" workflow
   - Select "major" from the dropdown
   - Result:
     - Tag: v2.0.0-rc1
     - Branch: release/portal/v2.0.0
     - Notes: Diff between v1.0.0 and v2.0.0-rc1

2. **Update Release**:
   - Make changes and merge to main
   - Trigger the "Update Release" workflow
   - Result:
     - Tag: v2.0.0-rc2
     - Branch: release/portal/v2.0.0 (unchanged)
     - Notes: Diff between v2.0.0-rc1 and v2.0.0-rc2

3. **Finalize Release**:
   - Trigger the "Finalize Release" workflow
   - Result:
     - Tag: v2.0.0
     - Branch: release/portal/v2.0.0 (unchanged)
     - Notes: Comprehensive diff between v1.0.0 and v2.0.0

### Minor Release Workflow

Starting with tag **v1.0.0**:

1. **Create Release**:
   - Trigger the "Create Release" workflow
   - Select "minor" from the dropdown
   - Result:
     - Tag: v1.1.0-rc1
     - Branch: release/portal/v1.1.0
     - Notes: Diff between v1.0.0 and v1.1.0-rc1

2. **Update Release**:
   - Make changes and merge to main
   - Trigger the "Update Release" workflow
   - Result:
     - Tag: v1.1.0-rc2
     - Branch: release/portal/v1.1.0 (unchanged)
     - Notes: Diff between v1.1.0-rc1 and v1.1.0-rc2

3. **Finalize Release**:
   - Trigger the "Finalize Release" workflow
   - Result:
     - Tag: v1.1.0
     - Branch: release/portal/v1.1.0 (unchanged)
     - Notes: Comprehensive diff between v1.0.0 and v1.1.0


## 🔧 Implementation

The workflow uses a combination of GitHub Actions and custom scripts:

- **[generate-release GitHub workflow](.github/workflows/generate-release.yml)** - Main workflow file
- **[release-notes script](scripts/release-notes.py)** - Python script for generating release notes

The workflow leverages GitHub Actions' built-in Git capabilities along with custom logic to manage:
- Semantic versioning
- Branch creation and management
- Tag creation
- Release note generation
- GitHub Releases integration

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
