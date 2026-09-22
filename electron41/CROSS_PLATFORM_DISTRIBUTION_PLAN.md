# Cross-platform build, distribution, cost, and legal review

Status: investigation and decision document. It is intentionally separate from
the package README so it can be reviewed and amended independently.

## Scope

Build Electron 41 and a future Freelens package for:

- Linux x86_64 RPMs;
- Linux aarch64 RPMs; and
- macOS Apple Silicon distribution.

The current Electron RPM uses a prepared, hook-complete Chromium/Electron
source artifact. The artifact is about 7.6 GiB compressed and is not a normal
Fedora-reviewable source tree.

## Artifact matrix

Create and retain a separate prepared artifact for each host/target platform
family. Chromium hooks download architecture- and host-specific inputs,
including the sysroot, LLVM toolchain, GN, and native dependencies.

| Deliverable | Separate artifact | Build host | Package output |
| --- | --- | --- | --- |
| Linux x86_64 | Yes | Native x86_64 Linux | RPM |
| Linux aarch64 | Yes | Native aarch64 Linux | RPM |
| macOS Apple Silicon | Yes | Native Apple Silicon macOS with Xcode | DMG, PKG, or signed zip |

Do not reuse a Linux artifact for macOS. For the same CPU architecture across
Fedora and AL2023, one artifact may work, but that is a tested compatibility
claim rather than a guarantee: build dependencies and host toolchain behavior
can still differ.

## Proposed pipeline

```text
native platform builder
  -> gclient sync and hooks
  -> prepared artifact + SHA-256 + source manifest + SBOM/license report
  -> versioned immutable S3 object
  -> verified RPM or macOS packaging build
  -> signed package and repository/release publication
```

Use persistent storage for the checkout and Git cache. Builders should upload
only verified immutable artifacts and associated metadata. Packaging jobs must
verify the checksum before use and must not fetch unpinned dependencies during
the RPM build.

## Build infrastructure

- Standard GitHub-hosted runners are unlikely to be adequate: this workflow
  needs about 150 GiB of workspace and can take hours.
- Prefer self-hosted GitHub Actions runners or dedicated EC2 builders with
  fast local NVMe or sufficiently large gp3/EBS volumes.
- Build aarch64 natively, for example on AWS Graviton. Do not use QEMU for
  production Electron builds.
- Use an Apple Silicon Mac runner for macOS ARM. Xcode/SDK files stay on that
  host; they must not be copied into source artifacts or S3.
- Record actual elapsed time, CPU time, peak RAM, peak disk, and artifact size
  for every platform before committing to capacity or cost assumptions.

## Storage and delivery

Suggested S3 key layout:

```text
electron41/<electron-version>/<platform>/<arch>/
  electron41-source-<version>.tar.zst
  electron41-source-<version>.tar.zst.sha256
  SOURCE-MANIFEST.json
  SBOM.spdx.json
  LICENSE-REPORT.md
```

Enable object versioning, encryption, lifecycle retention, and restricted IAM
write access. Use CloudFront only when a public download is justified. For
private build inputs, direct S3 access from the builders is simpler and avoids
unnecessary public egress.

Indicative, region-dependent costs to validate against current AWS pricing:

- S3 Standard is commonly about USD 0.023 per GB-month. Three 8 GiB artifacts
  are roughly 24 GiB, or about USD 0.55/month; ten retained versions are about
  USD 5.50/month.
- Artifact egress can dominate storage costs. An 8 GiB CloudFront download may
  cost roughly USD 0.70 depending on region and price tier.
- Compute cost is `hourly builder price * measured build hours`, plus block
  storage. Use actual measurements from x86_64 and ARM trials rather than
  estimates.

## Legal and publication gates

This is not legal advice; obtain a qualified legal review before any public
release.

1. The prepared artifact redistributes all hook-downloaded sources and binary
   inputs. Maintain source revisions, hashes, an SBOM, and a license inventory.
2. The current Electron configuration enables proprietary codecs and builds
   WebRTC/video support. Review codec-patent, export, and redistribution risk
   before public COPR, S3, or CloudFront publication.
3. Audit all Freelens inputs: Corepack, Kubernetes tools, Electron runtime,
   native modules, source availability, licenses, checksums, and redistribution
   terms.
4. Verify Electron and Freelens trademark/branding permissions separately from
   the software licenses.
5. Apple SDK/Xcode inputs cannot be redistributed; macOS release also requires
   a code-signing and notarization plan.
6. Public COPR requires auditable, redistributable inputs. The current
   multi-gigabyte prepared-artifact route should be treated as internal/private
   until that review is complete.

## Freelens integration decision

`freelens-bundled` currently builds and ships its own Electron runtime; it does
not depend on `electron41`. A true dependency requires a separate effort to:

- package the app payload without Electron;
- launch it through Electron 41;
- preserve matching Electron/Node ABI for native modules; and
- validate the resulting runtime layout and licenses.

Until that work is complete, keep the package explicitly named and documented
as bundled, and treat it as a separate legal/compliance review target.

## TODO checklist

- [ ] Finish and smoke-test the current x86_64 Electron RPM.
- [ ] Define and implement the artifact metadata contract.
- [ ] Produce and validate a native aarch64 artifact and RPM.
- [ ] Measure build resources and update the cost model with real figures.
- [ ] Create S3 IAM, versioning, lifecycle, and checksum-verification policy.
- [ ] Decide internal/private versus public artifact distribution.
- [ ] Package Corepack and remove download-during-build from Freelens.
- [ ] Decide whether to refactor Freelens to use `electron41`.
- [ ] Design the macOS ARM build, signing, and notarization workflow.
- [ ] Complete license, patent, trademark, export, and COPR publication review.
- [ ] Add automated per-platform build, install, smoke, and update tests.
