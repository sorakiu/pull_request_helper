## ADDED Requirements
### Requirement: GitHub OAuth Authentication
The system SHALL allow users to authenticate via GitHub OAuth, storing access tokens securely for API access.

#### Scenario: Successful Login
- **WHEN** user clicks login and completes GitHub OAuth flow
- **THEN** access token is stored and user is redirected to repo selection

#### Scenario: Invalid Token
- **WHEN** stored token is expired or invalid
- **THEN** user is prompted to re-authenticate