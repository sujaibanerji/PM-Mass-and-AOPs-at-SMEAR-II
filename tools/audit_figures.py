"""Source inventory and explicit, provenance-based scientific figure selection."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".svg", ".pdf", ".webp"}


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def scan_sources(source_root: Path, baseline_root: Path | None) -> list[dict]:
    roots = [("project", Path(source_root))]
    if baseline_root is not None:
        roots.append(("baseline", Path(baseline_root)))
    paths = [(kind, root, p) for kind, root in roots for p in root.rglob("*")
             if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES]

    def describe(item):
        kind, root, path = item
        relative = path.relative_to(root).as_posix()
        return dict(source_id=f"{kind}:{relative}", root=kind, relative=relative,
                    format=path.suffix.lower()[1:], bytes=path.stat().st_size,
                    sha256=sha256(path))

    with ThreadPoolExecutor(max_workers=6) as pool:
        return sorted(pool.map(describe, paths), key=lambda r: r["source_id"])


def resolve_inventory(candidates: list[dict], decisions: dict) -> dict:
    """Finalize only explicit, complete decisions, never filename-only guesses."""
    source_ids = {r["source_id"] for r in candidates}
    if len(source_ids) != len(candidates):
        raise ValueError("Repeated source IDs")
    missing, unknown = source_ids - decisions.keys(), decisions.keys() - source_ids
    if missing or unknown:
        raise ValueError(f"Unresolved sources: {len(missing)}; unknown decisions: {len(unknown)}")
    figures, records = [], []
    for row in candidates:
        choice = decisions[row["source_id"]]
        disposition = choice.get("decision")
        record = dict(row, **choice)
        if disposition == "keep":
            figure = dict(id=choice["id"], title=choice["title"],
                          group=choice["group"], status=choice.get("status", "historical"),
                          canonical_source=row["source_id"], sha256=row["sha256"],
                          formats=choice.get("formats", []), placements=[],
                          scope=choice.get("scope", "Original historical analysis; not current inference"),
                          provenance=choice.get("provenance", []),
                          regeneration=choice.get("regeneration", "archived_image"))
            figures.append(figure)
            record["canonical_ids"] = [figure["id"]]
        elif disposition not in {"duplicate", "format_variant", "presentation_variant",
                                 "superseded", "composite_covered", "non_scientific_artifact"}:
            raise ValueError(f"Unresolved decision: {row['source_id']}")
        elif not choice.get("evidence"):
            raise ValueError(f"Missing exclusion evidence: {row['source_id']}")
        records.append(record)
    by_id = {r["id"]: r for r in figures}
    if len(by_id) != len(figures):
        raise ValueError("Repeated canonical figure IDs")
    for record in records:
        ids = record.get("canonical_ids", [])
        if record["decision"] != "non_scientific_artifact" and not ids:
            raise ValueError("Scientific exclusion lacks its canonical replacement")
        if any(i not in by_id for i in ids):
            raise ValueError("Exclusion names an absent canonical figure")
        for canonical in ids:
            by_id[canonical]["placements"].append(record["source_id"])
    return dict(schema_version=1, figures=figures, decisions=records, unresolved=[])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--baseline-root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = scan_sources(args.source_root, args.baseline_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"Indexed {len(rows)} image/document-format candidates")
