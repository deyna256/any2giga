# Architecture

Any2Giga is an installable Python package. The gateway and server command are not implemented yet.
The [design draft](docs/superpowers/specs/2026-10-27-any2giga-design.md) describes the planned
APIs and open questions.

## Invariants

These rules apply to `src/any2giga/`. They follow the ideas of
[Elegant Objects](https://www.yegor256.com/elegant-objects.html), adapted to Python and this
gateway. Examples such as `Usage` and `NoUsage` illustrate the rules; they are not implemented yet.
The [references](#references) explain the ideas and technical constraints behind these rules.

1. **Classes describe things.** A class represents a concept in the problem, not a collection of
   procedures. Do not create `*Manager`, `*Helper`, `*Parser`, `*Runner` or `*Service` classes.
   There are no static methods or module-level functions with logic. When Litestar or the SDK
   requires an exception, keep it at that boundary and document it here.

2. **Objects are frozen by default.** Use `msgspec.Struct` with `frozen=True` for our objects.
   Owners of changing state, such as a connection or a concurrency limit, may be plain mutable
   classes. A mutable collection has a clear owner that controls changes and sharing: `frozen=True`
   alone does not freeze a nested `dict` or `list`.

3. **Constructors do not do work.** A constructor stores its arguments and may reject invalid
   values. It does not do I/O or call dependencies. Open and close resources during the lifetime
   of the component that owns them.

4. **Interfaces describe real alternatives.** Define a `Protocol` only when it has at least two
   implementations, including a fake. Each protocol has a simple working fake for tests. Fakes are
   internal; the public contract of the first release is the HTTP API. Call behavioral objects
   through their interface rather than checking their concrete type.

5. **Extend behavior by wrapping.** Do not add behavior through implementation inheritance or
   switches on an object. `msgspec.Struct`, `Protocol`, exceptions and framework-required base
   classes are exceptions. Fields required by an external API, such as a streaming flag, are data,
   not a reason to add a switch to an object.

6. **Absence has a type.** Use an explicit value for missing domain data, such as `NoUsage` in
   `Usage | NoUsage`. Zero, an empty value, missing data and an error are different things. Do not
   turn a failure into an absence. `None` may appear at external boundaries for JSON `null`,
   where Python or a framework requires it, or for an omitted optional constructor argument that
   is not a domain value. A method that returns no value may return `None`.

7. **Check data at the boundary.** Decode external data into known types and reject invalid input
   or unsupported meaningful parameters. A `Struct` constructor does not check its type
   annotations; use a typed decoder or conversion for external data. Keep an omitted field
   distinct from `null` when the API gives them different meanings. A `null` inside
   client-supplied JSON is that client's data, not our absence value.

   Type the known parts of a function call and result, such as names and IDs. Keep client-supplied
   schemas, arguments and result content as data with a clear owner. Preserve their meaning; report
   unsupported schema features rather than silently dropping them.

8. **Keep API boundaries clear.** Chat Completions and Responses have separate adapters. Share
   translation code only where behavior matches. GigaChat SDK types stay at the SDK boundary;
   our own types carry data within the gateway. Do not build a common format for future APIs
   before there is a real need.

9. **Keep failures explicit.** Normal outcomes and absent values are data. Network and API
   failures, including rate limits, use specific exceptions. Map them to the client API at the
   HTTP boundary without exposing raw provider response bodies or headers. Pass only safe metadata,
   such as a valid `Retry-After`, when it is useful. Do not swallow cancellation or report a failed
   stream as successful.

10. **Bound retries and resource use.** The gateway owns its retry policy. Limit attempts and
    total waiting time, honor `Retry-After` in seconds or as an HTTP date, and use backoff with
    jitter. Retry only when the request is known to be safe to repeat. Never retry after sending
    any stream data to the client. Bound the queue and its wait; release a slot when the upstream
    attempt ends or is cancelled.

    Account for the SDK's retry and authentication behavior so it cannot replay a stream after
    partial output. Client SDKs may retry independently. A limit in one process does not protect
    an account shared with other processes or applications.

11. **Keep sensitive data out of logs.** Internal logic does not print or log. The server may log
    safe operational details at its boundary. Credentials, prompts, model responses and raw
    provider errors must not enter normal logs or client error messages. Check SDK logs and error
    strings as well as our own.

12. **Test behavior at each boundary.** Use fakes for fast tests and the official OpenAI SDK to
    check the HTTP contract. Test streaming and disconnects through a real local connection as
    well: [HTTPX's ASGI transport](https://github.com/encode/httpx/blob/0.28.1/httpx/_transports/asgi.py)
    buffers the response and cannot prove incremental delivery. Live GigaChat tests run separately
    and require explicit credentials.

13. **Keep dependencies deliberate.** Declare every directly used dependency. Adding a runtime
    dependency or making a significant architectural choice needs a short decision record.
    `msgspec` is currently supplied by Litestar; add it as a direct dependency when our code first
    uses it.

`tests/` contains package tests. `pyproject.toml` and `uv.lock` define dependencies, and
`Justfile` contains commands used locally and in CI.

## References

These sources informed the rules above. The exact rules and exceptions are decisions made for
Any2Giga; the sources do not necessarily recommend the same choices.

### Object design

- Yegor Bugayenko, [Elegant Objects](https://www.yegor256.com/elegant-objects.html), volumes 1
  and 2. The original object design ideas behind rules 1–6.
- Articles by the same author: [class names](https://www.yegor256.com/2015/03/09/objects-end-with-er.html),
  [constructors](https://www.yegor256.com/2015/05/07/ctors-must-be-code-free.html),
  [immutability](https://www.yegor256.com/2014/06/09/objects-should-be-immutable.html),
  [null](https://www.yegor256.com/2014/05/13/why-null-is-bad.html),
  [wrappers](https://www.yegor256.com/2015/02/26/composable-decorators.html) and
  [fakes](https://www.yegor256.com/2014/09/23/built-in-fake-objects.html).
- [convy](https://github.com/deyna256/convy/blob/eb7c63d4042f62b28d6734330ea22759f608cb0f/ARCHITECTURE.md)
  and [wicket](https://github.com/deyna256/wicket/blob/78ee62cc3991ad74137dad57af9620b55701bcad/ARCHITECTURE.md)
  show how those ideas are used in Python. Their rules also informed our own choices.

### Python and API boundaries

- [msgspec Structs](https://msgspec.dev/structs) and
  [`UNSET`](https://msgspec.dev/supported-types#unset): frozen objects, validation, unknown fields
  and the difference between an omitted field and `null` (rules 2, 6 and 7).
- [Python protocols](https://typing.python.org/en/latest/spec/protocol.html) and
  [task cancellation](https://docs.python.org/3.12/library/asyncio-task.html#task-cancellation)
  describe the language features used by rules 4 and 9.
- [Litestar application lifespan](https://docs.litestar.dev/2/usage/applications.html#lifespan-context-managers)
  and the [ASGI HTTP specification](https://asgi.readthedocs.io/en/latest/specs/www.html) cover
  resource lifetime and client disconnects (rules 3, 9 and 10).
- [OpenAI Responses migration](https://developers.openai.com/api/docs/guides/migrate-to-responses),
  [function calling](https://developers.openai.com/api/docs/guides/function-calling) and
  [GigaChat Chat Completions v2](https://developers.sber.ru/docs/ru/gigachat/api/reference/rest/post-chat-v-2)
  describe the API contracts and function data we translate (rules 7 and 8).

### Reliability, privacy and testing

- [HTTP semantics: idempotency](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2) and
  [`Retry-After`](https://www.rfc-editor.org/rfc/rfc9110.html#section-10.2.3),
  [AWS on backoff and jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
  and [OpenAI on rate limits](https://developers.openai.com/api/docs/guides/rate-limits#retrying-with-exponential-backoff)
  explain retry safety and delays (rules 9 and 10).
- GigaChat SDK 0.2.3 source: [retries](https://github.com/ai-forever/gigachat/blob/v0.2.3/src/gigachat/retry.py),
  [authentication](https://github.com/ai-forever/gigachat/blob/v0.2.3/src/gigachat/authentication.py),
  [exceptions](https://github.com/ai-forever/gigachat/blob/v0.2.3/src/gigachat/exceptions.py)
  and [stream parsing](https://github.com/ai-forever/gigachat/blob/v0.2.3/src/gigachat/api/utils.py).
  These details are version-specific and must be checked again on SDK upgrades (rules 9–11).
- [OWASP logging guidance](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
  covers sensitive data in logs (rule 11).
- [OpenAI gateway compatibility](https://learn.chatgpt.com/docs/enterprise/gateway-compatibility)
  covers stream completion, tool calls and useful errors. It describes Codex-specific requirements;
  it does not establish that Any2Giga supports Codex (rule 12).
- [Python package metadata](https://packaging.python.org/en/latest/specifications/pyproject-toml/#dependencies)
  describes how to declare direct dependencies (rule 13).
