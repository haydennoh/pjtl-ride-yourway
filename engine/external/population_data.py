"""
External data source: Population demographics for prospective markets.

Key variables for NEMT demand estimation:
  - Elderly population (65+) -- primary NEMT users
  - Medicaid eligibility rates -- drives payer mix
  - Disability rates -- affects mode mix (wheelchair vs ambulatory)

MVP: accepts manual input or static census data.
Future: integrate with Census Bureau API, ACS data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class PopulationProfile:
    """Demographic profile of a prospective service area."""

    region_name: str
    total_population: int = 0

    # Age distribution
    pct_under_18: float = 0.0
    pct_18_to_64: float = 0.0
    pct_65_plus: float = 0.0

    # Insurance / eligibility
    pct_medicaid: float = 0.0
    pct_medicare: float = 0.0
    pct_uninsured: float = 0.0
    pct_private_insurance: float = 0.0

    # Disability / mobility
    pct_disability: float = 0.0
    pct_no_vehicle_access: float = 0.0

    # Density
    population_density_per_sq_mile: float = 0.0


class PopulationDataSource:
    """
    Provides population demographic data for demand estimation.

    MVP: manual entry.
    Future: Census Bureau API (ACS 5-year estimates).
    """

    def __init__(self) -> None:
        self._profile: Optional[PopulationProfile] = None

    def load_manual(self, profile: Dict) -> None:
        self._profile = PopulationProfile(**profile)

    def get_profile(self) -> Optional[PopulationProfile]:
        return self._profile

    def get_nemt_demand_indicators(self) -> Dict[str, float]:
        """
        Extract the key indicators that drive NEMT demand.

        Higher values = more NEMT demand potential.
        """
        if not self._profile:
            return {}

        p = self._profile
        return {
            "elderly_population": p.total_population * p.pct_65_plus,
            "medicaid_eligible": p.total_population * p.pct_medicaid,
            "mobility_impaired": p.total_population * p.pct_disability,
            "no_vehicle_access": p.total_population * p.pct_no_vehicle_access,
            "population_density": p.population_density_per_sq_mile,
        }
