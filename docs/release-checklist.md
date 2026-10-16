# Production Release Checklist

Unchecked items are release blockers or explicitly unsupported scope, not completed work.

- [ ] Start Docker, build both images, run PostgreSQL/Redis/Celery/Nginx integration.
- [ ] Prove ClamAV input/output clean/infected/error behavior with the harmless EICAR test fixture in an authorized isolated environment; verify engine/signature freshness.
- [ ] Remove parser access to service credentials and other users' job directories using a per-job sandbox and narrow result protocol.
- [ ] Test Linux CPU/memory/PID/file-size/timeout enforcement and actual network egress denial.
- [ ] Implement reviewed database migrations, crash/orphan recovery and queue/database reconciliation.
- [ ] Define durable queue semantics, retries, dead jobs, worker loss and API restart recovery.
- [ ] Configure real HTTPS, trusted ingress client identity, CSRF policy, secure cookies, probes and rate/load tests.
- [ ] Add credential rotation, scoped/revocable API keys, account deletion/export and recovery controls as applicable.
- [ ] Fully lock/hash Python transitives, pin scanned image digests, generate SBOM, run Trivy/Bandit and review exceptions.
- [ ] Perform independent security/cryptography review and adversarial native-parser fuzzing.
- [ ] Validate Office/media/libmagic support before enabling those formats; currently unsupported.
- [ ] Validate 7Z/deep archive analysis and safe extraction before enabling extraction; currently prohibited.
- [ ] Validate PDF rasterization/compression and complex sanitization; currently unsupported or conservatively refused.
- [ ] Publish verified UI screenshots without private file content and a hosted-service privacy notice.
- [ ] Demonstrate storage capacity alarms, audit log redaction, retention after outages and encrypted-storage/backups policy.

The baseline provides useful controls and working workflows, but it is not complete implementation of every product-specification requirement.