# RPM packages

This repository contains independent Fedora/COPR RPM package definitions.
Each package directory owns its spec, build commands, documentation, and build
results.

| Directory | RPMs | Status |
| --- | --- | --- |
| [freelens-bundled](freelens-bundled) | `freelens-bundled` | Compatibility package; rebuild pending after layout migration |
| [electron41](electron41) | `electron41`, `electron41-devel` | Source-build bootstrap |

Run package commands from its directory, for example:

```bash
cd freelens-bundled && make fc
cd electron41 && make fc
```

The native Freelens work and shared migration plan are recorded in
[plan.md](plan.md).
