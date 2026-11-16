# Native qualification

These scripts create only disposable local fixtures. PostgreSQL/OpenSearch use pinned official container digests, no published ports, a private no-network container, bounded CPU/memory and cleanup of their own named container/volume. They do not stop or alter existing containers. Native startup can take longer than the audit command runner's 30-second deadline, so the separate qualification coordinator allows 240 seconds per trusted test process.

Create a project-local or temporary Python 3.12 environment and install the pinned Linux AMD64 wheel from requirements-native.txt. Its single hash qualifies that exact wheel/platform; another platform needs its own verified artifact identity.

```sh
python3 -m venv .venv
.venv/bin/pip install --require-hashes -r requirements-native.txt
.venv/bin/python eng/qualify.py --native
```

The fixture covers constraints, bound input, transaction rollback, decimal arithmetic, Parquet, persistence, VARIANT, locked configuration and denied external file access. It does not prove arbitrary SQL isolation, Quack/S3 behavior or spill/load performance.

Outputs are retained under ignored artifacts/. The coordinator binds native result/snapshot identities and assesses the exported evidence through the independent zipapp. Its acceptance command checks the retained native result and snapshot integrity; it does not pretend to rerun the original engine after it has been cleaned up.
