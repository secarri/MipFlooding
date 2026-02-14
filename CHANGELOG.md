# Changelog

## [Unreleased] — 2026-02-14

### Acknowledgments

Thanks to [@TheBeardedBerry](https://github.com/TheBeardedBerry) for
[PR #5](https://github.com/secarri/MipFlooding/pull/5), which identified the
quality loss from the Python-to-C# port and proposed the Mip0 recomposite
approach.

### 🐛 Bug Fixes (C#)

- **Mip0 quality loss fixed** — The Python-to-C# port introduced quality
  degradation where the stacking result was closer to Mip1 than the original.
  Fixed by recompositing the original color and alpha back on top of the
  mip-flooded result, preserving full Mip0 fidelity in opaque regions. Exposed
  as `reCompositeMip0OnTop` (C#) / `recomposite_mip0` (Python), default `true`.

- **Alpha math corrected** — `>> 8` (divides by 256) replaced with
  `(x * a + 127) / 255` in `ApplyAlpha`. Previous implementation systematically
  darkened every processed texture.
- **GDI+ handle leak fixed** — `combinedColor` and `colorToStack` bitmaps are
  now properly disposed inside the mip stacking loop. Previously leaked ~24
  bitmaps per 4K texture run.
- **File-size reporting fixed** — Percentage logic no longer uses `Math.Abs`
  (which hid whether the file grew or shrank) and thresholds are corrected.
- **Black-pixel bias fixed** — `GenerateAverageColorImage` now uses the alpha
  mask to determine transparency instead of treating `r=g=b=0` as transparent.
- **Ownership violation fixed** — `StackMipLevels` no longer disposes the
  caller's `color` and `alpha` bitmaps.
- **Pixel format consistency** — `GenerateAverageColorImage` now uses
  `Format32bppArgb` consistently with the rest of the codebase.
- **Exception safety** — All bitmap creation in the mip stacking loop now uses
  `using` statements for proper disposal on exceptions.

### 🔒 Security Fix (Python)

- **Command injection risk eliminated** — `shell=True` with string interpolation
  in `__init__.py` replaced with list-based `subprocess.run()`.

### ⚡ Performance Improvement (Python)

- **Import-time overhead removed** — `Unblock-File` PowerShell call now runs
  only once per process (guarded by `_unblocked` flag) instead of on every import.

### 🧹 Code Quality (Python)

- **Debug print removed** — `print(mask)` leftover in `batch_processing.py`
  removed.
- **Batch error handling improved** — `run_batch_mip_flood` now uses
  `as_completed` to wait for all futures and collects errors instead of
  abandoning remaining tasks on first failure. Returns `List[str]` of errors.
- **Logging modernized** — Both `__init__.py` and `batch_processing.py` now use
  `logging` module instead of bare `print()` calls.

### 📦 Packaging & Documentation

- **Added `__init__.py`** files for `mipflooding/` and `mipflooding/wrapper/`
  packages (previously relied on implicit namespace packages).
- **Fixed README paths** — Replaced `Path("src\\MipFlooding\\...")` with
  idiomatic `pathlib` `/` joins for cross-platform compatibility.
