# Electron 41 public release and Fedora COPR audit

Audit date: 2026-09-21

This document records the current technical, legal, packaging, and
infrastructure status so work can continue in a later session. It is not legal
advice; public distribution should be reviewed with Fedora Legal or qualified
counsel.

## Executive decision

- The Linux x86_64 Electron 41 RPM build works locally.
- The packaging-code repository can be made public after a small repository
  hygiene pass.
- The current prepared source artifact and resulting RPM should **not** be
  published through public Fedora COPR yet.
- Public COPR is technically plausible after producing a Fedora-safe build,
  completing the license/provenance audit, and obtaining a powerful builder.

## Verified working state

The following work has been completed and verified:

- Electron 41.10.0 compiled successfully on Fedora 44 x86_64.
- RPMs were produced:
  - `electron41-41.10.0-1.fc44.x86_64.rpm`
  - `electron41-devel-41.10.0-1.fc44.x86_64.rpm`
- Both RPM header and payload SHA-256 digests passed verification.
- The extracted runtime reported `v41.10.0`.
- `ldd` found no unresolved runtime libraries on the build host.
- The runtime RPM is approximately 86 MiB compressed and 329 MB installed.
- The devel RPM is approximately 285 KiB compressed.
- Normal Ninja builds are limited to four jobs to fit a 16 GiB workstation.
- A completed build tree can be packaged without recompilation using:

  ```bash
  rpmbuild -bb --noprep --noclean \
    --define 'electron_skip_build 1' \
    ~/rpmbuild/SPECS/electron41.spec
  ```

Important: `--noprep --noclean` alone still executes `%build`.

Relevant packaging commits:

- `5aa7f81 Expose bundled GN to Electron helper scripts`
- `3ec044e Make Electron RPM rebuilds memory-safe`

## Current status by area

| Area | Status | Finding |
| --- | --- | --- |
| Local x86_64 compilation | Pass | Electron and all requested distribution targets completed. |
| RPM generation | Pass | Runtime and devel RPMs were generated and verified. |
| Basic runtime smoke test | Pass | Extracted binary reports `v41.10.0`; no unresolved libraries. |
| Git artifact hygiene | Pass | Source archive and RPMs are ignored and have never been committed. |
| Repository licensing | Blocked | No top-level license covers the packaging scripts, spec, Makefiles, and documentation. |
| Artifact provenance | Blocked | README and ignored working copy refer to older artifact revisions. |
| Publicly reproducible source | Blocked | `Source0` has no immutable public URL and the source artifact is not available from Git. |
| Package license metadata | Blocked | `LicenseRef-Electron-ThirdParty` is not a valid accepted identifier. |
| Codec/patent review | Blocked | Current build enables Chrome FFmpeg branding, proprietary codecs, H.264, and HEVC. |
| Source/binary inventory | Blocked | Prepared archive contains thousands of downloaded or generated binary-like files. |
| Clean Mock/SRPM build | Not proven | Successful build used a local prepared tree; the complete SRPM-to-Mock path has not passed. |
| COPR capacity | Needs approval | Powerful builders are the appropriate tier for Chromium/Blink. |
| Freelens integration | Blocked | Current Freelens package still bundles Electron and performs networked build downloads. |
| Linux aarch64 | Not implemented | Requires a separately prepared native aarch64 artifact and RPM validation. |
| macOS Apple Silicon | Not implemented | Requires native macOS build, signing, notarization, and separate artifacts. |

## Canonical successful artifact

The artifact used for the successful RPM build is:

```text
File: electron41-source-41.10.0.tar.zst
Size: 8,085,991,676 bytes (approximately 7.6 GiB)
SHA-256: 928d25dc4422c56bb43a952b1eef98a2686b4e6e659f401e2e470a3d86fa4778
Created UTC: 2026-09-20T13:55:12Z
Host: Linux x86_64
Electron revision: 015e7a65b770b8ca81c6adc7645b83b405e7f016
Chromium revision: 3a3dae94a80d53bce850c868789fe4ab7fc0b1a7
depot_tools revision: b6aeae1769e1448cf8b53d0d05c4b125fb5e2c93
```

Current provenance inconsistency:

- `~/rpmbuild/SOURCES/electron41-source-41.10.0.tar.zst` is the successful
  canonical artifact and matches the SHA-256 above.
- `/mnt/artifacts/electron41/` contains the matching checksum but the archive
  was moved away.
- The ignored archive in the repository is older and has a different hash.
- `README.md` records an older artifact hash.

Before release, restore one immutable canonical artifact/checksum pair and
update all documentation to match it. For a public-safe codec rebuild, assign a
new artifact revision instead of silently replacing this one.

## Prepared artifact audit

The successful archive contains:

```text
Total members: 1,222,039
Binary-like members: 4,361
```

Examples include:

- Debian amd64 sysroot libraries;
- Chromium LLVM and Rust toolchains;
- instrumented libraries;
- native Electron test-fixture `.o`, `.node`, and `.so` files;
- JavaScript dependency trees installed by hooks;
- host- and architecture-specific executables.

