# electron41 RPM packaging

This package provides parallel-installable Electron 41 runtime and development
RPMs: `electron41` and `electron41-devel`.

> **Publication scope:** this is a packaging proof of concept only. No public
> Electron source artifact or binary RPM is published or supported by this
> repository. Public binary distribution remains blocked on the legal,
> provenance, codec, and security work documented in
> [PUBLIC_RELEASE_COPR_AUDIT.md](PUBLIC_RELEASE_COPR_AUDIT.md).

Build with:

```bash
make fc
```

Electron's documented source build synchronizes Chromium dependencies through
`gclient` and runs Electron's DEPS hooks.  The hooks are required: they apply
Electron's patches to Chromium and install the locked JavaScript dependencies.
This is a very large networked COPR/Mock build and is not yet a fully vendored
Fedora-reviewable source package.

## Build time and network use

This package builds Electron/Chromium itself.  The initial `gclient sync` may
download tens of GiB and the compile can take hours.  A normal Electron
application build does **not** normally do this: Electron Forge / electron-
builder download a matching prebuilt Electron runtime once (and cache it), then
package the application into it.

For repeated source-RPM builds, configure Mock to bind-mount a persistent,
writable directory and set `GIT_CACHE_PATH` to that mounted directory before
`gclient sync`.  This avoids re-downloading Git objects, though each fresh
checkout still has to populate its worktree and Git index.  The cache must not
live only under `%{_builddir}`, since Mock removes that directory between
builds.

For a network-free RPM build, make a separate, versioned source snapshot after
one successful `gclient sync` **with hooks** (including Electron, Chromium and
all DEPS), compress it with `tar --zstd`, and add that archive as a checked-in
or internally hosted `Source` artifact.  The spec can unpack that snapshot
instead of invoking `gclient`.  It will be very large, must carry the licenses
for all bundled code, and is generally unsuitable for Fedora/COPR review; it
is appropriate only for an internal RPM pipeline.

### Creating an internal source artifact

Use `create-source-artifact.sh` on a machine with at least 150 GiB of free
space and a reliable network connection:

```bash
./create-source-artifact.sh \
  --workdir /mnt/fast/electron41-work \
  --output-dir /mnt/artifacts/electron41
```

It clones the exact Electron tag, pins depot_tools to the same revision as the
spec, runs `gclient sync` **with hooks**, and writes both a
`electron41-source-41.10.0.tar.zst` archive and its `.sha256` checksum. The
archive contains the `src/` source tree plus `SOURCE-MANIFEST.json`; it excludes
all nested `.git` data and `out/` build output. The workspace is intentionally
retained so a failed sync can be resumed. Do not point `--workdir` at a
directory containing other files. It also keeps `git-cache/`, and creates a
completion stamp after a successful sync; rerunning the command reuses these
and does not re-download dependencies or rerun `gclient`. The archive includes
`GCLIENT-REVINFO.txt` and records its host OS/architecture because hooks can
download platform-specific build inputs. If the archive and checksum already
exist and verify, a repeated invocation exits successfully without doing work.

### Measured Electron 41.10.0 artifact run

The first successful `linux-x86_64` run completed on 2026-09-05. This is a
useful capacity baseline, not a build-time guarantee:

| Measurement | Result |
| --- | ---: |
| Host CPU | Intel Core i5-10210U (4 cores / 8 threads) |
| Elapsed time (`real`) | 56m 54s |
| CPU time (`user` / `sys`) | 139m 08s / 19m 12s |
| Persistent workspace | 54 GiB |
| Checkout / Git cache / depot_tools | 25 GiB / 28 GiB / 1.0 GiB |
| Produced `.tar.zst` | 7.6 GiB (`zstd`: 7.51 GiB) |

The first measured artifact was later refreshed with missing prepared build
inputs. The canonical artifact used for the successful RPM build is
`electron41-source-41.10.0.tar.zst`, size 8,085,991,676 bytes, with SHA-256:

```text
928d25dc4422c56bb43a952b1eef98a2686b4e6e659f401e2e470a3d86fa4778
```

That digest is committed in
`electron41-source-41.10.0.tar.zst.sha256`. Its manifest records Electron commit
`015e7a65b770b8ca81c6adc7645b83b405e7f016`, Chromium commit
`3a3dae94a80d53bce850c868789fe4ab7fc0b1a7`, and the Chromium release
`146.0.7680.216` in `GCLIENT-REVINFO.txt`.

## Building the RPM from the artifact

The RPM spec now builds from the prepared archive rather than running
`gclient` in Mock. On the artifact-producing machine, use:

```bash
make build
```

`make` verifies the configured artifact against the checksum committed in this
directory, then stages a real copy for SRPM creation (a reflink is used where
the filesystem supports it). To use an artifact stored elsewhere, provide its
local path explicitly:

```bash
make build ARTIFACT=/path/to/electron41-source-41.10.0.tar.zst
```

The current artifact is `linux-x86_64` only, so the RPM deliberately supports
`x86_64` only. Mock still needs enough free disk for the expanded sources and
the Chromium compile; the 95 GiB currently free on this host may be tight.
The SRPM staging directory defaults to `/mnt/fast/electron41-rpmbuild`, rather
than `/tmp`, because the SRPM itself embeds the 7.6 GiB archive. Override it
with a path whose final component is `electron41` or starts with
`electron41-`; this naming requirement protects destructive cleanup operations.

The prepared x86_64 artifact includes Chromium's Debian amd64 sysroot and
bundled LLVM toolchain. If an older artifact fails GN/Ninja with a missing
`debian_bullseye_amd64-sysroot` or
`third_party/llvm-build/Release+Asserts/bin/llvm-strip`, recreate it without
re-downloading the Git checkout:

```bash
./create-source-artifact.sh \
  --workdir /mnt/fast/electron41-work \
  --output-dir /mnt/artifacts/electron41 \
  --refresh
```

`--refresh` installs only missing prepared inputs (including the sysroot and
LLVM toolchain), then
writes temporary archive/checksum files and replaces the old pair only after
a successful archive operation.
