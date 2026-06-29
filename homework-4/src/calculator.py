"""Core bill-splitting logic for the Bill Splitter API."""


def calculate_split(amount: float, tip_percent: float, people: int) -> dict:
    """Compute tip, total and the amount each person owes.

    amount       -- the pre-tip bill amount
    tip_percent  -- tip as a percentage of the bill (e.g. 10 for 10%)
    people       -- number of people splitting the bill
    """
    tip = amount * tip_percent / 100
    total = amount + tip

    # Split the total evenly between everyone.
    per_person = round(total / people, 2)

    return {
        "amount": round(amount, 2),
        "tip_percent": tip_percent,
        "tip": round(tip, 2),
        "total": round(total, 2),
        "people": people,
        "per_person": per_person,
    }
