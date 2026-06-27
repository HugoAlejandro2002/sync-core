from decimal import ROUND_HALF_UP, Decimal

_CENTS = Decimal("0.01")


def zero_money() -> Decimal:
    return Decimal("0.00")


def to_money(value: Decimal | int | float | str) -> Decimal:
    """Coerce a value into a 2-decimal Decimal. Never use float arithmetic for money."""
    if isinstance(value, float):
        value = str(value)
    return Decimal(value).quantize(_CENTS, rounding=ROUND_HALF_UP)


def format_money(value: Decimal) -> str:
    """Render money as a fixed 2-decimal string for API responses, e.g. '8000.00'."""
    return f"{to_money(value)}"
