"""
Internal metric data models -- the I/O contracts between modules.

Each dataclass represents the output of one module and the input
to downstream modules. This enforces a clean interface boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ── Module 1 Output: Demand Forecast ─────────────────────────────────

@dataclass
class DemandForecast:
    """Projected demand for a prospective market, by mode and time."""

    region_name: str

    # Aggregate projections
    expected_contracts: int = 0
    expected_daily_ride_requests: float = 0.0
    expected_completed_trips: float = 0.0
    expected_kent_legs: float = 0.0

    # Breakdown by order mode
    mode_mix: Dict[str, float] = field(default_factory=dict)
    # e.g. {"ambulatory": 0.55, "wheelchair": 0.35, "stretcher": 0.05, "securecare": 0.05}

    # Breakdown by day-of-week
    daily_demand: Dict[str, float] = field(default_factory=dict)
    # e.g. {"monday": 45.0, "tuesday": 50.0, ...}

    # Breakdown by daypart (optional granularity)
    daypart_demand: Dict[str, float] = field(default_factory=dict)

    # Cancellation / no-show expectations
    expected_cancellation_rate: float = 0.0
    expected_noshow_rate: float = 0.0


# ── Module 2 Output: Contract Profile ────────────────────────────────

@dataclass
class ContractProfile:
    """Aggregated contract economics for the market."""

    quality_volume_pct: float = 0.0               # target: >= 90%
    filler_volume_pct: float = 0.0                # target: >= 30%
    billed_utilization_forecast: float = 0.0      # target: >= 105%
    blended_revenue_per_kent_leg: float = 0.0     # target: >= $70

    # No-show economics
    expected_billable_noshow_rate: float = 0.0
    expected_non_billable_noshow_rate: float = 0.0

    # Concentration risk
    top_contract_volume_pct: float = 0.0          # must be < 20%
    top_contract_revenue_pct: float = 0.0         # must be < 20%
    concentration_flag: bool = False
    bad_revenue_flag: bool = False

    # Per-mode billability
    mode_billable_rates: Dict[str, float] = field(default_factory=dict)


# ── Module 3 Output: Capacity & Scheduling ───────────────────────────

@dataclass
class CapacityResult:
    """How well the deployed fleet can meet projected demand."""

    # Core utilization metrics
    vehicle_utilization: float = 0.0              # Metric #1 (target: >= 95%)
    billed_utilization: float = 0.0               # Metric #2 (target: >= 105%)
    non_billable_noshow_pct: float = 0.0          # Metric #6 (target: < 10%)
    road_hours_per_vehicle_per_day: float = 0.0   # Metric #7 (target: >= 9)

    # Kent-Leg output
    expected_completed_kent_legs: float = 0.0
    expected_mileage: float = 0.0

    # Acuity & volume
    high_acuity_trip_mix: float = 0.0             # Metric #5 (target: >= 5%)
    total_volume_pool_pct: float = 0.0            # Metric #3 (target: >= 120%)
    contract_concentration_ok: bool = True        # Metric #8

    # Vehicle-type utilization
    utilization_by_vehicle_type: Dict[str, float] = field(default_factory=dict)

    # Deadhead
    deadhead_time_pct: float = 0.0
    deadhead_miles: float = 0.0

    # Pass/fail for capacity-dependent metrics
    capacity_pass: bool = False


# ── Module 4 Output: Cost Estimate ───────────────────────────────────

@dataclass
class CostEstimate:
    """Fully-loaded operating cost projection."""

    # Totals
    total_cost: float = 0.0
    total_driver_wage: float = 0.0
    total_gas_cost: float = 0.0
    total_fixed_cost: float = 0.0                 # insurance, lease, repair
    total_overhead: float = 0.0

    # Unit economics
    cost_per_road_hour: float = 0.0               # Metric #9 (target: <= $50)
    cost_per_kent_leg: float = 0.0

    # SecureCare-specific
    securecare_fixed_cost: float = 0.0
    securecare_variable_cost: float = 0.0

    # Cost breakdown by category
    cost_breakdown: Dict[str, float] = field(default_factory=dict)


# ── Module 5 Output: Revenue & Margin ────────────────────────────────

@dataclass
class RevenueMarginResult:
    """Final financial projection combining all upstream modules."""

    total_revenue: float = 0.0
    total_cost: float = 0.0
    total_margin: float = 0.0
    operating_margin_pct: float = 0.0             # the north star: 25%

    # Unit economics
    avg_revenue_per_kent_leg: float = 0.0         # Metric #4 (target: >= $70)
    avg_margin_per_kent_leg: float = 0.0

    # Revenue by mode
    revenue_by_mode: Dict[str, float] = field(default_factory=dict)


# ── Viability Report ─────────────────────────────────────────────────

@dataclass
class ConditionResult:
    """Result for a single viability condition."""

    metric_number: int
    name: str
    target: str
    actual_value: float
    passed: bool
    gap: Optional[float] = None                   # how far from threshold


@dataclass
class ViabilityReport:
    """
    The final deliverable: Go / No-Go with per-condition detail.
    """

    region_name: str
    go_decision: bool = False                     # True only if ALL conditions pass

    conditions: List[ConditionResult] = field(default_factory=list)
    passing_count: int = 0
    failing_count: int = 0

    projected_margin: float = 0.0
    recommended_mitigations: List[str] = field(default_factory=list)

    # Full module outputs for drill-down
    demand: Optional[DemandForecast] = None
    contracts: Optional[ContractProfile] = None
    capacity: Optional[CapacityResult] = None
    cost: Optional[CostEstimate] = None
    revenue_margin: Optional[RevenueMarginResult] = None
