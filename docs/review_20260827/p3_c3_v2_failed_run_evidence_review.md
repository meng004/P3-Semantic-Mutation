# P3 C3 Prospective v2 Failed-Run Evidence Review

Date: 2026-08-27
Task: `P3_C3_V2_FAILED_RUN_EVIDENCE_REVIEW`
Model / reasoning: `gpt-5.6-sol` / high
Mode: read-only root-cause and recoverability audit
Verification status: `ANALYZED`
Reproducibility: `NOT_APPLICABLE` (no new experiment; no second controller call)

This review does not rerun the controller, does not delete staging, does
not rewrite official artifacts, and does not commit. C3 remains `blocked`.

`FORMAL_V2_RUN_RETRY_FORBIDDEN=true`

---

## 1. Historical task terminal

`V2_RESULT_VALIDATION_FAIL`

That string remains the historical terminal of
`P3_C3_PROSPECTIVE_V2_FORMAL_RUN`. This review does not rewrite that
task as FOUND. The formal-run acceptance rubric required the staging
root to be absent after a successful FOUND/EXHAUSTED return. The
observed empty sibling directory failed that hygiene check. The
historical fail is retained.

## 2. Controller original terminal

`V2_ELIGIBLE_SUBJECT_FOUND`

Single official invocation:

```text
PYTHONPATH=src python3 scripts/p3_v3/prospective_applicability_search_v2.py
```

Call count: 1. Exit code: 0. stderr: empty. stdout:

```json
{"attempted_count":8,"controller_source_sha256":"0a7cda2333210effebdc31b76eb25e502df786f7b3c086ddfdb5fa740547cb7e","design_commit":"4ea6f05b44c76ebaa031277872c3711cdd1953eb","first_eligible_successor_ordinal":8,"official_terminal_written":true,"slice_id":"p3-c3-prospective-applicability-search-v2","status":"V2_ELIGIBLE_SUBJECT_FOUND"}
```

Window: `2026-08-27T13:17:58Z` to `2026-08-27T13:20:26Z`.

Official `cohort-terminal.json` embeds the same scientific status:

- `terminal_status`: `V2_ELIGIBLE_SUBJECT_FOUND`
- attempted ordinals: `1..8`
- first eligible ordinal: `8`
- first eligible neutral:
  `4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b`

## 3. Root-cause data flow

Scene at audit time matched the expected failed-run snapshot:

- worktree: `/tmp/p3-c3-applicability-authority`
- branch: `codex/p3-c3-applicability-authority`
- HEAD and remote: `6ad7f1d7d280cb6c51d19c0006e54b5059bcf338`
- controller SHA-256:
  `0a7cda2333210effebdc31b76eb25e502df786f7b3c086ddfdb5fa740547cb7e`
- tracked diff vs HEAD: empty
- porcelain: exactly 81 untracked files under the official root
- no data commit
- official root present: 8 subject directories, 80 closures, 1 terminal
- staging root present as an empty regular directory

### 3.1 Phase-1 answers along the actual code path

1. **Where is the staging root created?**
   Not by a dedicated `mkdir` of `staging_root()`. The first
   `write_subject_closures(...)` call targets
   `staging_subject_dir = staging_root / <neutral_snapshot_id>` and
   executes `target.mkdir(parents=True, exist_ok=True)`. That parent
   create is the only creation of
   `data/p3_v3/phase2/prospective-applicability-search-v2.staging`.
   Preflight requires both official and staging roots to be absent
   (`_confirm_absent_namespace`).

2. **How does each subject staging directory move to official?**
   After 10 in-memory closures,
   `write_subject_closures` writes
   `slot-closure-<slot_id>.json` exclusively under the staging subject
   directory. `place_subject_directory` then refuses an existing official
   path, creates `official/subjects/` if needed, and calls
   `os.replace(staging_subject, official_subject)`. The subject directory
   inode is renamed into the official tree. After each successful place,
   that subject's staging path no longer exists.

