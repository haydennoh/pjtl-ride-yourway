"""
Kent-Leg calculation utilities.

A Kent-Leg Equivalent is RYW's standardized trip unit that normalizes
transportation output across trip types and distances.

Mileage-based formula (from module design doc):
    kent_legs = ((trip_miles - 8) / 23) + 1
    minimum: 1 Kent-Leg per trip

The constants (8 and 23) represent:
    - 8 miles: base distance included in the first Kent-Leg
    - 23 miles: each additional Kent-Leg increment

NOTE: This formula may not capture all complexity (mode-specific
multipliers, etc.). The Q1 data includes historical KL Multiplier
values per mode that should be used as a cross-check. Follow up
with Zach for the complete specification.
"""

from __future__ import annotations

from engine.config import KENT_LEG


def compute_kent_legs(trip_miles: float) -> float:
    """
    Convert trip mileage to Kent-Leg equivalents.

    Args:
        trip_miles: Total miles the patient is inside the vehicle.
                    This is trip mileage, NOT total vehicle mileage
                    (excludes deadhead).

    Returns:
        Number of Kent-Leg equivalents (minimum 1.0).
    """
    if trip_miles <= 0:
        return KENT_LEG.min_kent_legs

    kl = ((trip_miles - KENT_LEG.base_miles) / KENT_LEG.incremental_miles) + 1
    return max(kl, KENT_LEG.min_kent_legs)


def compute_kent_leg_multiplier(trip_miles: float) -> float:
    """
    Compute the Kent-Leg multiplier for a trip.

    The multiplier indicates how many KL-equivalents a single trip
    represents. A standard local trip = 1.0x, longer trips > 1.0x.

    This is what appears in the Q1 data as "KL Multiple".
    """
    return compute_kent_legs(trip_miles)


def estimate_kent_legs_from_mode(
    trip_count: int,
    mode: str,
    historical_kl_multipliers: dict[str, float] | None = None,
) -> float:
    """
    Estimate total Kent-Legs from trip count and mode using historical
    multipliers rather than the mileage formula.

    This is the preferred method when actual mileage data is unavailable
    but historical KL multipliers per mode are known.

    Args:
        trip_count: Number of trips
        mode: Order mode (ambulatory, wheelchair, stretcher, securecare)
        historical_kl_multipliers: Mode -> avg KL multiplier from Q1 data

    Returns:
        Estimated total Kent-Legs
    """
    if historical_kl_multipliers and mode in historical_kl_multipliers:
        return trip_count * historical_kl_multipliers[mode]

    # Fallback: assume 1.25x average multiplier (observed Q1 range: 1.14-1.36)
    DEFAULT_MULTIPLIER = 1.25
    return trip_count * DEFAULT_MULTIPLIER
