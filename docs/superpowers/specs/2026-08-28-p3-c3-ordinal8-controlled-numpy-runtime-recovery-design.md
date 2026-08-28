# P3 C3 ordinal-8 controlled NumPy runtime recovery

Status: recovery task `P3_C3_ORDINAL8_CONTROLLED_NUMPY_RUNTIME_RECOVERY`. Not a paired-evidence retry.
Claim C3 remains `blocked`. This document authorizes one isolated Meson/PEP 517 build of the frozen ordinal-8 NumPy source and one import/path/version qualification. It does not authorize contract execution, mutant application, kill/survival observation, or any invocation of the consumed first paired-evidence runner.

## 1. Preserved terminal (do not rewrite)

The first paired-evidence run is a permanent infrastructure terminal:

| Field | Frozen value |
|---|---|
| commit | `2a698e74ab49a6a73b98d3de9f21478156600f09` |
| formal class | `PAIRED_EVIDENCE_INFRASTRUCTURE_TERMINAL_VALID` |
| observations | 15/15 `FAIL_INFRASTRUCTURE` |
| kill/survival | all `UNOBSERVED` |
| `artifact_sha256` | `3f317d80c163114d9b5f5ee8373cec044c8f90fb04934a7ae63f0625114aee8f` |
| file SHA-256 | `8e0de660deba8b4bc00d5994dd180bfefb7aca9673583dcdef426ba27673855f` |
| runtime root | `/tmp/p3-c3-ordinal8-first-paired-evidence` |
| output root | `data/p3_v3/phase3/ordinal8-first-paired-evidence` |
| consumed CLI | `scripts/p3_v3/run_ordinal8_first_paired_evidence.py` |

That terminal cannot enter RQ2 paired evidence. It cannot be read as mutant survival, contract invalidity, or a NumPy invariant failure. The consumed runner has no `--retry` and must not be invoked again.

Root cause, already established by read-only tracing: the consumed runner edited `cholesky` text from the frozen source tree, then imported ambient

```
numpy
numpy.array_api._array_object
numpy.array_api._dtypes
numpy.array_api._elementwise_functions
```

Ambient NumPy is 2.4.4 and has no `numpy.array_api`. Failure occurred before any contract oracle or mutant behaviour.

## 2. Unchanged scientific selection

This recovery does not re-select, rewrite, or execute the frozen slice. The following remain identity locks only:

| Field | Frozen value |
|---|---|
| `slot_id` | `a2f7a2164e7968cb5a6edf0aafa9bb406b8ba089df79cccdc565bdd9164cd913` |
| `site_id` | `f37fc591deeeadf562c46130a6cc598ca142c552bbadd1d66b0d5b0d143e2fd3` |
| `contract_id` | `449bc0e7eba8f2947047d72817b36ebd966aa4759bc0ae25a570907414c035ae` |
| inventory artifact | `a2f7cf47fc0ddb3db5f1a3268fa319debf8388061b2157b88c633ab0f4ed0c5c` |
| semantic operator | `INV_TF_SCALE_CHOLESKY_FACTOR_V1` |
| semantic patch SHA-256 | `9f0bfbb4d14bb944bf13cfdb97e135590f71208b62eabeb8b3d78937f6cfcda6` |
| syntactic operator | `FIRST_ORDER_BOOLEAN_LITERAL_FLIP_V1` |
| syntactic patch SHA-256 | `234be58e515729e102dbb255564960e3767e939301d37e30a72a9fc333867f82` |
| five `input_id` values | inventory order, unchanged |

## 3. Frozen source and Meson build descriptor

