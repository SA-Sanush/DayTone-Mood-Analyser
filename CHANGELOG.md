# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Runtime configuration validation, migration integration, CI, and developer tooling.
- Editable mood logs and privacy-preserving CSV export by default.

### Changed
- Production startup now uses Gunicorn and avoids Flask debug mode.
- Burnout prediction falls back to rule-based analysis if the ML artifact fails.

## [1.0.0] - 2026-06-10

### Added
- Initial DayTone mood logging, dashboards, burnout prediction, admin analytics, CSV export, and PDF reporting.

