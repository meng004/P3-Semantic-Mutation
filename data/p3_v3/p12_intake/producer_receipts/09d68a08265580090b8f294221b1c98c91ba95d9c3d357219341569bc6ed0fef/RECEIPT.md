# Producer receipt

neutral_snapshot_id: 09d68a08265580090b8f294221b1c98c91ba95d9c3d357219341569bc6ed0fef
release_commit_sha: d57fa8119e47baf88c5bcff2d67346864cf3672d
verdict: BUILD_UNAVAILABLE

The original archive and build descriptor are present and their SHA-256
values match the consumer lock's bridge record. The normalized source tree
also matches `P3-NORMALIZED-SOURCE-TREE-v1`. The build descriptor has no
command, module, or entry point, so no build or import was run. This lock
is not replaced by a newer release.

## Files checked, not repacked

- archive: `data/p3_v3/p12_intake/archives/09d68a08265580090b8f294221b1c98c91ba95d9c3d357219341569bc6ed0fef.tar`
- descriptor: `data/p3_v3/p12_intake/descriptors/09d68a08265580090b8f294221b1c98c91ba95d9c3d357219341569bc6ed0fef.json`

## Checks

| Check | Expected | Observed | Result |
|---|---|---|---|
| source_archive_sha256 | dd8155d1f7e94b17e467cfb7b797e5d188285cc68b9c6ad003eaf2e0d2b1d482 | same | match |
| build_descriptor_sha256 | 9323b307ebf944e6056e7ea404f63297d2b5e41a3ce039cf002786c7e4fa721d | same | match |
| normalized_source_tree_sha256 | 0bb05eddbaaf341deb2e678328357ee1bceb80ace06c5daa7eb789d5e66f4ef5 | same | match |

Descriptor bytes are exactly `{"ecosystem":"python","language_family":"python"}`.
Missing for a run: a build or import command and the module or entry it
would execute. No new archive was created.

Logs: `logs/01_sha256.*`, `logs/02_normalized_tree.*`.
