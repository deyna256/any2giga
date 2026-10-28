# Contributing to Any2Giga

Keep issues, commits, documentation and code comments clear and in plain English. Follow the
[Code of Conduct](CODE_OF_CONDUCT.md) and distinguish implemented behaviour from plans.

## Development

Install [uv](https://docs.astral.sh/uv/) and [Just](https://just.systems/), then run
`uv sync --locked`. The project supports Python 3.12 and later.

The commands use the committed lockfile and fail if it is out of date. When changing dependencies,
run `uv lock` and include the updated `uv.lock` in the change.

| Command | Purpose |
| --- | --- |
| `just test` | Run the tests. |
| `just cov` | Run the tests with a coverage report. |
| `just lint` | Check formatting, style and import order. |
| `just format` | Format code and apply Ruff's automatic fixes. |
| `just type` | Check types in the package and tests. |
| `just build` | Build the wheel and source distribution. |
| `just changelog` | Preview the next release notes. |
| `just release-notes` | Move changelog fragments into the changelog. |

Run the relevant checks before a change is submitted. Tests must not require live GigaChat access
or credentials by default. Put optional live checks behind an explicit opt-in and keep secrets,
prompts and model responses out of fixtures and logs.

## Issues and changes

Keep each issue focused on one outcome. Describe the problem, why it matters and the observable
result that completes it. Report vulnerabilities privately as described in [SECURITY.md](SECURITY.md).

Use a short descriptive branch for work without an issue; for issue work, use the issue number as
the branch name. Use a one-line commit message beginning with an action, for example `#1: add the
request validator`, or `add the pull request template` for work without an issue.

Use the pull request template to explain the problem, resulting behaviour and checks performed.
Do not add generated-by lines, tool attribution, co-author lines or sign-off trailers.

## Changelog

User-visible changes get a fragment in `changelog.d/`. Name it `<issue>.<type>.md`, where type is
`added`, `changed`, `deprecated`, `removed`, `fixed` or `security`. Work without an issue uses
`+<name>.<type>.md`. Write one or two sentences for users. Changes to tests and internal tooling
need no fragment unless they change user-visible behaviour.

`just changelog` previews the entry. Before a release, `just release-notes` moves fragments into
[CHANGELOG.md](CHANGELOG.md); commit the result along with the version change.

## Releases

Releases are manual. Before merging to `main`:

1. Set the version with `uv version <version>` and update the lockfile with `uv lock`.
2. Review `just changelog`, then run `just release-notes` to update the changelog and remove the
   fragments. Commit these changes and the version together.
3. Run the checks and merge the release commit to `main`.

Run the **Release** workflow on `main`. It checks the prepared changelog, builds and attests the
distributions, tags the commit that triggered the workflow, and creates a GitHub release. The
tag and [build provenance](https://docs.github.com/en/actions/concepts/security/artifact-attestations)
identify the same commit, even if `main` advances while the workflow runs. If it fails after the
tag is pushed, inspect the existing tag and release before recovering; the workflow will refuse
to reuse that tag. The **Publish** workflow uploads distributions from a selected release to PyPI.

Building and testing run with read-only repository permissions. Separate jobs attest the artifacts
and create the release; the latter has write access but does not run project or build dependencies.
An attestation records artifact provenance; it cannot establish that the build dependencies were
trustworthy. The repository must support artifact attestations and allow Actions to create tags.

Before configuring a PyPI trusted publisher:

1. Protect `main` so that changes to publishing workflows require review by trusted maintainers.
2. Ensure the GitHub Actions environment `pypi` exists. Under **Deployment branches and tags**, select
   **Selected branches and tags** and allow the `main` branch only.
3. Where the GitHub plan and team permit it, require a trusted reviewer for the `pypi` environment
   and prevent self-review. Protect release tags as well.
4. Configure the PyPI trusted publisher for this repository, `publish.yml` and the `pypi`
   environment.

The environment restriction is a GitHub repository setting; the branch check in `publish.yml` is
only an additional guard. A workflow on another branch could change its own check. No release or
PyPI publication is automatic.
