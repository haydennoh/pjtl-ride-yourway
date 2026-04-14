"""
External data source: Geographic and density data for prospective markets.

Captures the spatial characteristics that affect trip density,
deadhead time, and whether the market resembles existing RYW
regions (Grand Rapids, Lansing, Battle Creek).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class GeographicProfile:
    """Spatial characteristics of a prospective service area."""

    region_name: str
    service_area_sq_miles: float = 0.0
    urban_pct: float = 0.0
    suburban_pct: float = 0.0
    rural_pct: float = 0.0

    # Facility density (per 100 sq miles)
    hospitals_per_100_sqmi: float = 0.0
    snfs_per_100_sqmi: float = 0.0
    clinics_per_100_sqmi: float = 0.0

    # Trip geometry estimates
    avg_pickup_to_dropoff_miles: float = 0.0
    avg_deadhead_miles: float = 0.0

    # Comparable existing region (for baseline selection)
    most_similar_existing_region: Optional[str] = None


class GeographicDataSource:
    """
    Provides geographic analysis for demand and capacity planning.

    MVP: manual input.
    Future: integrate with mapping APIs for facility geocoding and
    drive-time analysis.
    """

    def __init__(self) -> None:
        self._profile: Optional[GeographicProfile] = None

    # Existing RYW region benchmarks (from Q1 data)
    EXISTING_REGIONS: Dict[str, Dict[str, float]] = {
        "grand_rapids": {
            "vehicles": 26,
            "service_area_sqmi": 450.0,    # approximate Kent County + surroundings
            "urban_pct": 0.65,
        },
        "lansing": {
            "vehicles": 3,
            "service_area_sqmi": 560.0,    # approximate Ingham County area
            "urban_pct": 0.50,
        },
        "battle_creek": {
            "vehicles": 5,
            "service_area_sqmi": 720.0,    # approximate Calhoun County area
            "urban_pct": 0.35,
        },
    }

    def load_manual(self, profile: Dict) -> None:
        self._profile = GeographicProfile(**profile)

    def get_profile(self) -> Optional[GeographicProfile]:
        return self._profile

    def find_most_similar_region(self) -> Optional[str]:
        """
        Match the prospective market to the most similar existing
        RYW region based on area size and urban/rural mix.

        This determines which historical baseline to scale from.
        """
        if not self._profile:
            return None

        # TODO: implement similarity scoring (area, urban%, density)
        # For now, default to Grand Rapids as the most data-rich baseline
        return "grand_rapids"

    def estimate_trip_geometry(self) -> Dict[str, float]:
        """
        Estimate average trip distances and deadhead based on
        facility density and area size.
        """
        if not self._profile:
            return {}

        p = self._profile
        return {
            "avg_trip_miles": p.avg_pickup_to_dropoff_miles,
            "avg_deadhead_miles": p.avg_deadhead_miles,
            "loaded_mileage_ratio": (
                p.avg_pickup_to_dropoff_miles
                / (p.avg_pickup_to_dropoff_miles + p.avg_deadhead_miles)
                if (p.avg_pickup_to_dropoff_miles + p.avg_deadhead_miles) > 0
                else 0.42  # fall back to historical 42%
            ),
        }
