# Architecture

Any2Giga is at the infrastructure stage. `src/any2giga/` is an installable package, but the
gateway and server command are not implemented yet.

The [draft design](docs/superpowers/specs/2026-10-27-any2giga-design.md) describes the planned
APIs, GigaChat integration, reliability requirements and open questions. It does not describe
features available today.

`tests/` contains package tests. `pyproject.toml` and `uv.lock` define the dependencies, and
`Justfile` contains commands used locally and in CI.