The artifact is therefore more than a source snapshot. It is a prepared,
platform-specific build input assembled by `gclient` hooks. Every redistributed
component needs an acceptable license and redistribution basis. The claim that
the artifact excludes build outputs should also be narrowed: it excludes
`src/out`, but nested generated fixture outputs remain.

## Codec configuration: current public-release blocker

The effective successful build configuration includes:

```text
proprietary_codecs = true
ffmpeg_branding = "Chrome"
rtc_use_h264 = true
enable_platform_hevc = true
enable_hevc_parser_and_hw_decoder = true
enable_mse_mpeg2ts_stream_parser = true
enable_widevine = false
```

Electron's release GN arguments enable proprietary codecs by default. Fedora's
Chromium package takes the opposite approach: it creates a cleaned source
archive and builds with proprietary codecs disabled and Chromium FFmpeg
branding.

Before public Fedora COPR publication:

1. Define a Fedora-safe GN argument set.
2. Disable proprietary codecs and use Chromium FFmpeg branding.
3. Review H.264, HEVC, MPEG transport-stream, and related code with Fedora
   Legal.
4. Determine whether disabled-but-present codec sources may remain or whether
   a Fedora-style cleaned source archive is required.
5. Produce a new artifact and rebuild the RPM from that artifact.

## RPM quality audit

`rpmlint` reported six errors and seven warnings. Important findings:

- `LicenseRef-Electron-ThirdParty` is invalid.
- `libvulkan.so.1` is reported as unstripped; its split-DWARF companions are
  absent from the distribution archive.
- `chrome-sandbox` triggers the
  `missing-call-to-setgroups-before-setuid` check.
- Documentation and a manual page for `electron41` are missing.
- Explicit `alsa-lib` and `libnotify` dependencies are flagged.
- Several spelling checks incorrectly interpret “JS”.

The packaged `chrome-sandbox` currently has mode `0755`, not setuid mode. Its
runtime sandbox behavior must be tested after a real RPM installation. Do not
change it to setuid without a security review and comparison with Fedora's
Chromium packaging.

Automatic debuginfo packaging is disabled because `electron_dist_zip` omits
the `.dwo` files required by Fedora's GDB indexer. A future Fedora-quality
package should either produce a complete debuginfo source or explicitly retain
the current no-debuginfo decision with documentation.

## Public Git repository decision

Publishing the packaging-code repository is feasible after these changes:

1. Add a top-level license for original repository content.
2. Add a short third-party/trademark disclaimer.
3. Update the Electron README and root package-status table.
4. Decide whether to commit this audit and
   `CROSS_PLATFORM_DISTRIBUTION_PLAN.md`.
5. Resolve the unrelated modified `freelens-bundled/rpmlint.report.txt`.
6. Keep source archives, SRPMs, RPMs, keys, credentials, and build trees
   ignored.
7. Repeat secret and large-object history scans before pushing.

Checks already performed:

- Only 15 files are currently tracked in the full `rpm-packages` repository.
- No Electron archive or RPM was found in Git history.
- A basic tracked-file secret-marker scan found no obvious credentials or
  private keys.
- The Git remote is currently only a local `file://` remote.

Publishing the small packaging repository is legally distinct from publishing
the 7.6 GiB prepared artifact or the resulting binary RPM.

## Fedora COPR technical feasibility

Official COPR documentation states:

- default build timeout: 5 hours;
- Fedora COPR maximum timeout: 50 hours (`180000` seconds);
- regular builder disk: approximately 140 GB;
- powerful builder disk: approximately 280 GB;
- Blink-based browsers are an explicit powerful-builder use case;
- powerful builders support x86_64, aarch64, and ppc64le and require an admin
  request;
- the CLI `--memory` option currently has no effect.

Measured local footprint:

```text
Prepared archive: 7.6 GiB
Extracted source plus build output: 81 GiB
RPM BUILDROOT: 316 MiB
Runtime RPM: 86 MiB
Observed failed high-parallelism build peak: 13.2 GiB RAM
Safe workstation parallelism: ninja -j4 on 16 GiB RAM
```

A regular 140 GB builder is marginal once the SRPM, source archive, extracted
tree, buildroot, package-manager cache, and operating-system image coexist.
Use a powerful 280 GB builder for the pilot.

No documented public maximum SRPM upload size was found. An approximately
8 GiB SRPM is unusual enough that COPR administrators should approve the plan
before upload. The production COPR API did not advertise the newly implemented
direct binary-RPM upload endpoint, so the plan must not rely on that feature.

Recommended COPR pilot settings:

```text
Architecture: x86_64 only
Builder class: powerful/on-demand
Timeout: 180000 seconds
Ninja jobs: 4 initially
Build network: disabled after all sources are in the SRPM
Source delivery: immutable HTTPS URL or administrator-approved SRPM upload
```

## COPR legal policy implications

COPR does not require packages to follow every Fedora Packaging Guideline, but
it requires the uploader to ensure that:

- they have the right to upload and use every component;
- licenses are on Fedora's acceptable-license list;
- no Fedora Not-Allowed Item is included;
- the project does not violate third-party rights or applicable law; and
- the resulting repository can legally be public.

