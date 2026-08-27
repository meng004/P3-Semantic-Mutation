# P3 RQ4 Frozen-Release Eligibility Decision

## Terminal status

`RQ4_CONFIRMATORY_INELIGIBLE_FROZEN_RELEASE`

The pinned P12 successor release is origin-valid and bridge-valid, but its
35 formal items cannot satisfy the prespecified floor of 60 `P12_PAIRED`
real-fault families. Primary confirmatory RQ4 is therefore ineligible on this
frozen release. P12 evidence may be retained only for descriptive, sensitivity,
or case-series use under the existing contract. No outcome was opened and no
cohort member was replaced.

## Frozen identities

- P3 evidence snapshot: `25f0ebf5944328aa5b436c810739c8f9176213a9`
- P12 repository: `github.com/meng004/P12-Defect4MR`
- P12 release commit: `d57fa8119e47baf88c5bcff2d67346864cf3672d`
- P12 bridge verification: `PASS`
- Verified bridge SHA-256: `aba70e89b603866f6171ee93a1004d04954e1a3e90b093ba1db889da17690000`

## Mechanical eligibility result

| Quantity | Frozen value |
|---|---:|
| P12 bridge `eligible_item_count` | 35 |
| Number of bridge records | 35 |
| Records with `eligible_for_criterion=true` | 35 |
| Required `P12_PAIRED` real-fault families | at least 60 |
| Arithmetic upper-bound comparison | `35 < 60` |

`eligible_for_criterion=true` means that an item is permitted to enter P3's
criterion-construction process. It does not mean that the exact-version profile
is complete, that the item is already in `P12_PAIRED`, or that the cohort floor
has been met.

The frozen producer implementation plan independently states that the current
35 items are insufficient for P3's 60-item `P12_PAIRED` floor and requires
`DESCRIPTIVE_OR_SENSITIVITY_ONLY` when `N_P12_FULL < 60`. The producer does not
compute `P12_PAIRED` for P3.

## Claim impact

- C5 (`P12 criterion incremental value`) remains `blocked`.
- The blocking reason is now the prespecified frozen-release scale floor, not
  missing Git authority, a dirty P3 worktree, missing Cursor authentication, or
  absence of all 35 source archives.
- No confirmatory RQ4 profiling, predictive modelling, or archive-batch recovery
  is scientifically authorized by this decision.
- The 35-item release remains usable for explicitly labelled descriptive,
  sensitivity, and case-series analyses under the existing contract.

## Stopping rule

Do not download or regenerate all 35 source archives for primary confirmatory
RQ4. A future confirmatory RQ4 requires a new prospectively compatible release
that independently satisfies every frozen floor; it may not enlarge or replace
this cohort after P3 outcomes are opened.

## Actions not taken

- No P12 or P3 scientific outcome was opened.
- No source archive was downloaded or extracted.
- No profiling, qualification, Attempt-2, construction, certification, or RQ4
  analysis was run.
- No frozen plan, bridge, consumer lock, claim ledger, or prior evidence artifact
  was modified.

## Outcome-blind RQ1 successor subject

The only next subject selected for a bounded RQ1 profiling attempt is:

```text
neutral_snapshot_id = 4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b
language_family = python
ecosystem = meson
adapter discovery = EXECUTABLE
selected rows = 20
category counts = PUBLIC_API 8 / CLI 1 / EXAMPLE 3 / BENCHMARK 8
normalized_source_tree_sha256 = f8826c3b975f8699e136e0b6b4cd4c29bf0d7e9a3be04fe09b947eb8998e727b
source_archive_sha256 = c73c0ec41ea53ba9ecb0f9903a55a19ed6c1dbfd1de00404d96b58d9c30bb3c9
build_descriptor_sha256 = c6efda5c841b1900a51b69dc3982168098752015351a7e7fa07f201e70f99836
```

The selection used no profiling outcome or expected technique tag. The frozen
rule excluded the completed, retry-forbidden Boost.Math subject; required an
`EXECUTABLE` Phase-1 adapter and 20 selected rows; preferred Python to minimize
the cost of subject-contained dynamic tracing; and required a mixed, non-header-
only workload. Exactly one of the 35 frozen subjects satisfies all predicates.

This fixed subject is not replaced if archive recovery, workload executability,
execution, or classification is unfavorable. The next admissible step is to
recover and identity-check only its committed source archive. No second subject
may be chosen from outcome information produced by this slice.
