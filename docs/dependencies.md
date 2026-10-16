# Dependency Security

Direct Python runtime dependencies are exact-version pinned in `requirements.txt`; this is not a fully hashed transitive lockfile. Development requirements are separate. The frontend uses a generated npm package lock; install it with npm ci. Resolve and hash all transitives before production, keeping platform wheels and Python versions in mind.

Run `pip-audit -r requirements.txt`, an installed-environment audit, and `npm --prefix frontend audit`. Scan built containers with Trivy, generate an SBOM, inspect external binary versions, and pin scanned image digests. Audit databases are time-dependent and can be unavailable; an unavailable audit is not a passed audit.

Dependabot updates must pass tests, adversarial fixtures, type/build checks and integration gates. Review parser/cryptography patches promptly, check upstream advisories, and document deployment mitigations. Do not auto-merge codec, scanner or cryptographic upgrades without review.

The virtual environment's bundled pip had advisories during setup and was upgraded before re-auditing. pip is tooling, not an application runtime requirement. Keep interpreter patch releases updated separately; Python package audits do not scan the Python interpreter, Windows host, base image or antivirus database.