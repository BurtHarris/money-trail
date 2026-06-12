# Python Wheels — What They Are and Why They Matter

**Audience:** Experienced developers who are new to Python packaging.

---

## The short version

A **wheel** is a pre-built, platform-specific package archive. When you install a Python dependency with `pip` or `uv`, it checks whether the package maintainer published a wheel for your OS/CPU architecture/Python version. If a wheel exists, install is fast (seconds). If it doesn't, the tool falls back to compiling the package from C/C++/Rust source code — which can take minutes, require a compiler toolchain, and sometimes fails entirely.

---

## Analogy for non-Python developers

Think of Python wheels the same way you'd think about **pre-compiled binaries vs. source tarballs** in a Linux ecosystem:

| Concept | Linux (apt/rpm) | Python (pip/uv) |
|---|---|---|
| Pre-compiled artifact | `.deb` / `.rpm` package | `.whl` file (wheel) |
| Source artifact | `.tar.gz` + `./configure && make` | `.tar.gz` (sdist) + `gcc` / `rustc` |
| Install time | Fast | Fast |
| Requires compiler | No | No |

The difference is that Python packages are versioned against **three axes at once**: OS, CPU architecture, and Python version. A wheel named `duckdb-1.0.0-cp312-cp312-linux_x86_64.whl` only works on:
- CPython (`cp`) 3.12 (`312`)
- Linux x86-64

If you try to install that wheel on Python 3.14, pip will refuse it and fall back to building from source.

---

## The filename convention

Wheel filenames follow this pattern:

```
{package}-{version}-{python_tag}-{abi_tag}-{platform_tag}.whl
```

Example tags you'll see:
- `cp312` — CPython 3.12
- `py3` — any Python 3 (pure-Python package, no binary code — always works)
- `linux_x86_64` — Linux on Intel/AMD 64-bit
- `win_amd64` — Windows 64-bit
- `macosx_11_0_arm64` — macOS 11+ on Apple Silicon

Packages with binary extensions (C extensions, Rust extensions) must publish a separate wheel for every Python version × platform combination they want to support. Pure-Python packages publish one universal wheel that works everywhere.

---

## Why this matters for this project

The `requirements.txt` file pins specific package versions. Several of those packages include binary C/Rust extensions:

| Package | Extension type |
|---|---|
| `duckdb==1.0.0` | C++ extension |
| `pyarrow==16.1.0` | C++ extension (Apache Arrow) |
| `pandas==2.2.2` | C extensions |
| `psycopg2-binary==2.9.12` | C extension (PostgreSQL driver) |

These package versions were released before Python 3.14 reached stable status. The maintainers built wheels for Python 3.12 (the current stable at the time), but **not** for 3.14.

This means:
- On Python 3.12 — `uv pip install -r requirements.txt` completes quickly with pre-built wheels.
- On Python 3.14 — the installer falls back to compilation. In practice, `duckdb` and `pyarrow` do not compile cleanly from source in a standard container environment, and the build would fail.

---

## What it would take to upgrade to Python 3.14

To safely upgrade, every pinned package with a binary extension would need to be updated to a version that publishes Python 3.14 wheels. At minimum:

- `duckdb` (currently `1.0.0` → needs a release that ships `cp314` wheels)
- `pyarrow` (currently `16.1.0` → needs a release with `cp314` wheels)
- `pandas` (currently `2.2.2` → likely fine with `2.3.x`)
- `apache-airflow` (currently `3.2.2` → needs a compatible release)

See the GitHub issue "Consider upgrading to Python 3.14" for tracking this upgrade.

---

## References

- [Python Packaging User Guide: Wheels](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#wheels)
- [PEP 427 – The Wheel Binary Package Format](https://peps.python.org/pep-0427/)
- [PyPI wheel filename convention](https://packaging.python.org/en/latest/specifications/binary-distribution-format/#file-name-convention)
