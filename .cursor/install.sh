#!/usr/bin/env bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

# 无论从 /workspace 还是其它目录调用（例如 `bash .cursor/install.sh`），
# 都统一切到仓库根目录，保证 .venv 与 requirements-frozen.txt 的相对路径正确。
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

if [ "$(id -u)" -eq 0 ]; then
  SUDO=""
else
  SUDO="sudo"
fi

# ---------------------------------------------------------------------------
# 1) 系统 C++ 工具链 + Python 基础包
# ---------------------------------------------------------------------------
$SUDO apt-get update

# 保留 clang-18 作为固定 c++ 前端，同时安装基础工具链。
# 注意：g++ 元包只拉入 GCC-13 的 libstdc++-13-dev，而本镜像上 clang-18 会
# 选择更高的 GCC-14 工具链来链接，二者错配会导致 "cannot find -lstdc++"。
$SUDO apt-get install -y --no-install-recommends \
  ca-certificates \
  git \
  tar \
  xz-utils \
  make \
  cmake \
  ninja-build \
  binutils \
  clang-18 \
  lld-18 \
  g++ \
  python3 \
  python3-venv \
  python3-pip

# ---------------------------------------------------------------------------
# 2) 冻结 toolchain 绑定：/usr/bin/c++ -> /usr/lib/llvm-18/bin/clang
# ---------------------------------------------------------------------------
test -x /usr/lib/llvm-18/bin/clang
$SUDO ln -sfn /usr/lib/llvm-18/bin/clang /usr/bin/c++
test "$(readlink -f /usr/bin/c++)" = "/usr/lib/llvm-18/bin/clang"

# ---------------------------------------------------------------------------
# 3) 关键修正：安装与 clang-18 实际选择的 GCC 版本匹配的 libstdc++ 开发包。
#    本镜像上 clang-18 选择 GCC-14，故需要 libstdc++-14-dev 提供缺失的
#    libstdc++.so 链接库（g++ 带来的 libstdc++-13-dev 不会被 clang 选中）。
#    这里自动探测被选中的 GCC 主版本，避免将来默认 GCC 变动导致再次错配。
# ---------------------------------------------------------------------------
GCC_MAJOR="$(echo | /usr/bin/c++ -x c++ -E -v - 2>&1 \
  | sed -n 's|.*Selected GCC installation:.*/\([0-9][0-9]*\)$|\1|p' | head -n1)"
GCC_MAJOR="${GCC_MAJOR:-14}"
$SUDO apt-get install -y --no-install-recommends "libstdc++-${GCC_MAJOR}-dev"

# 验证标准库链接文件可被 clang 驱动找到（返回绝对路径且文件存在）。
LIBSTDCXX="$("/usr/bin/c++" -print-file-name=libstdc++.so)"
test "$LIBSTDCXX" != "libstdc++.so"
test -f "$LIBSTDCXX"

# ---------------------------------------------------------------------------
# 4) Python 环境：用锁定依赖复现工作 venv（幂等）。
# ---------------------------------------------------------------------------
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements-frozen.txt

echo "P3_CURSOR_TOOLCHAIN_READY"
echo "cxx_path=/usr/bin/c++"
echo "cxx_realpath=$(readlink -f /usr/bin/c++)"
echo "selected_gcc_major=$GCC_MAJOR"
echo "libstdcxx=$LIBSTDCXX"
echo "venv_python=$(.venv/bin/python --version 2>&1)"
