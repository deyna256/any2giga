# Any2Giga

Any2Giga is a planned OpenAI-compatible API gateway for GigaChat.

The gateway and server command are not implemented, and there is no release yet. The
[design draft](https://github.com/deyna256/any2giga/blob/main/docs/superpowers/specs/2026-10-27-any2giga-design.md)
describes the planned scope and open questions.

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
Tests do not require GigaChat credentials or access to a live model. See the
[contribution guide](https://github.com/deyna256/any2giga/blob/main/CONTRIBUTING.md) for details.

## License

MIT. See the LICENSE file in the source distribution.
