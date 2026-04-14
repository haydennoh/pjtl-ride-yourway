"""
Data models representing a prospective market and its geographic profile.
These are the *inputs* a user provides when evaluating a new region.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RegionGeography:
    """Geographic and demographic profile of a prospective service area."""

    region_name: str
    state: str

    # Hospital / facility density
    hospital_count: int = 0
    snf_count: int = 0                            # skilled nursing facilities
    clinic_count: int = 0
    competitor_count: int = 0

    # Population characteristics
    total_population: int = 0
    elderly_population_pct: float = 0.0           # 65+
    medicaid_eligible_pct: float = 0.0
    urban_rural_mix: str = "urban"                # "urban", "suburban", "rural", "mixed"

    # Area geometry
    service_area_sq_miles: float = 0.0
    avg_trip_distance_miles: float = 0.0


@dataclass
class FleetDeployment:
    """User-specified fleet deployment for the prospective market."""

    wheelchair_vehicles: int = 0
    ambulatory_vehicles: int = 0
    stretcher_vehicles: int = 0
    securecare_vehicles: int = 0
    drivers: int = 0

    @property
    def total_vehicles(self) -> int:
        return (
            self.wheelchair_vehicles
            + self.ambulatory_vehicles
            + self.stretcher_vehicles
            + self.securecare_vehicles
        )


@dataclass
class MarketProfile:
    """
    Complete market evaluation input. Combines user choices with
    geographic data and fleet deployment decisions.
    """

    region: RegionGeography
    fleet: FleetDeployment

    # User-configurable parameters
    overbooking_limit: float = 1.20               # 120-130% typical
    projection_horizon: str = "quarter"           # "quarter", "monthly", "annual"
    broker_volume_pct: float = 0.30               # default filler %

    # Optional: existing contracts being considered
    prospective_contracts: List[ProspectiveContract] = field(default_factory=list)


@dataclass
class ProspectiveContract:
    """A potential contract in the new market being evaluated."""

    name: str
    contract_type: str                             # "snf", "hospital", "broker", "va", "securecare"
    estimated_daily_rides: float = 0.0
    estimated_revenue_per_trip: float = 0.0
    order_modes: List[str] = field(default_factory=list)   # e.g., ["wheelchair", "ambulatory"]
    noshow_billing_tier: str = "snf"               # maps to config.NOSHOW_TIERS
    payer_name: Optional[str] = None
