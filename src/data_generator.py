"""Deterministic synthetic catalog. Every item and brand is fictional."""
import random
from .xml_parser import write_xml

CATALOG = {
 "Running Shoes": ("Stridecraft", ["Trail", "Road", "Stability"], ["breathable", "lightweight", "cushioned", "waterproof", "stability support"], ["running", "walking"]),
 "Casual Shoes": ("Urbanstep", ["Sneaker", "Walker", "Slip-On"], ["comfortable", "lightweight", "cushioned", "waterproof"], ["walking", "college"]),
 "Sportswear": ("Flexweave", ["Jacket", "Leggings", "Tee"], ["breathable", "quick dry", "lightweight"], ["fitness", "running"]),
 "Smartphones": ("NovaCell", ["Pro", "Lite", "Max"], ["5g", "fast charging", "long battery", "good camera"], ["daily use", "gaming"]),
 "Laptops": ("Arcbyte", ["Gaming", "Ultrabook", "Creator"], ["dedicated graphics", "lightweight", "backlit keyboard", "long battery"], ["gaming", "study", "work"]),
 "Headphones": ("Sonicraft", ["Over-Ear", "Earbuds", "Studio"], ["wireless", "noise cancellation", "long battery"], ["travel", "music", "study"]),
 "Smartwatches": ("Pulsewise", ["Fit", "Active", "Classic"], ["fitness tracking", "heart rate", "water resistant"], ["fitness", "daily use"]),
 "Backpacks": ("Carrywell", ["Campus", "Travel", "Trek"], ["lightweight", "water resistant", "laptop sleeve"], ["college", "travel"]),
 "Fitness Equipment": ("Motionlab", ["Dumbbell", "Yoga Mat", "Resistance Band"], ["portable", "adjustable", "durable"], ["fitness", "home workout"]),
 "Home Appliances": ("Homelytics", ["Mixer", "Air Fryer", "Vacuum"], ["energy efficient", "compact", "quiet"], ["cooking", "cleaning"]),
}


def generate_products(seed=2408, per_category=52):
    rng = random.Random(seed)
    products = []
    for category, (brand_root, subcategories, feature_pool, activities) in CATALOG.items():
        for i in range(per_category):
            sub = subcategories[i % len(subcategories)]
            features = sorted(set(rng.sample(feature_pool, rng.randint(1, min(3, len(feature_pool))))))
            usage = [activities[i % len(activities)]]
            if category == "Running Shoes" and i % 4 == 0:
                features = sorted(set(features + ["waterproof", "stability support"]))
                usage = ["running"]
            if category == "Headphones" and i % 5 == 0:
                features = sorted(set(features + ["wireless", "noise cancellation"]))
            attributes = {"material": rng.choice(["mesh", "synthetic", "recycled blend"])}
            specs = {"weight_g": str(rng.randrange(180, 1000, 20))}
            if category in ("Running Shoes", "Casual Shoes"):
                attributes.update({"waterproof": str("waterproof" in features).lower(), "arch_support": rng.choice(["neutral", "high", "medium"]), "stability_support": str("stability support" in features).lower(), "intended_activity": usage[0]})
                price = rng.randrange(1900, 9500, 100)
                if category == "Running Shoes" and i % 4 == 0:
                    price = rng.randrange(2900, 4900, 100)
            elif category == "Laptops":
                ram = 16 if i % 3 == 0 else rng.choice([8, 32])
                specs.update({"ram_gb": str(ram), "storage_gb": str(rng.choice([256, 512, 1024])), "battery_mah": str(rng.choice([4500, 5500, 6500]))})
                attributes["dedicated_graphics"] = str("dedicated graphics" in features).lower()
                if i % 6 == 0:
                    usage = ["gaming"]
                    features = sorted(set(features + ["dedicated graphics"]))
                    attributes["dedicated_graphics"] = "true"
                price = rng.randrange(43000, 120000, 500)
                if i % 6 == 0:
                    price = rng.randrange(57000, 69000, 500)
            elif category in ("Smartphones", "Smartwatches", "Headphones"):
                specs.update({"ram_gb": str(rng.choice([4, 6, 8, 12]) if category == "Smartphones" else 1), "storage_gb": str(rng.choice([64, 128, 256]) if category == "Smartphones" else 16), "battery_mah": str(rng.choice([4000, 5000, 6000]) if category == "Smartphones" else 500)})
                price = rng.randrange(5000, 42000, 250) if category == "Smartphones" else rng.randrange(1200, 13000, 100)
            else:
                price = rng.randrange(700, 9500, 100)
            products.append({"id": f"SG-{len(products)+1:04d}", "name": f"{brand_root} {sub} {i+1:02d}", "brand": f"{brand_root} {i%3+1}", "category": category, "subcategory": sub, "description": f"Synthetic {category.lower()} designed for {usage[0]}; features {', '.join(features)}.", "price": price, "rating": round(rng.uniform(3.1, 5), 1), "stock": "false" if i % 13 == 0 else "true", "features": features, "usage": usage, "specifications": specs, "attributes": attributes})
    return products


def generate_raw(path, invalid_path):
    valid = generate_products()
    bad = []
    for suffix, edits in (("duplicate_id", {"name": "Duplicate identifier"}), ("duplicate_record", {}), ("missing_name", {"name": ""}), ("missing_attributes", {"attributes": {}}), ("negative_price", {"price": -20}), ("bad_rating", {"rating": 7}), ("category_case", {"category": "running shoes"})):
        source = valid[0] if suffix == "duplicate_record" else valid[len(bad)+1]
        p = {**source, **edits}
        if suffix == "category_case":
            p["name"] += " Variant"
        if suffix not in ("duplicate_id", "duplicate_record"):
            p["id"] = "SG-0521" if suffix == "category_case" else "BAD-" + suffix
        bad.append(p)
    write_xml(valid + bad, path)
    write_xml(bad, invalid_path)
    return len(valid), len(bad)
