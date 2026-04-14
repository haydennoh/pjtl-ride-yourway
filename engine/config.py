"""
Viability thresholds, operational constants, and targets derived from
Ride YourWay's validated operating data. Every value here has been
proven in live markets -- they are not theoretical.
"""

from dataclasses import dataclass, field
from typing import Dict


# ── 9 Launch-Readiness Conditions ────────────────────────────────────
# A market is viable IFF *all* conditions hold simultaneously.

@dataclass(frozen=True)
class ViabilityThresholds:
    vehicle_utilization_min: float = 0.95          # Metric #1: 95%+ vehicle utilization
    billed_utilization_min: float = 1.05           # Metric #2: 105%+ billed utilization
    total_volume_pool_min: float = 1.20            # Metric #3: 120% total volume pool
    revenue_per_kent_leg_min: float = 70.0         # Metric #4: $70+ avg revenue / Kent-Leg
    high_acuity_mix_min: float = 0.05              # Metric #5: 5%+ SA/SC trip mix
    non_billable_noshow_max: float = 0.10          # Metric #6: <10% non-billable no-shows
    road_hours_per_vehicle_min: float = 9.0        # Metric #7: 9+ hrs road time / vehicle / day
    contract_concentration_max: float = 0.20       # Metric #8: no contract >20% vol or rev
    cost_per_road_hour_max: float = 50.0           # Metric #9: cost/road-hr <= $50

    target_operating_margin: float = 0.25          # The north-star: 25% operating margin


VIABILITY = ViabilityThresholds()


# ── Kent-Leg Calculation Constants ───────────────────────────────────
# Formula: ((trip_miles - BASE_MILES) / INCREMENTAL_MILES) + 1
# Source: Module design doc, pending full validation with Zach.

@dataclass(frozen=True)
class KentLegConstants:
    base_miles: float = 8.0
    incremental_miles: float = 23.0
    min_kent_legs: float = 1.0   # floor: every trip is at least 1 KL


KENT_LEG = KentLegConstants()


# ── Revenue Targets ──────────────────────────────────────────────────

@dataclass(frozen=True)
class RevenueTargets:
    wheelchair_per_kent_leg_min: float = 67.50
    blended_per_kent_leg_min: float = 70.0
    high_acuity_per_trip_min: float = 200.0


REVENUE = RevenueTargets()


# ── Cost Benchmarks ──────────────────────────────────────────────────

@dataclass(frozen=True)
class CostBenchmarks:
    cost_per_road_hour_target: float = 50.0
    cost_per_road_hour_stretch: float = 45.0
    cost_per_road_hour_benchmark: float = 49.50   # observed at 23% margin week

    ambulatory_cost_per_hour: float = 45.50
    wheelchair_cost_per_hour: float = 50.50


COST = CostBenchmarks()


# ── Operational Defaults ─────────────────────────────────────────────

@dataclass(frozen=True)
class OperationalDefaults:
    kent_legs_per_vehicle_per_shift: int = 8       # 95% utilization target
    max_kent_legs_per_vehicle_per_day: int = 11    # proven operational ceiling
    default_overbooking_pct: float = 1.20          # 120% default, adjustable 120-130%
    quality_volume_target: float = 0.90            # 90% quality volume
    filler_volume_target: float = 0.30             # 30% broker/filler
    standard_shift_hours: float = 9.0
    loaded_mileage_pct: float = 0.42               # 42% loaded (non-deadhead)


OPERATIONS = OperationalDefaults()


# ── No-Show Billing Rules ───────────────────────────────────────────
# Three-tier model for MVP. Contract-specific overrides handled in Module 2.

@dataclass(frozen=True)
class NoShowBillingTier:
    name: str
    billable_after_12hr: bool
    billable_before_12hr_pct: float
    description: str


NOSHOW_TIERS: Dict[str, NoShowBillingTier] = {
    "snf": NoShowBillingTier(
        name="Skilled Nursing Facility",
        billable_after_12hr=True,
        billable_before_12hr_pct=0.0,
        description="100% billable if cancelled within 12hr of pickup",
    ),
    "broker": NoShowBillingTier(
        name="Broker / Insurance",
        billable_after_12hr=False,
        billable_before_12hr_pct=0.0,
        description="Never billable (SafeRide, MTM, ModivCare, etc.)",
    ),
    "securecare": NoShowBillingTier(
        name="SecureCare / Behavioral Health",
        billable_after_12hr=False,
        billable_before_12hr_pct=0.0,
        description="Never billable; demand is spontaneous (ED-driven)",
    ),
}


# ── Fleet Baseline (Current Operations) ─────────────────────────────

@dataclass(frozen=True)
class FleetBaseline:
    regions: Dict[str, int] = field(default_factory=lambda: {
        "grand_rapids": 26,
        "lansing": 3,
        "battle_creek": 5,
    })
    total_drivers: int = 44
    securecare_vehicles: int = 2
    securecare_drivers: int = 2


FLEET = FleetBaseline()


# ── Order Modes ──────────────────────────────────────────────────────

ORDER_MODES = [
    "ambulatory",
    "wheelchair",
    "stretcher",         # Stretcher Alternative (SA) -- high acuity
    "securecare",        # SecureCare (SC) -- behavioral health, high acuity
]

HIGH_ACUITY_MODES = ["stretcher", "securecare"]


# ── Time Periods ─────────────────────────────────────────────────────

DAYS_OF_WEEK = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
DAYPARTS = ["morning", "midday", "afternoon", "evening"]
