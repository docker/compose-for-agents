# Refreshing example certificate trust

Rebuild existing example images after pulling the certificate trust updates:

```sh
cd <example>
docker compose build --pull --no-cache
docker compose up -d --force-recreate
```

Stop any previous locally started example containers as appropriate. Updating the
source or a running MCP Gateway does not replace these example images.

The Python examples require certifi 2026.10.19 or newer; the committed uv and
Poetry locks were regenerated with their package managers. Python images refresh
Debian 13 CA certificates and check the installed package is at least
20250419+deb13u1. Their pip installer is also updated to 26.2.2 or newer; uv users
install 0.13.4. The Go example builds with Go 1.26.10 and requires Alpine CA
certificates 20261020-r0 or newer in both build and runtime stages. The Node UI
uses Node 26.12.1 and checks the Debian 12 CA package floor
20250419~deb12u2. These checks fail builds when the configured distribution mirror
cannot supply the required trust update.

These source changes are not a verification receipt for every example or an
existing installation. Before treating an image as remediated, record its digest,
installed runtime and CA package versions, a successful valid-chain TLS check,
and certificate-validation failure for all current compromised-chain fixtures.
Connection failures and HTTP errors do not prove certificate rejection. Check
custom CA settings and bundled trust separately from the operating system store.

The Akka and Spring AI examples use Temurin Java trust stores, which require a
separate vendor-specific verification and rebuild. A newer operating-system CA
bundle alone does not establish that a Java trust store rejects the compromised
intermediates. Their Java images are not cleared by the Python, Go or Node
changes. Third-party images (including the Markdown linter and catalog servers)
also need supplier artifact verification.

References: [certifi release](https://github.com/certifi/python-certifi/releases/tag/2026.10.19),
[uv release](https://github.com/astral-sh/uv/releases/tag/0.13.4),
[Docker security announcements](https://docs.docker.com/security/security-announcements/#docker-sandboxes-response-to-emudhra-ca-compromise).
