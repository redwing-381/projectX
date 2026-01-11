# Implementation Plan: CLI Tool

## Overview

Build a Typer-based CLI that acts as an API client for the deployed ProjectX server. Uses Rich for formatted output and httpx for HTTP requests.

## Tasks

- [x] 1. Create configuration module
  - [x] 1.1 Create `cli/config.py` with CLIConfig model
    - Define config file path (~/.projectx/config.json)
    - Implement load_config() and save_config() functions
    - Set default server URL to Railway deployment
    - _Requirements: 4.1, 4.3, 4.4_

  - [ ]* 1.2 Write property test for config round-trip
    - **Property 1: Configuration round-trip**
    - **Validates: Requirements 4.1**

- [x] 2. Create API client module
  - [x] 2.1 Create `cli/client.py` with ProjectXClient class
    - Implement health(), status(), check(), test_urgent() methods
    - Use httpx for HTTP requests with timeout handling
    - Raise appropriate exceptions for error responses
    - _Requirements: 1.1, 2.1, 3.1_

- [x] 3. Implement CLI commands
  - [x] 3.1 Create `cli/main.py` with Typer app
    - Set up app with name "projectx" and help text
    - Import Rich console for formatted output
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 3.2 Implement `status` command
    - Call client.health() and client.status()
    - Display server URL, health status, pipeline readiness
    - Handle connection errors gracefully
    - Support --json flag
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 5.4_

  - [x] 3.3 Implement `check` command
    - Call client.check() with spinner
    - Display emails_checked, alerts_sent
    - List each alert with sender/subject in table
    - Handle errors gracefully
    - Support --json flag
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 5.4_

  - [ ]* 3.4 Write property test for check response display
    - **Property 2: Check response display completeness**
    - **Validates: Requirements 2.2, 2.3**

  - [x] 3.5 Implement `test` command
    - Call client.test_urgent() with spinner
    - Display classification result and reason
    - Show SMS status (sent/failed)
    - Support --json flag
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 5.4_

  - [ ]* 3.6 Write property test for classification display
    - **Property 5: Classification display completeness**
    - **Validates: Requirements 3.2**

  - [x] 3.7 Implement `config` command group
    - `config show` - display current config
    - `config set-url <url>` - save new server URL
    - Support --json flag
    - _Requirements: 4.1, 4.2, 5.4_

- [x] 4. Implement error handling
  - [x] 4.1 Create error handling utilities
    - Wrap API calls with try/except
    - Format error messages consistently
    - Never show stack traces without --debug
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [ ]* 4.2 Write property test for error message safety
    - **Property 4: Error message safety**
    - **Validates: Requirements 6.1, 6.2, 6.4**

- [ ]* 5. Write property test for JSON output validity
  - **Property 3: JSON output validity**
  - **Validates: Requirements 5.4**

- [x] 6. Checkpoint - Test CLI locally
  - Run `python -m cli.main status`
  - Run `python -m cli.main check`
  - Run `python -m cli.main test`
  - Run `python -m cli.main config show`
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Update pyproject.toml entry point
  - Ensure `projectx = "cli.main:app"` is configured
  - Test with `pip install -e .` and `projectx --help`
  - _Requirements: All_

## Notes

- Tasks marked with `*` are optional property tests
- Use Rich for all formatted output (colors, tables, spinners)
- httpx is already in dependencies
- Default server URL: https://projectx-production-0eeb.up.railway.app
- CLI should work without any local credentials (API client only)
