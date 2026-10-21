"""Conservative cleaning: normalize known labels, reject ambiguous records."""
import json
from collections import Counter
from .data_validator import CATEGORIES, validate_product


def clean_products(products):
    aliases = {c.casefold(): c for c in CATEGORIES}
    seen_ids, seen_records, clean, rejected, actions = set(), set(), [], [], []
    missing = Counter()
    duplicates = 0
    for p0 in products:
        p = dict(p0)
        for field in ("name", "brand", "category", "subcategory", "description"):
            p[field] = str(p.get(field, "")).strip()
        canonical = aliases.get(p["category"].casefold())
        if canonical and canonical != p["category"]:
            actions.append(f"{p.get('id')}: normalized category {p['category']} to {canonical}")
            p["category"] = canonical
        for field in ("name", "brand", "category", "subcategory", "description", "attributes"):
            if not p.get(field):
                missing[field] += 1
        fingerprint = json.dumps({k: v for k, v in p.items() if k != "id"}, sort_keys=True)
        duplicate = p.get("id") in seen_ids or fingerprint in seen_records
        if duplicate:
            duplicates += 1
            rejected.append({"id": p.get("id"), "reasons": ["duplicate ID or record"]})
            continue
        seen_ids.add(p.get("id"))
        seen_records.add(fingerprint)
        problems = validate_product(p)
        if problems:
            rejected.append({"id": p.get("id"), "reasons": problems})
            continue
        p["price"] = float(p["price"])
        p["rating"] = float(p["rating"])
        p["stock"] = p["stock"] == "true"
        clean.append(p)
    report = {"total_raw_products": len(products), "valid_products": len(clean), "invalid_records": len(rejected)-duplicates, "duplicate_records": duplicates, "missing_values": dict(missing), "cleaning_actions": actions, "rejected_records": rejected, "final_usable_products": len(clean)}
    return clean, report
