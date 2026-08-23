## Purpose

Gives reviewers a terminal-style interface inside the SaaS frontend to run backend test categories and see pass/fail results without leaving the browser. Embedded as a tab within the Configurações page (see `settings-ui`) rather than its own top-level route.

## ADDED Requirements

### Requirement: Not a standalone sidebar route
The Testes UI SHALL be reachable only as a tab/section within the Configurações page, not via its own sidebar entry or route.

#### Scenario: No dedicated sidebar entry
- **WHEN** the user views the sidebar
- **THEN** there is no "Testes" entry separate from "Configurações"

### Requirement: Test categories can be run from the UI
The Testes tab SHALL let the user select and run a backend test category, showing terminal-style output as the run progresses.

#### Scenario: Running a test category shows live output
- **WHEN** the user selects a test category and starts a run
- **THEN** the tab shows terminal-style output updating as the run progresses

### Requirement: Results show pass/fail with timing and error detail
The Testes tab SHALL display, for each completed test, its passed/failed status, duration, and error message when failed.

#### Scenario: Completed run lists per-test results
- **WHEN** a test run finishes
- **THEN** each test in that run is listed with its passed/failed status and duration, and its error message if it failed
