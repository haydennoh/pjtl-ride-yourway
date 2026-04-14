"""
Module 1: Demand Forecasting

Projects demand in a prospective market based on:
  - Historical ride volume by region / contract / mode / broker %
  - External data: hospital density, population demographics, competitor presence
  - Geographic similarity to existing RYW markets

Outputs: expected contracts, ride requests, completed trips, Kent-Legs, mode mix.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from engine.modules.base import BaseModule
from engine.models.market import MarketProfile, RegionGeography
from engine.models.metrics import DemandForecast
from engine.config import ORDER_MODES, DAYS_OF_WEEK


class DemandModule(BaseModule):
    name = "M1_Demand"

    def validate(self, inputs: Dict[str, Any]) -> bool:
        required = ["market_profile", "historical_baselines"]
        return all(k in inputs for k in required)

    def run(
        self,
        market_profile: MarketProfile,
        historical_baselines: Dict[str, Any],
        external_data: Optional[Dict[str, Any]] = None,
    ) -> DemandForecast:
        """
        Demand forecasting pipeline:

        1. Retrieve historical volume from analogous existing regions
           (Grand Rapids, Lansing, Battle Creek baselines from Q1 data)
        2. Scale by facility density ratio:
           (new_region_facilities / analogous_region_facilities)
        3. Adjust for population demographics (age mix, Medicaid eligibility)
        4. Adjust for competitor density (more competitors -> lower capture rate)
        5. Apply mode mix from historical data
        6. Convert trips -> Kent-Legs using historical KL multipliers by mode
        7. Project daily/daypart demand curves from historical patterns
        """

        region = market_profile.region

        # ── Step 1: Historical baseline lookup ───────────────────────
        # TODO: Pull per-region daily averages from ingested Q1 data
        # Variables needed:
        #   - total_rides_per_day by region
        #   - kent_legs_per_day by region
        #   - mode_breakdown_pct by region
        #   - completion_rate by region
        #   - cancellation_rate by region
        baseline = historical_baselines  # placeholder

        # ── Step 2: Facility density scaling ─────────────────────────
        # ratio = new_region_facilities / comparable_region_facilities
        # TODO: implement facility_density_ratio()
        density_ratio = 1.0  # placeholder

        # ── Step 3: Population adjustment ────────────────────────────
        # Higher elderly % and Medicaid eligibility -> higher NEMT demand
        # TODO: implement population_adjustment_factor()
        pop_adjustment = 1.0  # placeholder

        # ── Step 4: Competitor adjustment ────────────────────────────
        # More competitors -> lower expected market capture
        # TODO: implement competitor_adjustment_factor()
        competitor_adjustment = 1.0  # placeholder

        # ── Step 5: Composite demand estimate ────────────────────────
        # scaled_demand = baseline * density_ratio * pop_adj * competitor_adj
        # TODO: implement composite calculation
        expected_daily_rides = 0.0  # placeholder
        expected_contracts = 0      # placeholder

        # ── Step 6: Mode mix application ─────────────────────────────
        # Apply historical mode percentages from Q1 data
        # TODO: pull from Mode Breakdown sheet
        mode_mix = {mode: 0.0 for mode in ORDER_MODES}  # placeholder

        # ── Step 7: Kent-Leg conversion ──────────────────────────────
        # Use historical KL multipliers per mode from Q1 data
        # TODO: implement kent_leg_projection()
        expected_kent_legs = 0.0  # placeholder

        # ── Step 8: Daily / daypart curves ───────────────────────────
        # TODO: pull day-of-week distribution from Total Performance sheet
        daily_demand = {day: 0.0 for day in DAYS_OF_WEEK}  # placeholder

        return DemandForecast(
            region_name=region.region_name,
            expected_contracts=expected_contracts,
            expected_daily_ride_requests=expected_daily_rides,
            expected_completed_trips=expected_daily_rides * 0.85,  # placeholder rate
            expected_kent_legs=expected_kent_legs,
            mode_mix=mode_mix,
            daily_demand=daily_demand,
            expected_cancellation_rate=0.0,
            expected_noshow_rate=0.0,
        )

    def summarize(self, output: DemandForecast) -> Dict[str, Any]:
        return {
            "region": output.region_name,
            "expected_contracts": output.expected_contracts,
            "daily_ride_requests": output.expected_daily_ride_requests,
            "completed_trips": output.expected_completed_trips,
            "kent_legs": output.expected_kent_legs,
            "mode_mix": output.mode_mix,
            "noshow_rate": output.expected_noshow_rate,
        }
