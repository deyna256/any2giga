# Run the test suite.
test:
    uv run --locked pytest

# Report which lines and branches in the package the test suite did not reach.
cov:
    uv run --locked pytest --cov=any2giga --cov-branch --cov-report=term-missing --cov-report=json:build/coverage.json

# Check formatting, style and import order without changing files.
lint:
    uv run --locked ruff format --check .
    uv run --locked ruff check .

# Apply Ruff's automatic fixes and then format the result.
format:
    uv run --locked ruff check --fix .
    uv run --locked ruff format .

# Check types in the package and tests.
type:
    uv run --locked ty check

# Build a wheel and source distribution in dist/.
build:
    uv build

# Show the next release's changelog entry without changing files.
changelog:
    uv run --locked towncrier build --draft --version "$(uv version --short)"

# Move the fragments into CHANGELOG.md before committing a release.
release-notes:
    uv run --locked towncrier build --yes --version "$(uv version --short)"
