#!/usr/bin/env bash
# Create a ready-to-build Electron source snapshot for the electron41 RPM.
#
# This intentionally performs the expensive networked gclient sync outside of
# rpmbuild.  The resulting archive contains source only: no Git metadata and
# no Ninja output.

set -Eeuo pipefail

readonly electron_version_default='41.10.0'
readonly depot_tools_commit='b6aeae1769e1448cf8b53d0d05c4b125fb5e2c93'

electron_version="$electron_version_default"
workdir=''
output_dir="$PWD"
zstd_level=6

usage() {
  cat <<'EOF'
Usage: create-source-artifact.sh --workdir PATH [options]

Create a complete, patched Electron/Chromium source snapshot.  PATH must be a
dedicated directory with substantial free space (plan for at least 150 GiB).
The directory is retained on success and failure, so a failed gclient sync can
usually be resumed by running the same command again.

Options:
  --workdir PATH       Required workspace for the checkout and depot_tools.
  --output-dir PATH    Where to write the archive and .sha256 file (default: .)
  --version VERSION    Electron version without a leading v (default: 41.10.0)
  --zstd-level N       Zstandard level, 1-19 (default: 6)
  -h, --help           Show this help.

Example:
  ./create-source-artifact.sh \
    --workdir /mnt/fast/electron41-work \
    --output-dir /mnt/artifacts/electron41
EOF
}

die() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || die "required command not found: $1"
}

while (($#)); do
  case "$1" in
    --workdir)
      (($# >= 2)) || die '--workdir needs a path'
      workdir="$2"
      shift 2
      ;;
    --output-dir)
      (($# >= 2)) || die '--output-dir needs a path'
      output_dir="$2"
      shift 2
      ;;
    --version)
      (($# >= 2)) || die '--version needs a value'
      electron_version="${2#v}"
      shift 2
      ;;
    --zstd-level)
      (($# >= 2)) || die '--zstd-level needs a value'
      zstd_level="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *) die "unknown option: $1 (use --help)" ;;
  esac
done

[[ -n "$workdir" ]] || die '--workdir is required'
[[ "$electron_version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || die "invalid Electron version: $electron_version"
[[ "$zstd_level" =~ ^([1-9]|1[0-9])$ ]] || die "--zstd-level must be 1 through 19"

for command_name in git tar zstd sha256sum; do
  require_command "$command_name"
done
tar --help | grep -q -- '--exclude-vcs' || die 'GNU tar with --exclude-vcs is required'

mkdir -p "$workdir" "$output_dir"
workdir="$(cd "$workdir" && pwd -P)"
output_dir="$(cd "$output_dir" && pwd -P)"

readonly checkout="$workdir/checkout"
readonly depot_tools="$workdir/depot_tools"
readonly artifact_basename="electron41-source-${electron_version}"
readonly archive="$output_dir/${artifact_basename}.tar.zst"
readonly checksum="$archive.sha256"

if [[ -e "$archive" || -e "$checksum" ]]; then
  die "refusing to replace existing artifact: $archive"
fi

# A partial checkout is deliberately retained. gclient and Git reuse it on a
# later invocation, avoiding a full restart after a transient network failure.
if [[ ! -d "$depot_tools/.git" ]]; then
  git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git "$depot_tools"
fi
git -C "$depot_tools" fetch --quiet origin "$depot_tools_commit"
git -C "$depot_tools" checkout --quiet --detach "$depot_tools_commit"
export PATH="$depot_tools:$PATH"

mkdir -p "$checkout/src"
if [[ ! -d "$checkout/src/electron/.git" ]]; then
  if [[ -e "$checkout/src/electron" ]]; then
    die "$checkout/src/electron exists but is not a Git checkout; move it aside first"
  fi
  git clone --branch "v${electron_version}" --depth 1 \
    https://github.com/electron/electron.git "$checkout/src/electron"
fi

actual_tag="$(git -C "$checkout/src/electron" describe --exact-match --tags HEAD 2>/dev/null || true)"
[[ "$actual_tag" == "v${electron_version}" ]] || die "existing Electron checkout is not v${electron_version} (found ${actual_tag:-unknown})"

cd "$checkout"
gclient config --name src/electron --unmanaged https://github.com/electron/electron
# Do not add --nohooks. Electron's hooks patch Chromium and install its locked
# JavaScript dependencies; the resulting tree is what this artifact captures.
gclient sync -f --with_branch_heads --with_tags

[[ -f src/electron/BUILD.gn ]] || die 'Electron source disappeared during gclient sync'
[[ -f src/components/os_crypt/sync/features.gni ]] || die 'Chromium checkout is incomplete: expected os_crypt features.gni is absent'
grep -Fq '"//electron:*"' src/components/os_crypt/sync/BUILD.gn || \
  die 'Electron Chromium patches were not applied; do not publish this artifact'

manifest="$checkout/SOURCE-MANIFEST.json"
cat >"$manifest" <<EOF
{
  "artifact": "${artifact_basename}",
  "electron_version": "${electron_version}",
  "electron_revision": "$(git -C src/electron rev-parse HEAD)",
  "chromium_revision": "$(git -C src rev-parse HEAD)",
  "depot_tools_commit": "${depot_tools_commit}",
  "created_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "contents": "gclient-synced Electron source, including DEPS and applied hooks; excludes VCS metadata and build outputs"
}
EOF

# `--exclude-vcs` removes every nested .git directory. No build has been run,
# but exclude out/ defensively so rerunning this script never ships objects.
tar --use-compress-program="zstd -T0 -${zstd_level}" \
  --exclude-vcs \
  --exclude='src/out' \
  --transform="s,^,${artifact_basename}/," \
  -C "$checkout" \
  -cf "$archive" src SOURCE-MANIFEST.json

sha256sum "$archive" >"$checksum"
printf 'Created: %s\nSHA-256: %s\nWorkspace retained at: %s\n' \
  "$archive" "$checksum" "$workdir"
