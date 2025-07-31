#!/usr/bin/env python3
import argparse
import csv
import json
import time
import uuid
import random
import string
import sys
from pathlib import Path

# allowed characters for VIA random suffix
VIA_SUFFIX_CHARS = string.ascii_letters + string.digits + "-_"

def random_via_suffix(n=8):
    return ''.join(random.choice(VIA_SUFFIX_CHARS) for _ in range(n))

def parse_timestamp(ts: str) -> float:
    """
    Parse timestamps like "0:00:03", "1:23:45.67", "12:34", "5.5" into seconds (float).
    """
    ts = ts.strip()
    if not ts:
        return 0.0
    parts = ts.split(':')
    try:
        if len(parts) == 3:
            h = float(parts[0])
            m = float(parts[1])
            s = float(parts[2])
            return h * 3600 + m * 60 + s
        elif len(parts) == 2:
            m = float(parts[0])
            s = float(parts[1])
            return m * 60 + s
        else:
            # single number, could be seconds with decimals
            return float(parts[0])
    except ValueError:
        raise ValueError(f"Cannot parse timestamp: '{ts}'")

def build_via_json(annotations, file_id="1", video_filename="stream_to_via.mp4"):
    now_ms = int(time.time() * 1000)
    project = {
        "pid": "__VIA_PROJECT_ID__",
        "rev": "__VIA_PROJECT_REV_ID__",
        "rev_timestamp": "__VIA_PROJECT_REV_TIMESTAMP__",
        "pname": "Unnamed VIA Project",
        "creator": "OBS Studio from Zhao",
        "created": now_ms,
        "vid_list": [file_id]
    }
    config = {
        "file": {
            "loc_prefix": {
                "1": "",
                "2": "",
                "3": "",
                "4": ""
            }
        },
        "ui": {
            "file_content_align": "center",
            "file_metadata_editor_visible": True,
            "spatial_metadata_editor_visible": True,
            "temporal_segment_metadata_editor_visible": True,
            "spatial_region_label_attribute_id": "",
            "gtimeline_visible_row_count": "4"
        }
    }
    attribute = {
        "1": {
            "aname": "TEMPORAL-SEGMENTS",
            "anchor_id": "FILE1_Z2_XY0",
            "type": 4,
            "desc": "Temporal segment attribute added by default",
            "options": {"default": "Default"},
            "default_option_id": ""
        }
    }
    file_section = {
        file_id: {
            "fid": file_id,
            "fname": video_filename,
            "type": 4,
            "loc": 1,
            "src": ""
        }
    }
    metadata = {}
    existing_ids = set()
    for timestamp_str, annotation_text in annotations:
        try:
            t = parse_timestamp(timestamp_str)
        except ValueError as e:
            print(f"[warning] skipping line with bad timestamp '{timestamp_str}': {e}", file=sys.stderr)
            continue
        # generate unique metadata_id
        suffix = random_via_suffix(8)
        metadata_id = f"{file_id}_{suffix}"
        while metadata_id in existing_ids:
            suffix = random_via_suffix(8)
            metadata_id = f"{file_id}_{suffix}"
        existing_ids.add(metadata_id)

        metadata[metadata_id] = {
            "vid": file_id,
            "flg": 0,
            "z": [t, t],
            "xy": [],
            "av": {
                "1": annotation_text,
                "attr5": ""
            }
        }

    view = {
        "1": {
            "fid_list": [file_id]
        }
    }

    via_json = {
        "project": project,
        "config": config,
        "attribute": attribute,
        "file": file_section,
        "metadata": metadata,
        "view": view
    }
    return via_json

def read_csv_annotations(csv_path):
    annotations = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            if len(row) < 2:
                # try to skip malformed
                continue
            timestamp = row[0].strip()
            # join the rest in case annotation contains commas
            annotation = ",".join(row[1:]).strip()
            if timestamp == "" and annotation == "":
                continue
            annotations.append((timestamp, annotation))
    return annotations

def main():
    parser = argparse.ArgumentParser(description="Convert simple timestamp,annotation CSV to VIA JSON.")
    parser.add_argument("--input_csv", required=True, help="Input CSV file path")
    parser.add_argument("--output_json", required=True, help="Output JSON file path to write VIA project")
    parser.add_argument("--file-id", default="1", help="VIA file id to use (default '1')")
    parser.add_argument("--video-name", default="stream_to_via.mp4", help="Video filename to put in fname field")
    args = parser.parse_args()

    if not Path(args.input_csv).is_file():
        print(f"Input CSV '{args.input_csv}' does not exist.", file=sys.stderr)
        sys.exit(1)

    annotations = read_csv_annotations(args.input_csv)
    if not annotations:
        print("No annotations parsed from CSV.", file=sys.stderr)
        sys.exit(1)

    via_json = build_via_json(annotations, file_id=args.file_id, video_filename=args.video_name)

    # write to output
    with open(args.output_json, "w", encoding="utf-8") as out:
        json.dump(via_json, out, ensure_ascii=False, indent=2)
    print(f"VIA JSON written to {args.output_json}")

if __name__ == "__main__":
    main()
