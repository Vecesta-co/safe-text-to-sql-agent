# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅        |

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Email: vecesta.co@gmail.com

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will respond within 72 hours and issue a patch within 14 days for confirmed vulnerabilities.

## Security Design

- All SQL is validated against an AST whitelist before execution
- Only `SELECT` statements are allowed (no INSERT/UPDATE/DELETE/DROP)
- Schema introspection is read-only
- Parameterized queries prevent injection
- Quoted string literals are stripped before keyword scanning
