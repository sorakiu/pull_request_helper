# frontend-ui Specification

## Purpose
TBD - created by archiving change add-bulk-pull-request-creation. Update Purpose after archive.
## Requirements
### Requirement: Login UI
The frontend SHALL provide a login component that initiates GitHub OAuth.

#### Scenario: Login Click
- **WHEN** user clicks login button
- **THEN** redirect to GitHub OAuth URL

### Requirement: Repository Selection UI
The frontend SHALL display a list of repos with checkboxes for selection.

#### Scenario: Repo List Display
- **WHEN** authenticated user accesses app
- **THEN** show repos from API with checkboxes

### Requirement: Bulk PR Form UI
The frontend SHALL provide a form for global branches and editable PR metadata.

#### Scenario: Form Submission
- **WHEN** user selects repos, enters branches/title/body, and submits
- **THEN** send data to API and show job status