3. **Where and when is `cohort-terminal.json` written?**
   Only after the current subject is official and eligible (or after
   ordinal 22 is ineligible). `build_cohort_terminal` constructs the
   exact object in memory. `write_official_cohort_terminal` validates it,
   exclusive-writes `staging_root / cohort-terminal.json`, then
   `os.replace`s that file onto
   `official_root / cohort-terminal.json`. Design §11.1 steps 6–9 and
   `run_search` both make this the last official write.

4. **Is there any PBF read, closer call, or official write after the
   terminal?**
   No. On FOUND, `run_search` returns immediately after
   `write_official_cohort_terminal`. The `for` loop does not advance to
   the next successor. `main()` only serializes `stdout_summary(result)`
   and returns 0. There is no later `read_successor_pbf`,
   `close_successor_subject`, `write_subject_closures`, or second
   terminal write.

5. **Does the controller delete an empty staging root?**
   No. The controller source contains no `rmdir`, `rmtree`, `unlink`, or
   equivalent. Focused atomicity tests assert that the *subject* staging
   directory is gone after `os.replace`. They do not assert removal of
   the sibling staging *root*. The controlled-run plan §B5 even says
   "Do not stage `.staging` residue", which anticipates a leftover
   container.

6. **If not, is the empty directory a deterministic success result?**
   Yes, for every successful FOUND or EXHAUSTED path in this
   implementation. After the last subject `os.replace`, the staging root
   is already empty. The terminal write then creates one regular file
   inside that root and `os.replace`s the file away. The empty directory
   remains. This is independent of which ordinal stops the search.

7. **Can the staging root contain unfinished subjects, a temporary
   terminal, hidden files, symlinks, or special files?**
   In this scene: no. `lstat` shows a regular directory. `listdir`,
   `scandir`, and `rglob` all return 0 entries. `nlink=2` matches an
   empty directory (`.` and `..` only). No hidden names, no symlink, no
   fifo/socket/device, no leftover `cohort-terminal.json`, no leftover
   subject directory. A non-empty staging root would have been a
   different finding and would have blocked recoverability.

8. **Are exit 0 and stdout FOUND decided before or after the leftover
   staging root exists?**
   After the leftover already exists. Sequence inside one process:
   official terminal `os.replace` (staging root now empty) →
   `_search_result(status="V2_ELIGIBLE_SUBJECT_FOUND")` →
   `main()` writes stdout → process exit 0. The scientific FOUND
   decision is the in-memory eligibility of ordinal 8 plus the official
   terminal place. The empty directory is not an input to that
   decision.

9. **Can the staging root's existence change any byte of the terminal,
   closures, or attempted sequence?**
   No. Terminal and closure self-hashes are canonical JSON of their own
   objects. Neither schema includes a staging path. The empty directory
   is not a parent of any official file after the replaces. Deleting it
   cannot change tracked or untracked official bytes.

10. **Is this a scientific state-machine error, an atomic-write error,
    or a post-success directory-hygiene omission?**
    Post-success directory-hygiene omission. Evidence:
    - state machine reached FOUND and stopped at ordinal 8;
    - each subject directory and the terminal were placed with
      `os.replace` and now exist only in the official tree;
    - design §7 / §11.1 require the official terminal to be last and
      forbid later PBF/closure writes; they do not treat the empty
      sibling root as a scientific artifact;
    - the controller never implements the extra rmdir that the formal
      run's acceptance rubric later demanded.

Single root cause:

**After a successful FOUND path, the controller leaves the emptied
temporary sibling root on disk because it has no post-place cleanup of
that container.**

This is not a second scientific result, not a partial subject, and not
an atomicity failure of the 81 official files.

## 4. Staging metadata and entry verification

Path:
`data/p3_v3/phase2/prospective-applicability-search-v2.staging`

