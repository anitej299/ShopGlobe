"""Weighted relevance with normalized active factors and traceable evidence."""

WEIGHTS = {"category": .25, "features": .35, "activity": .20, "specifications": .15, "rating": .05}


def _feature_evidence(product, feature):
    features = set(product["features"])
    attrs = product["attributes"]
    if feature in features:
        return "exact"
    if feature == "stability support" and attrs.get("stability_support") == "true":
        return "semantic: stability support supports flat feet"
    if feature == "waterproof" and attrs.get("waterproof") == "true":
        return "attribute: waterproof=true"
    if feature == "long battery" and int(product["specifications"].get("battery_mah", 0)) >= 5000:
        return "semantic: battery capacity ≥ 5000 mAh"
    return None


def rank_product(product, intent):
    if intent.max_price is not None and product["price"] > intent.max_price:
        return None
    if intent.min_price is not None and product["price"] < intent.min_price:
        return None
    if intent.category and product["category"] != intent.category:
        return None
    if intent.subcategory and product["subcategory"] != intent.subcategory:
        return None
    if intent.ram_gb is not None and int(product["specifications"].get("ram_gb", 0)) < intent.ram_gb:
        return None
    if intent.activity and intent.activity not in product["usage"]:
        return None
    if intent.category == "Laptops" and intent.activity == "gaming" and product["attributes"].get("dedicated_graphics") != "true":
        return None
    if any(_feature_evidence(product, f) for f in intent.negated_features):
        return None
    reasons = []
    for feature in intent.features:
        evidence = _feature_evidence(product, feature)
        if evidence is None:
            return None  # Explicit features are mandatory; unknown is not false or a match.
        reasons.append(f"{feature}: {evidence}")
    factors = {"rating": product["rating"] / 5}
    if intent.category:
        factors["category"] = 1
        reasons.append(f"Exact category: {intent.category}")
    if intent.features:
        factors["features"] = 1
    if intent.activity:
        factors["activity"] = 1 if intent.activity in product["usage"] else 0
        if factors["activity"]:
            reasons.append(f"Intended for {intent.activity}")
    if intent.ram_gb is not None:
        factors["specifications"] = min(1, int(product["specifications"]["ram_gb"]) / intent.ram_gb)
        reasons.append(f"RAM: {product['specifications']['ram_gb']} GB (minimum {intent.ram_gb} GB)")
    weight = sum(WEIGHTS[k] for k in factors)
    score = 100 * sum(WEIGHTS[k] * v for k, v in factors.items()) / weight
    if not reasons:
        reasons.append("Ranked by customer rating; no specific attributes requested")
    return {"product": product, "score": round(score, 1), "explanation": reasons}
