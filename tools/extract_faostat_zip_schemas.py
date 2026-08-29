from __future__ import annotations

import concurrent.futures
import json
import re
import struct
import sys
import time
import urllib.request
import zlib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "faostat_datasets_E_2026-08-19.json"
OUTPUT = ROOT / "faostat_zip_schemas_2026-08-19.json"
USER_AGENT = "FAOSTAT-data-dictionary/1.0 (metadata extraction; contact: local research use)"


def request_range(url: str, start: int, end: int, timeout: int = 45) -> tuple[bytes, dict[str, str], int]:
    headers = {"Range": f"bytes={start}-{end}", "User-Agent": USER_AGENT, "Accept-Encoding": "identity"}
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=timeout) as response:
                requested = end - start + 1
                cap = requested + 65536
                chunks: list[bytes] = []
                seen = 0
                while seen < cap:
                    chunk = response.read(min(65536, cap - seen))
                    if not chunk:
                        break
                    chunks.append(chunk)
                    seen += len(chunk)
                return b"".join(chunks)[:cap], {k.lower(): v for k, v in response.headers.items()}, response.status
        except Exception as exc:  # network retries are intentionally narrow and bounded
            last_error = exc
            time.sleep(1.0 * (attempt + 1))
    assert last_error is not None
    raise last_error


def get_size(url: str) -> int:
    data, headers, _ = request_range(url, 0, 0)
    content_range = headers.get("content-range", "")
    match = re.search(r"/(\d+)$", content_range)
    if match:
        return int(match.group(1))
    length = headers.get("content-length")
    if length:
        return int(length)
    raise RuntimeError(f"No file size returned for {url}; first response had {len(data)} bytes")


def parse_central_directory(data: bytes) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    pos = 0
    while pos + 46 <= len(data):
        signature = data[pos : pos + 4]
        if signature != b"PK\x01\x02":
            next_pos = data.find(b"PK\x01\x02", pos + 1)
            if next_pos < 0:
                break
            pos = next_pos
            continue
        fields = struct.unpack_from("<4s6H3I5H2I", data, pos)
        flags = fields[3]
        method = fields[4]
        compressed_size = fields[8]
        uncompressed_size = fields[9]
        name_length = fields[10]
        extra_length = fields[11]
        comment_length = fields[12]
        local_offset = fields[16]
        name_bytes = data[pos + 46 : pos + 46 + name_length]
        encoding = "utf-8" if flags & 0x800 else "cp437"
        name = name_bytes.decode(encoding, errors="replace")
        entries.append(
            {
                "name": name,
                "method": method,
                "compressed_size": compressed_size,
                "uncompressed_size": uncompressed_size,
                "local_offset": local_offset,
            }
        )
        pos += 46 + name_length + extra_length + comment_length
    return entries


def get_zip_entries(url: str, size: int) -> list[dict[str, Any]]:
    tail_size = min(size, 262144)
    tail_start = size - tail_size
    tail, _, status = request_range(url, tail_start, size - 1)
    if status == 200 and tail_start > 0:
        raise RuntimeError("Server ignored tail range request")
    eocd_pos = tail.rfind(b"PK\x05\x06")
    if eocd_pos < 0 or eocd_pos + 22 > len(tail):
        raise RuntimeError("ZIP end-of-central-directory record not found")
    cd_size = struct.unpack_from("<I", tail, eocd_pos + 12)[0]
    cd_offset = struct.unpack_from("<I", tail, eocd_pos + 16)[0]
    if cd_size == 0xFFFFFFFF or cd_offset == 0xFFFFFFFF:
        raise RuntimeError("ZIP64 central directory is not supported by this metadata extractor")
    if cd_offset >= tail_start and cd_offset + cd_size <= tail_start + len(tail):
        cd = tail[cd_offset - tail_start : cd_offset - tail_start + cd_size]
    else:
        cd, _, status = request_range(url, cd_offset, cd_offset + cd_size - 1)
        if status == 200 and cd_offset > 0:
            raise RuntimeError("Server ignored central-directory range request")
        cd = cd[:cd_size]
    entries = parse_central_directory(cd)
    if not entries:
        raise RuntimeError("No ZIP entries parsed")
    return entries