| Field | Observed |
|---|---|
| exists | yes |
| `lstat` type | directory (`S_ISDIR=true`) |
| symlink | no (`S_ISLNK=false`) |
| mode | `040755` |
| nlink | 2 |
| inode | 29732 |
| size | 4096 (empty-dir filesystem block) |
| uid/gid | 1000/1000 |
| `listdir` | `[]` |
| hidden entries | none |
| special inodes | none (`FIFO/SOCK/CHR/BLK` all false) |
| `rglob('*')` | `[]` |
| unique evidence | none |
| appears in Git porcelain | no |

mtime/ctime: `2026-08-27T13:20:25.554575+00:00`, equal to the official
terminal mtime. That equality is consistent with the last operation on
the staging root being `os.replace` of `cohort-terminal.json` out of
that directory. Timestamps are auxiliary only.

Deleting this directory would remove no file bytes from the official
tree and would not appear in any official self-hash.

## 5. Identity summary of the 81 official artifacts

Official root:
`data/p3_v3/phase2/prospective-applicability-search-v2/`

| Class | Count | Result |
|---|---|---|
| regular files | 81 | pass |
| subject directories | 8 | pass; names = frozen neutrals 1–8 |
| `cohort-terminal.json` | 1 | regular file, not a symlink |
| slot closures | 80 | 10 per subject |
| symlinks | 0 | pass |
| nested extra dirs or extra files | 0 | pass |
| ordinal 9+ directories | 0 | pass, including staging |

File SHA-256 of the terminal:

`ffd551dd7baab17118ede2c58c125f5828174503cc047b6a29252a098ddd5148`

Embedded `artifact_sha256`:

`a9bac14781f59d144f172d319b98a9d2a19705f25d5d24e73b23be72e8144fab`

The 80 closure file SHA-256 values were recomputed from current bytes
and matched the on-disk files used in the prior formal-run listing.
This review does not reprint site identifiers.

## 6. Terminal consistency

`validate_cohort_terminal(...)` was invoked once against the official
object, with `controller_source_sha256` equal to the on-disk controller
file. `main()` and `run_search()` were not called.

| Check | Result |
|---|---|
| regular file, not symlink | pass |
| file SHA-256 | pass |
| embedded artifact SHA-256 | pass |
| canonical self-hash | pass |
| exact-object keys | pass (12 keys, schema v1) |
| controller / design / authority / prior-closure bindings | pass |
| `terminal_status` | `V2_ELIGIBLE_SUBJECT_FOUND` |
| attempted ordinals | `1..8` contiguous |
| first eligible ordinal | 8 |
| first eligible neutral | `4e7e9556…a274f38b` |
| forbidden leak keys | none |

Bindings:

| Field | Value |
|---|---|
| `controller_source_sha256` | `0a7cda2333210effebdc31b76eb25e502df786f7b3c086ddfdb5fa740547cb7e` |
| `design_commit` | `4ea6f05b44c76ebaa031277872c3711cdd1953eb` |
| `design_file_sha256` | `bb0ca5d20f3fec61257b2ba524585fe899d28c8b8963c61273a8ffeb857aa6c6` |
| `authority_artifact_sha256` | `30b08271eafdead14a06707b461f108c1ec5a53eb5d2859a37b2cd6238e20214` |
| `prior_closure_commit` | `e6f9e84a5a71900e0fb6f0655393c5e1b613b6a5` |
| `schema_version` | `p3-c3-prospective-applicability-search-v2-terminal-v1` |
| `slice_id` | `p3-c3-prospective-applicability-search-v2` |

The empty staging root is not a field in this object and is not part of
the self-hash.

## 7. Subject and closure consistency

Independent byte checks only. Predicate and site-selection functions
were not re-executed.

