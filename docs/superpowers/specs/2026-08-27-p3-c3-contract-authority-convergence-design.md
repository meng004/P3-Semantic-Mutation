# P3 C3 Contract Authority Convergence Design

## Outcome

Move ordinal 8 from six frozen sites to an implementation-ready contract freeze
without creating another policy layer. The slice adds the five already-allowed
`E_CONTRACT` generators, a fixed mapping for the six frozen slots, and one
exclusive-write command that a later authorization can use to freeze contracts
and their five input rows. This slice does not run that command on formal paths.

## Frozen scientific input

- Evidence commit: `19fbb31559f3d83677b664cac09d424e6a807e66`.
- Subject: `0fefefc546f7c4519d036849a85279cc7d3aa00fe88d6ed5e259209769b5bb48`.
- Source tree: `f8826c3b975f8699e136e0b6b4cd4c29bf0d7e9a3be04fe09b947eb8998e727b`.
- Six `SITE_FROZEN` slots: two `INV` slots at `cholesky`, two `MONO`
  slots at `func`, and two `CMP` slots at `get_test_cases`.
- Four `CONV`/`DYN` slots remain closed and receive no downstream artifacts.
- Mutation, MR, profiling, P12 outcome, and reveal material are excluded.

## Chosen design

Three approaches were considered. A new manifest/schema was rejected because
the existing contract object, generator registry, verified source snapshot, and
`build_contract_inputs()` already provide the required seam. A generic generator
plus subject adapters was rejected because adapter bytes would become an
unbound second implementation source. The selected design uses five standalone
registered generators and one contract-authority module that validates and
returns the exact six-slot mapping.

The module interface is deliberately small:

```python
build_ordinal8_contracts(closures: Sequence[Mapping[str, object]]) -> dict[str, dict]
freeze_ordinal8_package(*, closures, registry) -> dict[str, object]
```

The implementation hides site/slot identities, contract-ID construction,
generator selection, domain validation, and the six calls to
`build_contract_inputs()`. Callers learn only the frozen evidence inputs and the
returned contracts/inventories.

## Contract meanings

- `INV/cholesky`: generate symmetric positive-definite arrays. The oracle is
  reconstruction of the input by the returned triangular factor within the
  frozen tolerance; activation requires successful factorization.
- `MONO/func`: generate ordered integer pairs. The oracle is nondecreasing
  Boolean output for `a <= b`; activation requires both calls to return Boolean
  values. The deliberately trivial original is retained rather than replaced.
- `CMP/get_test_cases`: generate directory-entry sequences. The oracle compares
  yielded case identifiers with the `.py`/`.pyi` projection of the same entry
  sequence; activation requires at least one accepted and one rejected suffix.

Both construction mechanisms at the same site receive distinct contract IDs
because the ID binds the slot ID, but share the same outcome-blind semantic
domain. Contract IDs are recomputable as
`canonical_sha256({domain: "P3-CONTRACT-v1", slot_id, generator_id, site_id,
contract_domain})`.

## Generator behavior

Each registered generator accepts only canonical domain bytes and the frozen
seed. It returns the existing `p3-contract-input-envelope-v1` shape and a hash
of canonical payload bytes. Enum, numeric, array, sequence, and relation-pair
generators validate their own minimal domain. Invalid domains occupy their
ordinal with the registry failure code; unsupported domains remain handled by
the existing `CONTRACT_INPUT_UNAVAILABLE` path.

## Data flow and failure behavior

The later formal command reads the six existing closure files, validates the
registered implementation snapshots, builds all six contracts in canonical
slot order, then computes five rows per contract through
`build_contract_inputs()`. Only after the full in-memory package validates does
it exclusively write one contracts file and six inventories. Existing paths,
identity mismatches, incomplete registry state, or a non-generated row fail
before any formal write.

No retry or resume interface is provided. Formal execution requires separate
authorization and does not run in this implementation slice.

## Verification

Focused tests prove exact six-slot coverage, no downstream artifact for the four
closed slots, recomputable contract IDs, generator determinism, domain-specific
payload invariants, registry source binding, fail-closed identity handling, and
exclusive output preflight. Existing contract-registry and chronology tests are
the regression surface. No full suite, subject build, mutation, or profiling is
part of this slice.

## Scientific status

This engineering slice does not add an observation and does not upgrade C3.
Its completion removes the final engineering blocker before a separately
authorized `CONTRACT_FROZEN`/`E_CONTRACT_FROZEN` write. The next scientific
target after that write is a semantic-mutant and syntactic-baseline paired
execution, not another authority review.
