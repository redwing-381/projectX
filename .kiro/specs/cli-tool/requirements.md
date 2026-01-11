# Requirements Document

## Introduction

A command-line interface (CLI) tool for ProjectX that allows developers to interact with the deployed email monitoring service without leaving their terminal. The CLI acts as a thin API client, communicating with the Railway-deployed server to check status, trigger email checks, and view alert history.

## Glossary

- **CLI**: Command-Line Interface application built with Typer
- **API_Server**: The deployed FastAPI backend on Railway
- **User**: Developer using the CLI from their terminal
- **Alert**: An SMS notification sent for an urgent email

## Requirements

### Requirement 1: Server Health Check

**User Story:** As a developer, I want to quickly check if the ProjectX server is running, so that I can verify the service is operational before relying on it.

#### Acceptance Criteria

1. WHEN the User runs `projectx status`, THE CLI SHALL display the server health status
2. WHEN the API_Server is reachable and healthy, THE CLI SHALL display "✓ Server is running" with green formatting
3. WHEN the API_Server is unreachable, THE CLI SHALL display "✗ Server is offline" with red formatting and exit with code 1
4. THE CLI SHALL display the configured server URL in the status output

### Requirement 2: Manual Email Check

**User Story:** As a developer, I want to manually trigger an email check from my terminal, so that I can process new emails on demand without opening a browser.

#### Acceptance Criteria

1. WHEN the User runs `projectx check`, THE CLI SHALL call the /check endpoint on the API_Server
2. WHEN the check completes successfully, THE CLI SHALL display the number of emails checked and alerts sent
3. WHEN urgent emails are found, THE CLI SHALL list each alert with sender and subject
4. WHEN no urgent emails are found, THE CLI SHALL display "No urgent emails found"
5. IF the API_Server returns an error, THEN THE CLI SHALL display the error message and exit with code 1

### Requirement 3: Test Urgent Classification

**User Story:** As a developer, I want to test the urgency classification without real emails, so that I can verify the AI and SMS flow is working correctly.

#### Acceptance Criteria

1. WHEN the User runs `projectx test`, THE CLI SHALL call the /test-urgent endpoint
2. WHEN the test completes, THE CLI SHALL display the classification result (URGENT/NOT_URGENT) and reason
3. WHEN SMS is sent successfully, THE CLI SHALL display "✓ SMS sent to your phone"
4. WHEN SMS fails, THE CLI SHALL display the error reason

### Requirement 4: Configuration Management

**User Story:** As a developer, I want to configure the CLI with my server URL, so that I can connect to my deployed instance.

#### Acceptance Criteria

1. WHEN the User runs `projectx config set-url <url>`, THE CLI SHALL save the server URL to a config file
2. WHEN the User runs `projectx config show`, THE CLI SHALL display the current configuration
3. THE CLI SHALL store configuration in `~/.projectx/config.json`
4. WHEN no configuration exists, THE CLI SHALL use a default URL or prompt the user

### Requirement 5: Rich Terminal Output

**User Story:** As a developer, I want clear, formatted terminal output, so that I can quickly understand the results.

#### Acceptance Criteria

1. THE CLI SHALL use colored output for success (green), errors (red), and warnings (yellow)
2. THE CLI SHALL use tables for displaying multiple results
3. THE CLI SHALL show spinners/progress indicators for long-running operations
4. THE CLI SHALL support `--json` flag for machine-readable output on all commands

### Requirement 6: Error Handling

**User Story:** As a developer, I want clear error messages when something goes wrong, so that I can troubleshoot issues quickly.

#### Acceptance Criteria

1. WHEN a network error occurs, THE CLI SHALL display "Connection failed: <reason>"
2. WHEN the server returns a 4xx/5xx error, THE CLI SHALL display the error detail from the response
3. WHEN configuration is missing, THE CLI SHALL prompt the user to run `projectx config set-url`
4. THE CLI SHALL never display raw stack traces to the user (log them if --debug flag is set)