| Ordinal | Eligibility | SITE_FROZEN | NOT_APPLICABLE | Frozen identity |
|---|---|---|---|---|
| 1 | `V2_APPLICABILITY_INELIGIBLE` | 0 | 10 | match |
| 2 | `V2_APPLICABILITY_INELIGIBLE` | 0 | 10 | match |
| 3 | `V2_APPLICABILITY_INELIGIBLE` | 0 | 10 | match |
| 4 | `V2_APPLICABILITY_INELIGIBLE` | 0 | 10 | match |
| 5 | `V2_APPLICABILITY_INELIGIBLE` | 0 | 10 | match |
| 6 | `V2_APPLICABILITY_INELIGIBLE` | 0 | 10 | match |
| 7 | `V2_APPLICABILITY_INELIGIBLE` | 0 | 10 | match |
| 8 | `V2_APPLICABILITY_ELIGIBLE` | 6 | 4 | match |

Per-closure checks, all 80:

- filename `slot-closure-<slot_id>.json` equals object `slot_id` and the
  terminal row `slot_id`;
- canonical file bytes and closer `artifact_sha256` self-hash;
- official closer self-hash reconstructed from
  `(slot_id, controlled_subject_id, site_id, state)` only;
- `slot_id` belongs to that subject's frozen inventory, in inventory
  order;
- terminal row `state` / `site_id` / `closure_artifact_sha256` equal
  the file;
- `controlled_subject_id` on each file equals the attempted-subject
  row.

No extra files, hidden files, or nested directories inside any subject
directory. No ordinal 9+ directory exists under official or staging.

This review does not interpret 10/10 `NOT_APPLICABLE` as a claim about
absent families, does not compute a cohort rate, and does not treat
ordinal 8 as representative. Those interpretations remain forbidden.

## 8. Write chronology

Control-flow order in `run_search` for this FOUND run:

1. `validate_v2_preflight` (namespaces were absent at start).
2. Ordinals 1–8: PBF identity read → 10 in-memory closures → staging
   subject write → atomic subject place → append attempted row.
3. Ordinals 1–7: eligibility `INELIGIBLE`; loop continues.
4. Ordinal 8: eligibility `ELIGIBLE`; build terminal; atomic terminal
   place; return FOUND.
5. No ordinal 9 iteration.
6. `main()` writes stdout and exits 0.

Filesystem mtimes, used only as supporting evidence:

| Artifact | Latest mtime (UTC) | Before official terminal |
|---|---|---|
| ordinal 1 closures | 2026-08-27T13:18:04.130368Z | yes |
| ordinal 2 closures | 2026-08-27T13:18:13.498378Z | yes |
| ordinal 3 closures | 2026-08-27T13:18:25.154392Z | yes |
| ordinal 4 closures | 2026-08-27T13:18:26.434394Z | yes |
| ordinal 5 closures | 2026-08-27T13:18:27.398395Z | yes |
| ordinal 6 closures | 2026-08-27T13:18:45.746418Z | yes |
| ordinal 7 closures | 2026-08-27T13:18:46.850420Z | yes |
| ordinal 8 closures | 2026-08-27T13:20:25.530575Z | yes |
| official terminal | 2026-08-27T13:20:25.554575Z | last official file |
| empty staging root | 2026-08-27T13:20:25.554575Z | equal to terminal |

No official regular file is newer than the terminal. Official run
artifacts record one command, one stdout FOUND line, and one exit 0.
HEAD still points at the implementation commit. There is no second
controller process evidence and no tracked edit of official bytes after
the run.

The leftover staging root is the emptied container after the last
`os.replace`, not a second write of scientific content.

## 9. Scientific impact

