from __future__ import annotations

from pathlib import Path, PurePosixPath

from p3_v3.artifacts import EvidenceError

RUNNER_VERSION = "p3-cxx-header-compile-profiler-v1"
COMPILE_TIMEOUT_SECONDS = 120


def header_include(entrypoint: str) -> str:
    if type(entrypoint) is not str or "\\" in entrypoint:
        raise EvidenceError("E_PROFILE_HEADER_ENTRYPOINT", "entrypoint is invalid")
    path = PurePosixPath(entrypoint)
    parts = entrypoint.split("/")
    if (
        path.is_absolute()
        or path.as_posix() != entrypoint
        or any(part in {"", ".", ".."} for part in parts)
        or parts[:2] != ["include", "boost"]
    ):
        raise EvidenceError("E_PROFILE_HEADER_ENTRYPOINT", "entrypoint escaped include/boost")
    return PurePosixPath(*parts[1:]).as_posix()


def translation_unit_bytes(entrypoint: str) -> bytes:
    include = header_include(entrypoint)
    return f"#include <{include}>\nint main() {{ return 0; }}\n".encode("utf-8")


def compile_argv(
    compiler: Path,
    include_root: Path,
    source: Path,
    object_path: Path,
    depfile: Path,
) -> list[str]:
    return [
        compiler.as_posix(), "-std=c++14", "-DBOOST_MATH_STANDALONE=1",
        "-I", include_root.as_posix(), "-MD", "-MF", depfile.as_posix(),
        "-MT", object_path.as_posix(), "-c", source.as_posix(),
        "-o", object_path.as_posix(),
    ]


def _depfile_dependency_tokens(depfile_bytes: bytes) -> list[str]:
    text = depfile_bytes.decode("utf-8")
    text = text.replace("\\\r\n", " ").replace("\\\n", " ")
    colon = None
    escaped = False
    for index, char in enumerate(text):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == ":":
            colon = index
            break
    if colon is None:
        raise EvidenceError("E_PROFILE_DEPFILE", "depfile target is absent")
    tokens: list[str] = []
    current: list[str] = []
    escaped = False
    for char in text[colon + 1 :]:
        if escaped:
            current.append(char)
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char.isspace():
            if current:
                tokens.append("".join(current))
                current = []
            continue
        current.append(char)
    if current:
        tokens.append("".join(current))
    return tokens


def validate_depfile_containment(
    depfile_bytes: bytes,
    include_root: Path,
    requested_header: str,
) -> None:
    if type(depfile_bytes) is not bytes:
        raise EvidenceError("E_PROFILE_DEPFILE", "depfile bytes are invalid")
    include_resolved = include_root.resolve()
    requested_resolved = (include_root / requested_header).resolve()
    found_requested = False
    for token in _depfile_dependency_tokens(depfile_bytes):
        resolved = Path(token).resolve()
        if resolved == requested_resolved:
            found_requested = True
        if "boost" in resolved.parts and not resolved.is_relative_to(include_resolved):
            raise EvidenceError(
                "E_PROFILE_DEPFILE",
                "SYSTEM_BOOST_FALLBACK",
            )
    if not found_requested:
        raise EvidenceError("E_PROFILE_DEPFILE", "requested controlled header is absent")
