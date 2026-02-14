import os
import re
import sys
import time
from pathlib import Path
from datetime import datetime

# Add the source directory to sys.path so we can import the package
# Assumes this script is in <root>/tests/ and the package is in <root>/python/
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR / "python"))

from mipflooding.wrapper import image_processing
from mipflooding.wrapper import batch_processing

TEST_IMAGES_DIR = ROOT_DIR / ".test_images"
OUTPUT_DIR = TEST_IMAGES_DIR / "output"
README_PATH = ROOT_DIR / "README.md"
# Use stricter patterns including the dot to avoid partial matches (e.g. "T_Chair")
COLOR_PATTERN = "_C."
MASK_PATTERN = "_M."

def get_file_size_str(size_bytes):
    return f"{size_bytes / (1024 * 1024):.2f} MB"

def run_single_benchmark():
    results = []
    times = []
    percentages = []
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    files = sorted([f for f in os.listdir(TEST_IMAGES_DIR) if COLOR_PATTERN in f])
    
    for file_name in files:
        color_path = TEST_IMAGES_DIR / file_name
        # Replace only the last occurrence or strictly the pattern
        mask_name = file_name.replace(COLOR_PATTERN, MASK_PATTERN)
        mask_path = TEST_IMAGES_DIR / mask_name
        
        if not mask_path.exists():
            continue
            
        output_path = OUTPUT_DIR / file_name
        
        start_time = time.perf_counter()
        # Pass the suffix (without dot) as the format
        img_fmt = color_path.suffix.lstrip(".").lower()
        image_processing.run_mip_flooding(str(color_path), str(mask_path), str(output_path), img_format=img_fmt)
        elapsed = time.perf_counter() - start_time
        times.append(elapsed)
        
        old_size = color_path.stat().st_size
        new_size = output_path.stat().st_size
        percentage = ((old_size - new_size) / old_size) * 100
        percentages.append(percentage)
        
        results.append(f"| {file_name} | {get_file_size_str(old_size)} | {get_file_size_str(new_size)} | {percentage:.2f}% | {elapsed:.2f} sec |")

    avg_percentage = sum(percentages) / len(percentages) if percentages else 0
    avg_time = sum(times) / len(times) if times else 0
    
    results.append(f"| **Average** | | | {avg_percentage:.2f}% | {avg_time:.2f} sec |")
    return "\n".join(results)

def run_batch_benchmark():
    # Only files matching the stricter pattern
    files = [str(TEST_IMAGES_DIR / f) for f in os.listdir(TEST_IMAGES_DIR) if COLOR_PATTERN in f]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Synchronous
    start_sync = time.perf_counter()
    batch_processing.run_batch_mip_flood(
        files, 
        str(OUTPUT_DIR), 
        input_color_pattern=COLOR_PATTERN, 
        input_mask_pattern=MASK_PATTERN, 
        output_pattern=COLOR_PATTERN,
        max_workers=1
    )
    time_sync = time.perf_counter() - start_sync
    
    # Asynchronous
    start_async = time.perf_counter()
    batch_processing.run_batch_mip_flood(
        files, 
        str(OUTPUT_DIR), 
        input_color_pattern=COLOR_PATTERN, 
        input_mask_pattern=MASK_PATTERN, 
        output_pattern=COLOR_PATTERN,
        max_workers=None
    )
    time_async = time.perf_counter() - start_async
    
    return time_sync, time_async

def update_readme(single_table_rows, batch_times):
    content = README_PATH.read_text(encoding="utf-8")
    
    # 0. Update Timestamp under Statistics
    
    timestamp = datetime.now().strftime("%Y-%m-%d")
    last_run_msg = f"> *Last updated: {timestamp}*"
    
    # Regex to find ## Statistics and optional existing timestamp following it
    # We look for ## Statistics, then optional whitespace/newlines, then optional timestamp line
    pattern = r"(## Statistics)(\s*\n\s*> \*Last updated: .*?\*)?"
    replacement = f"\\1\n\n{last_run_msg}"
    content = re.sub(pattern, replacement, content, count=1)

    # 1. Update Single Processing Section
    # Find the start of the section
    start_marker = "### Single Processing"
    end_marker = "### Batch Processing"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx != -1 and end_idx != -1:
        # Construct new content
        header_single = "| Input                       | Old Size Disk | New Size Disk | Percentage Smaller | Elapsed Time |\n|-----------------------------|---------------|---------------|--------------------|--------------|"
        new_section = f"{start_marker}\n{header_single}\n{single_table_rows}\n\n"
        
        # Replace the content between start and end markers
        # We want to keep end_marker, so replace up to end_idx
        content = content[:start_idx] + new_section + content[end_idx:]
    else:
        print("Error: Could not find Single Processing or Batch Processing sections in README.")

    # 2. Update Batch Processing Section
    # Find start of Batch Processing (which is the end_marker from before)
    # The end of this section is a bit harder to define, usually an empty line before <p> or next header
    # But based on the file, it ends before <p align="center">
    
    batch_start_marker = "### Batch Processing"
    # We look for the next blank line after the table, or the <p tag
    # Let's use a regex for this part to find the table block specifically
    
    header_batch = "| Same set of files above | Elapsed Time |\n|-------------------------|--------------|"
    rows_batch = f"| Synchronous calls       | {batch_times[0]:.2f} sec    |\n| Asynchronous calls      | {batch_times[1]:.2f} sec     |"
    new_batch_content = f"{batch_start_marker}\n\n{header_batch}\n{rows_batch}\n"
    
    # We find where batch starts (updated content has it too)
    batch_start_idx = content.find(batch_start_marker)
    if batch_start_idx != -1:
        # Find the next <p or ## header
        # We start searching AFTER the marker
        rest = content[batch_start_idx:]
        # We assume the section ends at the next HTML tag or Header
        # <p align="center"> is on line 102 in original
        
        # Simple heuristic: The table ends at double newline.
        # But let's be safe. Find next "<p" or "##"
        next_section_idx = -1
        p_idx = rest.find("<p")
        h_idx = rest.find("## ") # Space to avoid matching ## inside text? No, headers are at start of line.
        
        candidates = []
        if p_idx != -1: candidates.append(p_idx)
        
        # Since we search in 'rest', we need to consider '## ' might find the current marker
        # So we skip the length of marker
        search_start = len(batch_start_marker)
        h_idx_next = rest.find("\n## ", search_start)
        if h_idx_next != -1: candidates.append(h_idx_next)
        
        if candidates:
            cutoff = min(candidates)
            # content before cutoff is the section
            # content after cutoff is the rest of file
            
            # The replacement
            content = content[:batch_start_idx] + new_batch_content + "\n" + rest[cutoff:].strip()
            # Note: adding \n and stripping rest to ensure clean separation
        else:
            # End of file?
            content = content[:batch_start_idx] + new_batch_content
            
    README_PATH.write_text(content, encoding="utf-8")
    print("README.md updated successfully.")

if __name__ == "__main__":
    print("Running Single Processing Benchmark...")
    single_rows = run_single_benchmark()
    
    print("Running Batch Processing Benchmark...")
    batch_times = run_batch_benchmark()
    
    print("Updating README...")
    update_readme(single_rows, batch_times)