def decode_first_line(url: str, entry: dict[str, Any]) -> str:
    offset = int(entry["local_offset"])
    target = min(max(int(entry["compressed_size"]), 65536), 1048576)
    raw, _, status = request_range(url, offset, offset + target + 4096)
    if status == 200 and offset > 0:
        raise RuntimeError("Server ignored local-entry range request")
    if raw[:4] != b"PK\x03\x04":
        raise RuntimeError(f"Local ZIP header not found at byte {offset}")
    flags, method = struct.unpack_from("<HH", raw, 6)
    name_length, extra_length = struct.unpack_from("<HH", raw, 26)
    data_start = 30 + name_length + extra_length
    compressed = raw[data_start:]
    if method == 0:
        expanded = compressed
    elif method == 8:
        expanded = zlib.decompressobj(-15).decompress(compressed, 1048576)
    else:
        raise RuntimeError(f"Unsupported ZIP compression method {method}")
    line = expanded.splitlines()[0] if expanded else b""
    if not line:
        raise RuntimeError("Could not decompress the first CSV line")
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            return line.decode(encoding)
        except UnicodeDecodeError:
            continue
    return line.decode("utf-8", errors="replace")


def choose_main_csv(entries: list[dict[str, Any]]) -> dict[str, Any]:
    csv_entries = [e for e in entries if e["name"].lower().endswith(".csv")]
    if not csv_entries:
        raise RuntimeError("ZIP contains no CSV files")
    excluded = re.compile(r"(area|item|element|flag|symbol|unit|month|year|indicator|partner).*codes?", re.I)
    preferred = [e for e in csv_entries if "normalized" in e["name"].lower() and not excluded.search(e["name"])]
    if not preferred:
        preferred = [e for e in csv_entries if "all_data" in e["name"].lower() and not excluded.search(e["name"])]
    if not preferred:
        preferred = [e for e in csv_entries if not excluded.search(e["name"])]
    return max(preferred or csv_entries, key=lambda e: int(e["uncompressed_size"]))


def extract_dataset(dataset: dict[str, Any]) -> dict[str, Any]:
    code = dataset["DatasetCode"]
    url = dataset["FileLocation"]
    result: dict[str, Any] = {"dataset_code": code, "file_location": url}
    try:
        size = get_size(url)
        entries = get_zip_entries(url, size)
        main = choose_main_csv(entries)
        header = decode_first_line(url, main)
        result.update(
            {
                "zip_size_bytes": size,
                "main_csv": main["name"],
                "header": header,
                "columns": [part.strip().strip('"') for part in header.split(",")],
                "zip_entries": [e["name"] for e in entries],
                "companion_csvs": [e["name"] for e in entries if e["name"].lower().endswith(".csv") and e["name"] != main["name"]],
                "status": "ok",
            }
        )
    except Exception as exc:
        result.update({"status": "error", "error": f"{type(exc).__name__}: {exc}"})
    return result


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    datasets = manifest["Datasets"]["Dataset"]
    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(extract_dataset, dataset): dataset["DatasetCode"] for dataset in datasets}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(f"{result['dataset_code']}: {result['status']}", flush=True)
    order = {dataset["DatasetCode"]: index for index, dataset in enumerate(datasets)}
    results.sort(key=lambda row: order[row["dataset_code"]])
    OUTPUT.write_text(json.dumps({"extracted_at": "2026-08-19", "datasets": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    ok = sum(row["status"] == "ok" for row in results)
    print(f"Wrote {OUTPUT} with {ok}/{len(results)} successful schemas", flush=True)
    return 0 if ok == len(results) else 2


if __name__ == "__main__":
    sys.exit(main())
