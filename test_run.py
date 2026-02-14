"""Test script for the mip flooding algorithm using T_Chair textures.

Runs both with and without Mip0 recomposite to compare quality vs size.
"""
import time
from pathlib import Path

from mipflooding.wrapper import image_processing

# Paths
root = Path(__file__).parent
color = root / ".test_images" / "T_Chair_N.PNG"
mask = root / ".test_images" / "T_Chair_M.PNG"
output_dir = root / ".test_images" / "output"
output_dir.mkdir(exist_ok=True)

original_size = color.stat().st_size

print(f"Color texture: {color}  ({original_size / 1024 / 1024:.2f} MB)")
print(f"Mask texture:  {mask}  ({mask.stat().st_size / 1024:.1f} KB)")
print("=" * 60)

# Run both modes
for recomposite, label in [(False, "WITHOUT recomposite"), (True, "WITH recomposite")]:
    suffix = "_recomposite" if recomposite else "_no_recomposite"
    out = output_dir / f"T_Chair_N{suffix}.png"

    print(f"\n--- {label} (recomposite_mip0={recomposite}) ---")
    start = time.perf_counter()
    image_processing.run_mip_flooding(str(color), str(mask), str(out), recomposite_mip0=recomposite)
    elapsed = time.perf_counter() - start

    output_size = out.stat().st_size
    change_pct = ((output_size - original_size) / original_size) * 100

    print(f"  Time:    {elapsed:.2f} sec")
    print(f"  Size:    {output_size / 1024 / 1024:.2f} MB")
    if change_pct < 0:
        print(f"  Change:  {abs(change_pct):.1f}% smaller [OK]")
    else:
        print(f"  Change:  {change_pct:.1f}% bigger [WARN]")

print("\n" + "=" * 60)
print("Done. Compare the two outputs visually to see the quality difference.")
