# electron41 RPM packaging

This package provides parallel-installable Electron 41 runtime and development
RPMs: `electron41` and `electron41-devel`.

Build with:

```bash
make fc
```

Electron's documented source build synchronizes Chromium dependencies through
`gclient`. This is a very large networked COPR/Mock build and is not yet a
fully vendored Fedora-reviewable source package.