| Field | Frozen value |
|---|---|
| `neutral_snapshot_id` | `4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b` |
| `controlled_subject_source_id` | `667f66bbdb3b392af99b044181dcfa861040546fc5550906e30fca2f9aabb5d0` |
| `controlled_subject_id` | `0fefefc546f7c4519d036849a85279cc7d3aa00fe88d6ed5e259209769b5bb48` |
| normalized source-tree SHA-256 | `f8826c3b975f8699e136e0b6b4cd4c29bf0d7e9a3be04fe09b947eb8998e727b` |
| adapter | `MESON_TEST_V1` |
| ecosystem | `meson` |
| build descriptor | `{"ecosystem":"meson","language_family":"python"}` |
| `build_descriptor_sha256` | `c6efda5c841b1900a51b69dc3982168098752015351a7e7fa07f201e70f99836` |
| source path | `numpy/array_api/linalg.py` |
| `linalg.py` SHA-256 | `b64e5f8c46b457c94a96f74da90bff368f409f9f77f27519f0c84e9517803b00` |
| declared project version | `2.0.0.dev0` |

The isolated build must consume that descriptor and the extracted snapshot. It must not install NumPy from PyPI as a substitute for the frozen tree. Build work happens on a copy under the new runtime root so the extracted snapshot stays bit-identical. Git environment variables from this repository must not leak into `gitversion.py`.

The snapshot `pyproject.toml` names `vendored-meson/meson/meson.py`. That path is a git submodule (`https://github.com/numpy/meson.git`) recorded in the frozen `.gitmodules`, but the admitted tarball did not unpack the gitlink. File-identity search against NumPy history maps `pyproject.toml`, `meson.build`, `.gitmodules`, and `numpy/array_api/linalg.py` onto commit `61f97f07b73f64c0dce92cb8158739d6d92ceb82`, whose `vendored-meson/meson` gitlink is `4e370ca8ab73c07f7b84abe8a4b937caace050a4` (Meson 1.2.99 plus the `features` module). The recovery clones that pin into the source copy only. It does not rewrite the extracted snapshot. Isolated `PATH` still exposes Cython and Ninja from the prefix.

`allow-noblas=true` is the frozen Meson default in this snapshot. The recovery may pass that option explicitly. It may not change other Meson options to chase a faster or more convenient binary.

## 4. New runner, new roots

| Item | New value |
|---|---|
| CLI | `scripts/p3_v3/qualify_ordinal8_controlled_numpy_runtime.py` |
| runtime root | `/tmp/p3-c3-ordinal8-controlled-numpy-runtime` |
| output root | `data/p3_v3/phase3/ordinal8-controlled-numpy-runtime` |

The new runner must refuse to start unless commit `2a698e74…` is an ancestor and the preserved runtime/output still match the hashes above. It must refuse to write those preserved paths. It exposes no `--retry`, `--resume`, `--skip`, `--mutant`, `--slot`, `--contract`, or input selectors. It must not import or call `run_formal_once` / `main` from the consumed paired-evidence module.

This invocation is a new-version qualification, not an original-runner retry. A later clean paired-evidence replay, if any, requires a separate authorization and a later runner.

## 5. Qualification boundary

The only scientific act authorized here is import/path/version qualification:

1. Create an isolated virtualenv under the new runtime root.
2. Install the frozen `meson-python` / Cython build requirements into that prefix.
3. Build and install the copied frozen NumPy tree into that prefix.
4. Using isolated `python -I` of that prefix, import `numpy` and `numpy.array_api`.
5. Prove:
   - `numpy.__version__` is exactly `2.0.0.dev0`;
   - `numpy.__file__` and `numpy.array_api.__file__` resolve under the new runtime root;
   - those paths are not ambient 2.4.4 locations;
   - `numpy/array_api/linalg.py` SHA-256 remains `b64e5f8c…`;
   - ambient interpreters still lack `numpy.array_api`.

The record must set `paired_evidence_admissible` to false, keep kill/survival `UNOBSERVED`, and keep `scientific_result` null. It must not execute `cholesky`, the reconstruction oracle, or either mutant.

Focused tests may stub the Meson build and isolated interpreter. They must not invoke the consumed paired-evidence CLI and must not write the claim ledger.

## 6. Stop rules

- Do not delete, rewrite, or retry commit `2a698e74…` or its runtime/output.
- Do not change slot, contract, inputs, or patches.
- Do not upgrade C3.
- Do not call the consumed runner.
- If isolated build or import qualification fails, retain `FAIL_INFRASTRUCTURE` on this new record. That failure is not paired evidence and is not a license to retry the old runner.
