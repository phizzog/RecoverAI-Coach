# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please report it responsibly.

### How to Report

1. **Do NOT** open a public issue for security vulnerabilities
2. Email the maintainers directly or use GitHub's private vulnerability reporting feature
3. Include as much detail as possible:
   - Type of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- Acknowledgment within 48 hours
- Regular updates on the status
- Credit in the security advisory (if desired)

### Scope

This security policy applies to:
- The main application code
- API endpoints
- Data handling and storage
- Authentication mechanisms

### Out of Scope

- Third-party dependencies (report to the respective maintainers)
- Social engineering attacks
- Physical security

## Security Best Practices for Users

1. **Never commit secrets** - Always use environment variables
2. **Use strong API keys** - Rotate them periodically
3. **Secure your MongoDB** - Use proper authentication and network rules
4. **Keep dependencies updated** - Run `npm audit` and `pip audit` regularly
