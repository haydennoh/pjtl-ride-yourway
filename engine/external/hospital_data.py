"""
External data source: Hospital & facility data for prospective markets.

For MVP, this defines the schema and accepts manual input.
Future: integrate with CMS Provider of Services data, state licensing
databases, or commercial healthcare facility APIs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FacilityRecord:
    """A single healthcare facility in the prospective market."""

    name: str
    facility_type: str              # "hospital", "snf", "clinic", "rehab", "va", "behavioral_health"
    address: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    bed_count: int = 0
    annual_discharges: int = 0      # estimated transport-generating events
    has_nemt_contract: bool = False  # currently served by any NEMT provider
    competitor_serving: Optional[str] = None


class HospitalDataSource:
    """
    Provides facility density and capacity data for a target region.

    MVP: accepts manually-entered facility lists.
    Future: pulls from CMS, state databases, or web scraping.
    """

    def __init__(self) -> None:
        self._facilities: List[FacilityRecord] = []

    def load_manual(self, facilities: List[Dict]) -> None:
        """Load facility data from a list of dicts (e.g., from a spreadsheet)."""
        self._facilities = [
            FacilityRecord(**f) for f in facilities
        ]

    def get_facility_summary(self) -> Dict[str, int]:
        """Count facilities by type."""
        counts: Dict[str, int] = {}
        for f in self._facilities:
            counts[f.facility_type] = counts.get(f.facility_type, 0) + 1
        return counts

    def get_total_beds(self) -> int:
        return sum(f.bed_count for f in self._facilities)

    def get_estimated_daily_transports(self) -> float:
        """
        Rough estimate of daily NEMT-eligible transports from facilities.

        Heuristic (to be refined):
          - Hospitals: ~2% of beds generate a discharge transport daily
          - SNFs: ~5% of beds need recurring medical transport
          - Clinics: varies widely
        """
        TRANSPORT_RATES = {
            "hospital": 0.02,
            "snf": 0.05,
            "clinic": 0.01,
            "rehab": 0.03,
            "va": 0.03,
            "behavioral_health": 0.02,
        }
        total = 0.0
        for f in self._facilities:
            rate = TRANSPORT_RATES.get(f.facility_type, 0.01)
            total += f.bed_count * rate
        return total

    def get_competitor_coverage(self) -> float:
        """Fraction of facilities already served by a competitor."""
        if not self._facilities:
            return 0.0
        served = sum(1 for f in self._facilities if f.competitor_serving)
        return served / len(self._facilities)
