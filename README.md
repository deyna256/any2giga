# Any2Giga

Any2Giga is intended to let applications use GigaChat through an OpenAI-compatible API.

The project is at the infrastructure stage. The gateway, its API routes and a server command
have not been implemented, and there is no release yet. The planned scope and open questions are
in `docs/superpowers/specs/2026-10-27-any2giga-design.md` in the repository.

## Development

Install [uv](https://docs.astral.sh/uv/) and [Just](https://just.systems/), then run:

```sh
uv sync --locked
just lint
just type
just test
just build
```

The project uses Python 3.12 or later. `just --list` shows the other development commands.
Tests do not require GigaChat credentials or access to a live model.

## License

MIT. See the LICENSE file in the source distribution.
