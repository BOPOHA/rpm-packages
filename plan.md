# Freelens RPM unbundling plan

## Goal

Move from the upstream Electron bundle toward a Fedora-native package without
unverified third-party executable payloads. Each phase must retain a working
Freelens installation on the supported Fedora target before the next starts.

## Package variants

Maintain two mutually exclusive RPM variants from the same source and release:

- `freelens-bundled` is the compatibility package. It follows the upstream
  Electron build and retains its bundled Electron/Chromium runtime and helper
  executables, apart from low-risk cleanup already proven safe. It is the
  fallback and the package to use when upstream-version compatibility matters.
- `freelens-native` is the Fedora-native package. It uses system or separately
  built RPM components wherever practical, beginning with a compatible Electron
  runtime and then the Kubernetes helpers and native Node modules.

They must not be co-installable: both own the `freelens` command, desktop ID,
configuration location, and application data. `freelens-bundled` provides the
unqualified `freelens` capability and obsoletes older unqualified packages so
that RPM-installed GitHub releases migrate transactionally. Both variants
declare reciprocal `Conflicts:` by their exact package names.

Use explicit build targets such as `make fc-bundled` and, once its spec exists,
`make fc-native`, each producing a distinct SRPM/binary RPM and rpmlint report.
Do not call the native variant equivalent until its phase-specific tests pass.

## Phase 1: low-risk cleanup — implemented

- Use Fedora's `vulkan-loader` (`libvulkan.so.1`) instead of Electron's bundled
  Vulkan loader.
- Remove `@electron-internal/extract-zip` native add-ons that do not match the
  RPM's Linux architecture. Keep only the glibc add-on for the target arch.
- Retain the Electron graphics stack, native Node modules, and Kubernetes
  helpers for now.

Validation: run `make fc`, install the RPM in a test environment, and start
Freelens with both GPU acceleration and `--disable-gpu` to verify startup.

## Phase 2: Fedora Electron runtime — current priority

- Fedora 44 currently has no `electron` or `electron-devel` package in the
  enabled repositories, while Freelens 1.10.3 requires Electron 41.10.0.
- The `electron41.spec` bootstrap provides parallel-installable `electron41`
  and `electron41-devel` packages. It pins Electron and depot_tools, while
  gclient synchronizes Electron's pinned Chromium DEPS at build time.
- Audit Electron's generated Chromium third-party notice before publication;
  the initial aggregate license expression deliberately does not claim the
  runtime is MIT-only.
- Do not substitute individual Chromium private libraries; the native variant
  must use a whole compatible system Electron runtime.

Validation: reproducible Electron RPM build, then Freelens startup under that
runtime with GPU, software rendering, Wayland/X11, terminal, and extensions.

## Phase 3: Kubernetes helper packages — deferred

- Build `freelens-k8s-proxy` from source inside `freelens-native`.
- Use Fedora Helm 4.2.2 and Kubernetes 1.36 client packages via controlled
  resource-path symlinks in `freelens-native`. Keep the bundled variant's
  pinned resources unchanged.

Validation: cluster connection, kubectl operations, Helm repository/chart/
release operations, and proxy-backed features against supported Kubernetes
versions.

## Phase 4: native Node add-ons

- Build `node-pty` and `@electron-internal/extract-zip` from source for the
  Electron ABI used by the native variant.
- Add the required compiler, Node/Electron headers, and reproducibility checks.

Validation: terminal/exec sessions, archive extraction, and a clean rebuild in
Mock for every supported architecture.

## Phase 5: native variant integration

- Patch the native build to use the validated system Electron runtime and its
  compatible library set; do not substitute individual Chromium private
  libraries piecemeal.
- Remove the upstream Electron ZIP and its bundled Chromium graphics/codec
  libraries from the native RPM only after the system-Electron build is proven.

Validation: full UI smoke test, GPU and software rendering, Wayland/X11,
terminal support, extensions, and update the RPM dependency/provides policy.

## Phase 6: maintenance policy

- Keep every remaining external artifact source-versioned and independently
  verifiable.
- Require Mock builds and installed-RPM smoke tests for each Freelens, Electron,
  or Kubernetes-helper update.
