"""
dataset_prep.py
----------------
Reorganizes the "SkinDisease" Kaggle dataset (already pre-split into
train/valid/test, 21 classes each) into the 4-class structure our
model actually trains on:

    data/
      train/
        acne/
        fungal_infection/
        eczema/
        healthy/
      val/
        ... same 4 classes
      test/
        ... same 4 classes

WHY ONLY 4 CLASSES:
The original plan included "hyperpigmentation", but the dataset we're
using (youssefmohmmed/human-skin-diseases-image, "SkinDisease" folder)
does not contain that class. We substitute "eczema", which is well
represented in the data and just as strong a resume item. This is a
documented dataset-availability constraint, not a shortcut - mention
it plainly in your report's methodology/limitations section.

SOURCE STRUCTURE (already on disk after your Kaggle download):
    model/data/raw/SkinDisease/train/<21 class folders>/
    model/data/raw/SkinDisease/valid/<21 class folders>/
    model/data/raw/SkinDisease/test/<21 class folders>/

USAGE:
    cd model
    python dataset_prep.py

This copies (does not move) the relevant images into model/data/train,
model/data/val, model/data/test - leaving your raw download untouched
in case you want to add more classes later.
"""

import shutil
from pathlib import Path

RAW_ROOT = Path("data/raw/SkinDisease")
OUT_DIR = Path("data")

# Maps: raw folder name (as it appears in the Kaggle download) -> our
# target class name. Edit this if you add/remove classes later.
CLASS_MAP = {
    "Acne": "acne",
    "Tinea": "fungal_infection",
    "Candidiasis": "fungal_infection",
    "Normal": "healthy",
    "Eczema": "eczema",
}

# The dataset's split folders map directly to ours (no re-splitting needed)
SPLIT_MAP = {
    "train": "train",
    "valid": "val",
    "test": "test",
}


def copy_split(raw_split_name, out_split_name):
    raw_split_dir = RAW_ROOT / raw_split_name
    if not raw_split_dir.exists():
        print(f"WARNING: {raw_split_dir} not found, skipping.")
        return

    for raw_class_name, target_class in CLASS_MAP.items():
        src_dir = raw_split_dir / raw_class_name
        if not src_dir.exists():
            print(f"WARNING: {src_dir} not found, skipping this class "
                  f"for split '{raw_split_name}'.")
            continue

        dest_dir = OUT_DIR / out_split_name / target_class
        dest_dir.mkdir(parents=True, exist_ok=True)

        count = 0
        for f in src_dir.iterdir():
            if f.suffix.lower() in (".jpg", ".jpeg", ".png"):
                # prefix filename with source class to avoid collisions
                # when two raw classes (Tinea, Candidiasis) merge into
                # one target class (fungal_infection)
                dest_name = f"{raw_class_name}_{f.name}"
                shutil.copy2(f, dest_dir / dest_name)
                count += 1

        print(f"[{out_split_name}] {raw_class_name} -> {target_class}: "
              f"{count} images")


if __name__ == "__main__":
    if not RAW_ROOT.exists():
        print(f"Expected dataset at {RAW_ROOT} - check your unzip path.")
        raise SystemExit(1)

    for raw_split, out_split in SPLIT_MAP.items():
        copy_split(raw_split, out_split)

    print("\nDone. Check model/data/train, model/data/val, model/data/test.")
    print("Each should now have 4 subfolders: acne, fungal_infection, "
          "eczema, healthy.")
