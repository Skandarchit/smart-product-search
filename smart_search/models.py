"""Immutable records keep the linked list and price index in agreement."""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


def money(value):
    try:
        result = Decimal(str(value))
        if not result.is_finite() or result < 0:
            raise ValueError("Price must be finite and non-negative")
        if result != result.quantize(Decimal("0.01")):
            raise ValueError("Use at most two decimal places")
        return result.quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError) as exc:
        raise ValueError("Enter a valid price") from exc


@dataclass(frozen=True)
class Product:
    product_id: str
    name: str
    price: Decimal
    category: tuple[str, str, str]

    rating: float = 0.0
    currency: str = "INR"

    def __post_init__(self):
        import math
        if not math.isfinite(float(self.rating)) or not 0 <= float(self.rating) <= 5:
            raise ValueError("Rating must be between 0 and 5")
        object.__setattr__(self, "rating", float(self.rating))
        if self.currency not in ("INR", "GBP"):
            raise ValueError("Currency must be INR or GBP")
        for field in ("product_id", "name"):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field} must be non-empty text")
            object.__setattr__(self, field, value.strip())
        if not isinstance(self.category, (list, tuple)) or len(self.category) != 3:
            raise ValueError("Category needs exactly three levels")
        if any(not isinstance(c, str) or not c.strip() for c in self.category):
            raise ValueError("Category levels must be non-empty text")
        object.__setattr__(self, "category", tuple(c.strip() for c in self.category))
        object.__setattr__(self, "price", money(self.price))

    def row(self):
        return {"id": self.product_id, "name": self.name,
                "price": str(self.price), "rating": self.rating, "currency": self.currency, "category": " > ".join(self.category)}
