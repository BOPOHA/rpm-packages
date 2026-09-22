# RPM packages

This repository contains independent Fedora/COPR RPM package definitions.
Each package directory owns its spec, build commands, documentation, and build
results.

| Directory | RPMs | Status |
| --- | --- | --- |
| [freelens-bundled](freelens-bundled) | `freelens-bundled` | Compatibility package; rebuild pending after layout migration |
| [freelens-native](freelens-native) | `freelens-native` | Thin package using the separate `electron41` runtime |
| [freelens-native-tools](freelens-native-tools) | `freelens-native-tools` | Independently updated Kubernetes helper binaries for native FreeLens |
| [electron41](electron41) | `electron41`, `electron41-devel` | Source-build bootstrap |

Run package commands from its directory, for example:

```bash
cd freelens-bundled && make fc
cd freelens-native && make fc
cd freelens-native-tools && make fc
cd electron41 && make fc
```
