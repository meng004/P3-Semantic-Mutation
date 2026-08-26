# P3 Boost.Math Attempt-2 Archive Contract Update Design

**Date:** 2026-08-26

**Status:** USER-APPROVED DESIGN

## Goal

Restore the missing Boost.Math Attempt-2 input from the verified public
upstream commit using a deterministic archive recipe whose bytes can be
reproduced and checked locally. This update changes only the Attempt-2 source
restoration archive identity. It does not authorize another Attempt-2 run or
formal profiling.

## Evidence and fixed upstream identity

- Upstream repository: `https://github.com/boostorg/math.git`
- Witness commit: `04c2c248dfc5e35eeb7638152d5bd7c2985feef2`
- Mainline witness: `03ea9c8d7dff1083facd134c8f641e006b68fdae`
- Common Git root tree: `dc86f3259c84f68ac7c4e2be11a1ed8567011240`
- Excluded path: `build/Jamfile.v2`
- Retained regular-file count: `4396`
- Retained regular-file bytes: `95635487`
- Normalized source-tree SHA-256:
  `93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8`

The witness commit and the mainline witness both resolve to the fixed common
Git root tree. The source projection therefore remains the same controlled
subject; only the tar serialization identity changes.

## Canonical projection recipe

The replacement archive is the byte output of this Git operation against a
clone of the upstream repository:

```text
git archive --format=tar \
  --output=boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar \
  04c2c248dfc5e35eeb7638152d5bd7c2985feef2 \
  -- . ':(exclude)build/Jamfile.v2'
```

The output must be a regular, non-symlink TAR file with mode `0644`, not
group/world writable, at:

```text
/tmp/p3-boost-math-public-source-discovery/content-equivalence-r1/
boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar
```

Its replacement frozen identity is:

- SHA-256: `e97524b457326fdb4d0ccd8f6d83cb33cdad920a76dffc4b508f628a0a70393d`
- bytes: `99092480`
- format: `TAR`

Any mismatch blocks publication to the frozen path. Candidate archives are
created and checked outside that path first.

## Contract boundary

The following active Attempt-2 recovery bindings change together:

1. `ATTEMPT2_ARCHIVE_SHA256` becomes the replacement SHA-256 above.
2. `ATTEMPT2_ARCHIVE_BYTES` becomes `99092480`.
3. The active Attempt-2 recovery specification records this superseding
   archive recipe and identity.
4. Tests assert the replacement identity and reject the superseded identity.
5. The reviewed recovery implementation commit and implementation verdict are
   regenerated because `src/p3_v3/pilot_source.py` changes.

The following identities do not change:

- upstream repository, witness commits, and common Git root tree;
- excluded path and normalized source object;
- retained file count and retained byte count;
- production archive path and production source root;
- claim ceiling (`claims=blocked`, `rq4_supported=false`,
  `formal_denominator_membership=false`);
- no-retry status of the already consumed Attempt-2 invocation.

The 2026-08-17 launch packet and durable source-preparation evidence remain
historical records and are not rewritten. The Attempt-2 recovery amendment
explicitly supersedes only their archive serialization identity for missing
source restoration.

## Data flow

1. Resolve both witness commits and verify their Git tree equals the fixed
   common tree.
2. Generate the candidate archive with the canonical Git command.
3. Verify candidate path type, permissions, TAR format, byte count, SHA-256,
   file count, total file bytes, excluded-path absence, and normalized tree
   hash.
4. Publish the candidate to the frozen archive path only after every check
   succeeds.
5. Run the production source-entry validator without starting Attempt-2.

## Failure handling

- A commit/tree mismatch blocks generation.
- Any candidate identity, layout, metric, or normalized-tree mismatch blocks
  publication.
- An existing different object at the frozen path blocks replacement; it is
  not deleted or overwritten implicitly.
- Contract tests or source-entry validation failure blocks a new recovery
  implementation verdict.
- No Attempt-2 or profiling process is started by this change.

## Verification

The implementation must demonstrate:

1. a focused test fails while the old archive SHA/size are active;
2. the focused test passes after the active constants are updated;
3. the full Attempt-2 source/build/CLI test suites pass;
4. the published archive exactly matches the replacement SHA, size, format,
   permissions, file count, total file bytes, excluded path, and normalized
   source-tree hash;
5. the worktree contains only the explicitly reviewed tracked changes plus
   the canonical implementation verdict and one-time authorization artifacts.

Passing these checks updates the recovery input contract only. A later real
run requires a new explicit run decision and a valid one-time authorization.
