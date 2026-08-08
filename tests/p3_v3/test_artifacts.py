from __future__ import annotations

import hashlib

import pytest

from p3_v3.artifacts import (
    EvidenceError,
    canonical_json_bytes,
    canonical_sha256,
    read_canonical_json,
    safe_relative_path,
    validate_exact_object,
    validate_sha256,
    write_canonical_json,
)


def test_canonical_file_has_sorted_keys_and_one_terminal_lf(tmp_path):
    path = tmp_path / "artifact.json"
    write_canonical_json(path, {"b": 2, "a": 1}, exclusive=True)
    assert path.read_bytes() == b'{"a":1,"b":2}\n'
    assert read_canonical_json(path) == {"a": 1, "b": 2}


def test_exclusive_write_preserves_existing_bytes(tmp_path):
    path = tmp_path / "artifact.json"
    path.write_bytes(b"original\n")
    with pytest.raises(EvidenceError, match="E_EXISTS"):
        write_canonical_json(path, {"a": 1}, exclusive=True)
    assert path.read_bytes() == b"original\n"


def test_reader_rejects_noncanonical_json_bytes(tmp_path):
    path = tmp_path / "artifact.json"
    path.write_bytes(b'{"b": 2, "a": 1}\n')
    with pytest.raises(EvidenceError, match="E_NONCANONICAL_JSON"):
        read_canonical_json(path)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), {"x": float("-inf")}])
def test_canonical_json_rejects_nonfinite_numbers(value):
    with pytest.raises(EvidenceError, match="E_CANONICAL_JSON"):
        canonical_json_bytes(value)


@pytest.mark.parametrize(
    "value",
    ["", "/absolute", "../escape", "a/../b", "a/./b", "a//b", "a\\b", "a\x00b"],
)
def test_safe_relative_path_rejects_unsafe_or_noncanonical_values(value):
    with pytest.raises(EvidenceError, match="E_PATH"):
        safe_relative_path(value)


def test_safe_relative_path_returns_posix_path():
    assert safe_relative_path("data/input.json").as_posix() == "data/input.json"


def test_exact_object_rejects_extra_key_and_bool_as_integer():
    schema = {"name": str, "count": int}
    with pytest.raises(EvidenceError, match="E_SCHEMA_KEYS"):
        validate_exact_object({"name": "x", "count": 1, "extra": 2}, schema, "record")
    with pytest.raises(EvidenceError, match="E_SCHEMA_TYPE"):
        validate_exact_object({"name": "x", "count": True}, schema, "record")


def test_sha256_and_canonical_hash_require_lowercase_hex():
    literal = b'{"a":1}\n'
    expected = hashlib.sha256(literal).hexdigest()
    assert canonical_sha256({"a": 1}) == expected
    assert validate_sha256(expected, "digest") == expected
    with pytest.raises(EvidenceError, match="E_SHA256"):
        validate_sha256(expected.upper(), "digest")
