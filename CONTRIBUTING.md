# Contributing to Any2Giga

Keep issues, commits, documentation and code comments clear and in plain English. Follow the
[architecture rules](ARCHITECTURE.md) and [Code of Conduct](CODE_OF_CONDUCT.md). Distinguish
implemented behaviour from plans.

## Development

Install [uv](https://docs.astral.sh/uv/) and [Just](https://just.systems/), then run
`uv sync --locked`. The project supports Python 3.12 and later.

The commands use the committed lockfile and fail if it is out of date. When changing dependencies,
run `uv lock` and include the updated `uv.lock` in the change.

| Command | Purpose |
| --- | --- |
| `just test` | Run the tests. |
| `just cov` | Run the tests with statement and branch coverage reports. |
| `just lint` | Check formatting, style and import order. |
| `just format` | Format code and apply Ruff's automatic fixes. |
| `just type` | Check types in the package and tests. |
| `just build` | Build the wheel and source distribution. |
| `just changelog` | Preview the next release notes. |
| `just release-notes` | Move changelog fragments into the changelog. |

Run the relevant checks before a change is submitted. Tests must not require live GigaChat access
or credentials by default. Put optional live checks behind an explicit opt-in. Use synthetic data
in fixtures; do not include credentials or real prompts and model responses.

`just cov` reports missing lines and branches in the terminal and writes separate statement and
branch totals to `build/coverage.json`, including per-function and per-class details. The terminal's
coverage percentage combines statements and branches.

## Issues

Check existing issues before opening one. Give each issue one clear outcome and a short title that
describes the problem or change. Use the [issue template](.github/ISSUE_TEMPLATE/issue.md) to
describe the problem, why it matters and the observable results and checks that complete the work.

Keep the issue self-contained. Add examples, links and scope limits when useful. Separate agreed
behaviour from proposals; do not invent implementation details. Keep credentials, prompts and
private model responses out of issues. Report vulnerabilities privately as described in
[SECURITY.md](SECURITY.md).

Give each issue one type label: `bug`, `feature`, `maintenance`, `docs` or `question`. Add `ci`
for CI and developer tooling, and `good first issue` for small, self-contained tasks. Close
duplicates and declined issues with the matching close reason instead of a label. Link the original
issue when closing a duplicate.

## Branches and commits

For issue work, branch from `main` and use only the issue number as the branch name, for example
`1` for issue #1. Keep the branch focused on its issue. Work without an issue uses a short
descriptive branch name.

Use a one-line commit message that starts with an action. For issue work, include the issue number,
for example `#1: add the request validator`. Without an issue, use a line such as
`add the pull request template`. Keep unrelated changes out of the commit and inspect the staged
diff before committing. Add any required [changelog fragment](#changelog) in the same commit as the
change.

Do not add generated-by lines or tool attribution to commits, issues, pull requests, reviews,
comments, documentation or code. Do not add commit bodies, co-author lines or sign-off trailers.

## Pull requests

Use the [pull request template](.github/pull_request_template.md) to explain the problem, resulting
behaviour, relevant decisions and checks. Keep it short; do not repeat the issue or list every
changed file. Add migration or breaking-change notes when needed. Link the issue and use
`Closes #<number>` when the pull request completes it. Update the description and affected
documentation when the change evolves.

Open a draft pull request while work is in progress. When it is ready, mark it ready for review. If
a maintainer other than the author is available, request their review and request it again after
addressing the findings.

## Reviews

Review the submitted change against the issue and the checklist below. State what the code does,
its consequences and what you checked. Do not restate the diff or guess at intent; ask instead.

Put findings about specific code in inline comments. Use the review body for the verdict and
findings that span files. Mark non-blocking findings with one of these prefixes:

- **Nit:** a small or stylistic point the author may skip.
- **Question:** a request for clarification that does not block the change.

Other findings block the merge until resolved. A question also blocks the merge if its answer is
needed to judge the change. Use these sections in the review body, omitting empty sections:

- **Summary:** one sentence on the change and whether it is ready.
- **Blocking:** each problem, its `file:line`, consequence and a concrete fix or check.
- **Non-blocking:** nits, questions and follow-ups.
- **Checked:** commands run and anything not verified.

Request changes only for blocking findings. If only nits remain, approve and say which ones you
expect to be addressed. Move work outside the pull request's scope to a separate issue and link it.

### Review checklist

- The change follows the [architecture rules](ARCHITECTURE.md#invariants), including how to document
  exceptions.
- The public HTTP contract and its documentation match the behaviour.
- Errors and logs do not expose credentials, prompts or private model responses.
- New behaviour has tests; fakes and adapters have contract tests where applicable.
- Relevant checks pass, including `just lint`, `just type` and `just test` for code changes.
- User-visible changes have a [changelog fragment](#changelog).

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
