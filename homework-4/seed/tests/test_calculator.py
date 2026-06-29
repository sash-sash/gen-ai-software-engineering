"""Baseline tests for the bill splitter.

These cover the simple, happy-path behaviour that works today. The richer
edge-case tests (rounding, zero people, etc.) are produced by the Unit Test
Generator agent later in the pipeline.
"""

from src.calculator import calculate_split


def test_even_split_no_tip():
    result = calculate_split(amount=100, tip_percent=0, people=4)
    assert result["total"] == 100
    assert result["per_person"] == 25


def test_tip_amount_is_computed():
    result = calculate_split(amount=200, tip_percent=10, people=2)
    assert result["tip"] == 20
    assert result["total"] == 220
