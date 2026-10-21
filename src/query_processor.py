"""Conservative rules for catalog-specific natural language queries."""
import re
from dataclasses import dataclass, field

CATEGORY_TERMS = {
 "Running Shoes": ("running shoes", "running shoe", "running sneaker", "jogging shoe"),
 "Casual Shoes": ("casual shoes", "casual shoe", "walking shoes", "walking shoe", "comfortable shoes", "comfortable shoe", "shoes for walking"),
 "Sportswear": ("sportswear", "sports wear", "activewear", "jacket", "leggings"),
 "Smartphones": ("smartphone", "mobile phone", "phone"),
 "Laptops": ("laptop", "notebook computer"),
 "Headphones": ("headphones", "headphone", "earbuds", "earbud", "headset"),
 "Smartwatches": ("smartwatches", "smartwatch", "smart watch", "fitness watch"),
 "Backpacks": ("backpacks", "backpack", "rucksack", "school bag"),
 "Fitness Equipment": ("fitness equipment", "dumbbell", "yoga mat", "resistance band"),
 "Home Appliances": ("home appliance", "air fryer", "mixer", "vacuum"),
}
FEATURE_TERMS = {
 "waterproof": ("waterproof", "water proof"),
 "water resistant": ("water resistant", "water resistance"),
 "stability support": ("flat feet", "flat foot", "stability support", "overpronation"),
 "noise cancellation": ("noise cancellation", "noise cancelling", "anc"),
 "wireless": ("wireless", "bluetooth"),
 "long battery": ("good battery", "long battery", "battery life"),
 "lightweight": ("lightweight", "light weight"),
 "comfortable": ("comfortable", "comfort"),
 "fitness tracking": ("fitness tracking", "activity tracking"),
 "dedicated graphics": ("gaming graphics", "dedicated graphics", "gpu"),
 "breathable": ("breathable",),
 "quick dry": ("quick dry", "quick-dry"),
}
ACTIVITIES = ("running", "walking", "gaming", "college", "fitness", "travel", "study", "work", "music")


@dataclass
class Intent:
    category: str | None = None
    subcategory: str | None = None
    features: list[str] = field(default_factory=list)
    activity: str | None = None
    max_price: float | None = None
    min_price: float | None = None
    ram_gb: int | None = None
    negated_features: list[str] = field(default_factory=list)
    raw: str = ""


def parse_query(query):
    if not isinstance(query, str):
        raise ValueError("Query must be text")
    text = re.sub(r"\s+", " ", query.casefold().replace(",", "")).strip()
    if len(text) > 500:
        raise ValueError("Query is too long (500 characters maximum)")
    intent = Intent(raw=text)
    for category, terms in CATEGORY_TERMS.items():
        if any(re.search(r"(?<!\w)" + re.escape(t) + r"\b", text) for t in terms):
            intent.category = category
            break
    for feature, terms in FEATURE_TERMS.items():
        for term in terms:
            match = re.search(r"(?<!\w)" + re.escape(term) + r"\b", text)
            if match:
                prefix = text[max(0, match.start()-14):match.start()]
                target = intent.negated_features if re.search(r"\b(?:no|not|without)\s*$", prefix) else intent.features
                if feature not in target:
                    target.append(feature)
                break
    for activity in ACTIVITIES:
        if re.search(r"\b" + activity + r"\b", text):
            intent.activity = activity
            break
    for subcategory in ("Jacket", "Leggings", "Tee"):
        if re.search(r"\b" + subcategory.casefold() + r"s?\b", text):
            intent.subcategory = subcategory
            break
    upper = re.search(r"(?:under|below|less than|up to|max(?:imum)?|within)\s*(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(k|lakh)?\b", text)
    lower = re.search(r"(?:above|over|at least|min(?:imum)?)\s*(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(k|lakh)?\b", text)
    def money(m):
        return float(m.group(1)) * {None: 1, "k": 1000, "lakh": 100000}[m.group(2)]
    if upper:
        intent.max_price = money(upper)
    if lower:
        intent.min_price = money(lower)
    ram = re.search(r"\b(\d{1,3})\s*gb\s*ram\b", text)
    if ram:
        intent.ram_gb = int(ram.group(1))
    if "budget" in text or "affordable" in text:
        if intent.max_price is None:
            intent.max_price = {"Laptops": 70000, "Smartphones": 20000, "Smartwatches": 5000}.get(intent.category, 5000)
    return intent