| Question | Answer |
|---|---|
| 1. Does the empty staging root enter the terminal self-hash? | No. |
| 2. Does it enter any closure self-hash? | No. |
| 3. Does it change the attempted successor sequence? | No. Sequence is `1..8` in the frozen table. |
| 4. Does it make ordinal 8 eligibility uncertain? | No. 6 `SITE_FROZEN` / 4 `NOT_APPLICABLE` are in the official files and the terminal. No conflicting artifact. |
| 5. Does it show the controller continued after FOUND? | No. Code returns immediately. No ordinal 9 directory. No official file after the terminal. |
| 6. Is there a partial subject or unbound artifact? | No. 8 complete subjects, 80 bound closures, 1 official terminal, empty staging. |
| 7. Can evidence be recovered without rerun? | Yes: delete only the empty staging directory, then submit the existing 81 official files. This review does not perform that deletion. |
| 8. Is deleting the empty directory a scientific-evidence edit or empty-container cleanup? | Empty-container cleanup. It removes no official bytes and is not part of any hash. |
| 9. Must `V2_RESULT_VALIDATION_FAIL` remain the historical task terminal? | Yes. It correctly records that the formal-run acceptance rubric failed on leftover staging. |
| 10. If recovery is later authorized, should the scientific terminal still cite the original controller return? | Yes: `V2_ELIGIBLE_SUBJECT_FOUND`. Recovery must not mint a new terminal or rerun the search. |

Authority conflict check: design §11.1 and plan §B5 treat the official
tree plus `cohort-terminal.json` as the scientific output and tell the
operator not to stage `.staging` residue. The formal-run acceptance
rule that required the staging root to be absent is a stricter hygiene
gate. That gate failed. It does not make the 81 official files
scientifically invalid.

## 10. Recoverable without rerun

Yes, under a later explicit authorization only.

Required recovery actions, not executed here:

- delete the empty staging root and nothing else;
- leave all 81 official files untouched;
- stage only
  `data/p3_v3/phase2/prospective-applicability-search-v2/`;
- commit with the already specified data message if that later task
  so authorizes.

Not required, and still forbidden:

- second controller call;
- predicate or site-selection rerun;
- rewrite of `cohort-terminal.json`;
- rewrite or move of any closure;
- controller or design patch as part of evidence recovery.

## 11. Semantics of deleting empty staging

Deleting
`data/p3_v3/phase2/prospective-applicability-search-v2.staging`
is cleanup of an emptied run container. It is not regeneration of
evidence and not a scientific rerun.

Git does not currently list that directory. After a successful rmdir,
porcelain would still be the same 81 official files, plus this review
document if it remains uncommitted.

This review does not delete it.

## 12. Unique terminal of this review

`V2_RESULT_RECOVERABLE_EMPTY_STAGING`

All recoverability predicates hold:

- staging is an empty regular directory;
- unique root cause is post-success empty-directory hygiene omission;
- all 81 official files pass identity validation;
- terminal/closure/controller/design/authority bindings are correct;
- ordinals `1..8` are contiguous;
- ordinal 8 is the first eligible subject;
- ordinal 9 and later were not opened;
- deleting empty staging would not change official evidence bytes;
- no rerun, rebuild, or official rewrite is required.

This terminal only authorizes *requesting* a later empty-directory
cleanup and evidence commit. It does not perform that cleanup.

## 13. Unique next task

`P3_C3_V2_EMPTY_STAGING_RECOVERY_AND_EVIDENCE_COMMIT`

## 14. What was not run, not modified, and not read

Not run:

- controller `main()` / `run_search()`;
- pytest;
- predicate execution;
- site selection;
- source recovery, build, profiling, mutation;
- `git add` / commit / push;
- rmdir or any cleanup.

Not modified:

- controller, tests, design, authority, inventory, registry;
- official 81 files;
- staging root (left in place);
- claim ledger;
- `/workspace`.

Not read for content:

- successor PBF site `path` / `symbol` / `span`;
- source trees;
- profiling, technique, or mutation/MR outcomes.

Read for this audit:

- `scripts/p3_v3/prospective_applicability_search_v2.py`;
- staging/official atomicity tests in
  `tests/p3_v3/test_prospective_applicability_search_v2.py`;
- design §§7, 10, 11;
- controlled-run plan Slice B;
- official terminal and the 80 closure files' identity fields only;
- filesystem metadata of official and staging paths.

C3 remains `blocked`. Claim ledger is unchanged.