The current package fails the readiness test because:

- proprietary/patent-sensitive codecs are enabled;
- the generic third-party `LicenseRef` is not valid license metadata;
- downloaded toolchain, sysroot, Node modules, and binaries lack a consolidated
  redistribution audit;
- no SPDX SBOM or complete license report exists;
- the public source location and immutable provenance contract are undefined.

Required legal/compliance outputs:

- SPDX SBOM for source artifact and binary RPM;
- actual SPDX license expression for the RPM;
- third-party license inventory and notices;
- redistribution review for LLVM, Rust, sysroot, generated native modules, and
  every bundled binary;
- codec/patent assessment;
- Electron and Freelens trademark/branding review;
- export-control review for cryptographic components where applicable;
- written Fedora Legal/COPR administrator guidance before publication.

## Freelens status

The Electron RPM does not complete the overall Freelens project.
`freelens-bundled` currently:

- builds and ships its own Electron runtime;
- does not depend on `electron41`;
- installs Corepack from npm during `%build`;
- runs pnpm with networked dependency resolution;
- downloads or bundles kubectl, Helm, and Kubernetes proxy executables;
- declares x86_64 and aarch64 but invokes an x64 Electron Builder target;
- requires its own license, source, binary, codec, and trademark review.

To use `electron41` as a dependency, create an unbundled Freelens variant that:

1. packages only the application payload;
2. launches through `/usr/bin/electron41`;
3. rebuilds or validates native modules against Electron 41's Node ABI;
4. removes download-during-build behavior;
5. packages helper executables independently or builds them from audited
   source;
6. tests upgrades and runtime compatibility.

## Ordered continuation plan

### Phase 1: repository publication

- [ ] Choose and add a repository license.
- [ ] Add third-party and trademark disclaimers.
- [ ] Update stale README artifact metadata.
- [ ] Commit the audit/plan documents if desired.
- [ ] Resolve the dirty Freelens report.
- [ ] Repeat secret and Git-history large-object scans.
- [ ] Add a real public Git remote and publish the code-only repository.

### Phase 2: canonical artifact and provenance

- [ ] Restore the successful artifact and checksum as an immutable pair.
- [ ] Preserve the embedded manifest and `GCLIENT-REVINFO.txt` separately.
- [ ] Define an S3 object-key/versioning policy.
- [ ] Add checksum and optional signature verification to the public workflow.
- [ ] Generate SBOM and license-report outputs.

### Phase 3: Fedora-safe Electron variant

- [ ] Define free-codec GN arguments.
- [ ] Compare source-cleaning behavior with Fedora Chromium.
- [ ] Obtain Fedora Legal guidance.
- [ ] Produce a new cleaned/prepared source artifact.
- [ ] Rebuild and run RPM/license/rpmlint tests.

### Phase 4: clean packaging validation

- [ ] Build an SRPM from the canonical artifact.
- [ ] Build the SRPM in a fresh local Mock chroot with networking disabled.
- [ ] Record peak disk, RAM, CPU, and elapsed time.
- [ ] Install both RPMs in a clean Fedora VM/container.
- [ ] Test `electron41 --version` without agent sandbox restrictions.
- [ ] Test a minimal Electron JavaScript application.
- [ ] Test Chromium sandbox behavior.
- [ ] Resolve or explicitly document each actionable rpmlint finding.

### Phase 5: COPR pilot

- [ ] Open a COPR issue describing the 8 GiB SRPM and resource profile.
- [ ] Request powerful-builder matching for the project/package.
- [ ] Confirm acceptable source upload/URL method and storage limits.
- [ ] Create an x86_64-only test project or side repository.
- [ ] Use a 50-hour timeout and four Ninja jobs initially.
- [ ] Verify COPR signatures, metadata, installability, and repository updates.
- [ ] Publish only after legal/compliance approval.

### Phase 6: application and additional platforms

- [ ] Refactor Freelens to use `electron41` or explicitly retain a bundled
  variant.
- [ ] Remove Corepack/pnpm/helper downloads from RPM `%build`.
- [ ] Produce and validate a native Linux aarch64 artifact and RPM.
- [ ] Design the macOS Apple Silicon build, signing, and notarization pipeline.
- [ ] Establish Electron/Freelens security-update and rebuild SLAs.

## References

- [COPR user documentation](https://docs.copr.fedorainfracloud.org/user_documentation.html)
- [COPR powerful builders](https://docs.copr.fedorainfracloud.org/user_documentation/powerful_builders.html)
- [Fedora allowed licenses](https://docs.fedoraproject.org/en-US/legal/allowed-licenses/)
- [Fedora not-allowed licenses](https://docs.fedoraproject.org/en-US/legal/not-allowed-licenses/)
- [Fedora: What can be packaged](https://docs.fedoraproject.org/en-US/packaging-guidelines/what-can-be-packaged/)
- [Fedora Chromium spec](https://src.fedoraproject.org/rpms/chromium/raw/rawhide/f/chromium.spec)

