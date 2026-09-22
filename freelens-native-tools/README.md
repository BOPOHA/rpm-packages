# freelens-native-tools RPM packaging

This package supplies the three version-pinned helper executables used by
`freelens-native`:

- kubectl 1.36.2
- Helm 4.2.2
- FreeLens Kubernetes proxy 1.8.0

They install in FreeLens's private resource directory:

```text
/usr/lib64/freelens-native/x64/
```

This is intentional. FreeLens resolves these helpers relative to its own
resources path, and placing generic names such as `kubectl` or `helm` in
`/usr/bin` would conflict with their dedicated Fedora packages.

## Updating a helper

Update the relevant version macro and source URL in `freelens-native-tools.spec`,
increment `Release`, then build only this package:

```bash
make fc
```

The spec downloads upstream release checksums and verifies every binary during
the RPM build. No FreeLens application rebuild is needed.

`freelens-native-tools` conflicts with `freelens-bundled`, just as the native
application package does.
