# Scripted Releases

This workflow is intended to easily automate the release process by automatically creating release notes with a tag and a new release branch.

## Requirements

Two seperate options required
1. Create-release
2. Update-release

### Create-release

**Purpose**: To easily create release branch and release notes with auto-incrementing tags

To create a release it needs to:
1. Create Release branch Ex: release/portal/v1.0.0
2. Generate release notes off the that branch with version.
 1. The Tag for a given release will auto-increment. Ex: First release = portal/v1.0.0-rc1, second release = portal/v2.0.0-rc1
 2. The release note title will be release-{{date}}

### Update-release

**Purpose**: In the event an addition to a given release is required, this task will be used. 

To update a release it needs to:
1. Grab the latest release candidate branch. Ex: release/portal/v1.0.0-rc1
2. Grab the associated tag and increment the rc. Ex: portal/v1.0.0-rc2
3. Generate link to display the diff between rc1 and rc2 tag. 
4. Merge the changes into the release candidate branch. 

### Finalize-release

**Purpose**: We will use this to create the final tag which drops the RC suffix from the existing tags.

To finalize the release, it needs to:
1. Grab the latest release candidate tag 



## Implementation

We use the [generate-release GitHub workflow](.) to automatically create a new release branch, release notes, and tag. 

In order to run the python script [release-notes](url) 
