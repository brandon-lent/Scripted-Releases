# Scripted Releases

This workflow is intended to easily automate the release process by automatically creating release notes with a tag and a new release branch.

## Requirements

Four seperate options required
1. Create-release
2. Update-release
3. Finalize-release
4. Create-hotfix

### Create-release

**Purpose**: To easily create release branch and release notes with auto-incrementing tags

When we create a release, we want the ability to have a minor / major version. In order to do this, we can grab a value from the GitHub action dropdown. 

Ex:

**If the release is minor**:
1. Grab latest tag. eg: v1.0.0
2. Tag = v1.1.0-rc1
3. Branch = release/portal/v1.1.0

**If the release is major**:
1. Grab latest tag. eg: v1.0.0
2. Tag = v2.0.0-rc1
3. Branch = release/portal/v2.0.0

To create a release it needs to:
1. Create Release branch Ex: release/portal/v1.0.0
2. Generate release notes off the that branch with version.
 1. The Tag for a given release will auto-increment. Ex: First release = portal/v1.0.0-rc1, second release = portal/v2.0.0-rc1
 2. The release note title will be release-{{date}}

### Update-release

**If the release is a hotfix**
1. Grab latest tag. eg: v1.0.0
2. Tag = v1.0.1
3. Branch = release/portal/v1.0.1-hotfix

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
2. Drop the 'rc' on the tag

## Example with Major release

The current tag is **v1.0.0**

### We create a major release
**Note**: diff is between last production tag and rc1 we are creating
1. Tag = v2.0.0-rc1
2. Branch = release/portal/v2.0.0 with the changes in the tag
3. Release with release notes created in GitHub called portal/v2.0.0-rc1

### We need to update the release with new changes
**Note**: diff is between rc1 and rc2 for release notes
1. Tag = v2.0.0-rc2
2. Branch = release/portal/v2.0.0
3. Release with release notes created in GitHub called portal/v2.0.0-rc2

### We finalize the release to promote it to production
**Note**: Diff is between last production tag and this tag
1. Tag = v2.0.0
2. Branch = release/portal/v2.0.0
3. Release with release notes created in GitHub called portal/v2.0.0

## Example with Minor release
The current tag is **v1.0.0**

### We create a major release
**Note**: diff is between last production tag and rc1 we are creating
1. Tag = v1.1.0-rc1
2. Branch = release/portal/v1.1.0 with the changes in the tag
3. Release with release notes created in GitHub called portal/v1.1.0-rc1

### We need to update the release with new changes
**Note**: diff is between rc1 and rc2 for release notes
1. Tag = v1.1.0-rc2
2. Branch = release/portal/v1.1.0
3. Release with release notes created in GitHub called portal/v1.1.0-rc2

### We finalize the release to promote it to production
**Note**: Diff is between last production tag and this tag
1. Tag = v1.1.0
2. Branch = release/portal/v1.1.0
3. Release with release notes created in GitHub called portal/v1.1.0

## Example with Hotfix
The current tag is **v1.0.0**

### Developer creates Hotfix PR
1. Opens PR against `main` and merge
2. Grab the commit hash to pass to the create-hotfix script
   
### Developer runs the create-hotfix task
1. Developer passes in the commit hash to the script which will cherrypick the specified commits
2. Script creates new tag: v1.0.1
3. Script creates release notes: portal/v1.0.1. The diff is between v1.0.1 and v1.0.0 in this case.

### We take the tag and deploy to target environment
1. Pass in the new tag v1.0.1 and deploy that to prod.

## Implementation

We use the [generate-release GitHub workflow](.) to automatically create a new release branch, release notes, and tag. 

In order to run the python script [release-notes](url) 
