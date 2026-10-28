# Security policy

## Supported versions

The project is in development and has no release yet. Once releases exist, the latest release
receives security fixes while the version is `0.x`.

## Reporting a vulnerability

Report vulnerabilities privately to [literallybugcreator@gmail.com](mailto:literallybugcreator@gmail.com).
Describe the affected version, impact and steps to reproduce. Do not include real credentials,
private prompts or model responses.

## Security boundaries

The planned gateway will hold GigaChat credentials and handle client requests and model responses.
Credentials, prompts and responses must not appear in ordinary logs or public error details. TLS
verification, client access, request limits and the lifecycle of stored conversations are part of
the design and must be implemented and tested before the gateway is used.
