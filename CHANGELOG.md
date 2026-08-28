# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [4.2.1] - 2026-08-08

### Fixed

- Harden wait feed against races and accidental Redis cross-worker marker deletes.
- Filter exceptions during wait resolution no longer crash the middleware.

### Added

- Real Redis integration test suite and CI workflow.

## [4.2.0] - 2026-08-08

### Added

- `RedisInputStorage` for shared wait markers across workers (optional `redis` extra).
- Stronger CI coverage gate and additional edge-case tests.

## [4.1.0] - 2026-08-08

### Added

- `data_key` parameter on `setup_input()` to customize the handler DI key (default: `input`).

### Changed

- README rewritten as a short problem-first overview.

## [4.0.0] - 2026-08-08

### Added

- Dispatcher-scoped `setup_input()` with `InputWaiter` injected into handlers (like `FSMContext`).
- `InputStorage` protocol, `MemoryInputStorage`, and `WaitRegistry`.
- Test workflow matrix for Python 3.10–3.14 with coverage gate.

### Changed

- Packaging migrated to `uv`, `pyproject.toml`, and `src/` layout.
- Minimum supported Python version raised to 3.10.

### Removed

- `InputManager` / router-manager API replaced by `setup_input()` + `InputWaiter`.

### Fixed

- Superseded waits are aborted without leaking session state.

## [3.1.1] - 2026-08-08

### Added

- GitHub Actions workflow to publish to PyPI on `v*` tags.

## [3.1.0] - 2025-09-22

### Changed

- `InputMiddleware` marks consumed messages so other handlers can still run.
- `SessionManager.feed()` returns whether the message was consumed.
- `InputManager` and router setup accept `Router` or `Dispatcher`.

## [2.2.1] - 2025-09-20

### Fixed

- Session cleanup logic in `SessionManager`.
- Filter handling updated to use `FilterObject`.
- Router initialization logic in type helpers.

## [2.0.1] - 2025-09-17

### Fixed

- Argument validation in `InputManager`.

## [2.0.0] - 2025-09-17

### Changed

- Refactored input manager and storage architecture (breaking internal layout).

## [1.1.1] - 2025-09-11

### Changed

- Storage methods made asynchronous.

### Fixed

- Email validation and filter handling improvements.

## [1.0.0] - 2025-09-11

### Changed

- Renamed `Asker` to `InputManager`.
- Project renamed to `aiogram-input` / `aiogram_input`.

## [0.1.0] - 2025-08-17

### Added

- Initial release: await user replies in aiogram handlers with timeout support.
- `Asker` class, router setup, and `PendingUserFilter`.
- PyPI packaging workflow.

[Unreleased]: https://github.com/mamahoos/aiogram-input/compare/v4.2.1...HEAD
[4.2.1]: https://github.com/mamahoos/aiogram-input/compare/v4.2.0...v4.2.1
[4.2.0]: https://github.com/mamahoos/aiogram-input/compare/v4.1.0...v4.2.0
[4.1.0]: https://github.com/mamahoos/aiogram-input/compare/v4.0.0...v4.1.0
[4.0.0]: https://github.com/mamahoos/aiogram-input/compare/v3.1.1...v4.0.0
[3.1.1]: https://github.com/mamahoos/aiogram-input/compare/v3.1.0...v3.1.1
[3.1.0]: https://github.com/mamahoos/aiogram-input/compare/v2.2.1...v3.1.0
[2.2.1]: https://github.com/mamahoos/aiogram-input/compare/v2.0.1...v2.2.1
[2.0.1]: https://github.com/mamahoos/aiogram-input/compare/2.0.0...v2.0.1
[2.0.0]: https://github.com/mamahoos/aiogram-input/compare/v1.1.1...2.0.0
[1.1.1]: https://github.com/mamahoos/aiogram-input/compare/9d83751...v1.1.1
