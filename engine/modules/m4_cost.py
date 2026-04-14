"""
Module 4: Cost Modeling

Projects the fully-loaded operating cost for the deployed fleet,
combining fixed costs (overhead, insurance, lease) with variable
costs (driver wages, fuel, maintenance) scaled by Module 3 scheduling.

Key output: Cost per Road Hour (Metric #9, must be <= $50).
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from engine.modules.base import BaseModule
from engine.models.market import MarketProfile
from engine.models.metrics import CapacityResult, CostEstimate
from engine.config import COST, VIABILITY


class CostModule(BaseModule):
    name = "M4_Cost"

    def validate(self, inputs: Dict[str, Any]) -> bool:
        required = ["market_profile", "capacity_result"]
        return all(k in inputs for k in required)

    def run(
        self,
        market_profile: MarketProfile,
        capacity_result: CapacityResult,
        cost_assumptions: Optional[Dict[str, float]] = None,
    ) -> CostEstimate:
        """
        Cost modeling pipeline:

        1. Calculate fixed overhead (office wages, admin, allocated corporate)
        2. Calculate fixed operating (insurance, vehicle lease/payments, Samsara)
        3. Calculate variable: driver wages = drivers * hours * wage_rate
        4. Calculate variable: fuel = expected_mileage * cost_per_mile
        5. Calculate variable: maintenance (preventative + reactive)
        6. Add SecureCare-specific costs if SC vehicles deployed
        7. Compute total cost and cost-per-road-hour
        """

        fleet = market_profile.fleet
        defaults = cost_assumptions or {}

        # ── Step 1: Fixed overhead ───────────────────────────────────
        # From Weekly Margin sheet: Fixed Overhead Cost = $4,276/day (current)
        # Scales with region (smaller market = proportionally less overhead)
        # TODO: implement overhead_scaling()
        daily_overhead = defaults.get("daily_overhead", 0.0)  # placeholder

        # ── Step 2: Fixed operating ──────────────────────────────────
        # Insurance, vehicle payments, Samsara GPS, etc.
        # From Weekly Margin sheet: Fixed Operating Cost = $3,690/day (current)
        # Scales linearly with vehicle count
        # TODO: implement per-vehicle fixed operating cost
        daily_fixed_operating = defaults.get("daily_fixed_operating", 0.0)

        # ── Step 3: Driver wages ─────────────────────────────────────
        # drivers * shift_hours * hourly_rate
        # Historical: AMB = $45.50/hr, WC = $50.50/hr
        # TODO: compute blended wage rate from fleet vehicle mix
        daily_driver_wage = 0.0  # placeholder

        # ── Step 4: Fuel ─────────────────────────────────────────────
        # expected_mileage * fuel_cost_per_mile
        # TODO: pull fuel cost from historical gas data in Weekly Margin sheet
        daily_fuel = 0.0  # placeholder

        # ── Step 5: Maintenance ──────────────────────────────────────
        # preventative + reactive, scaled by fleet size and mileage
        # TODO: implement maintenance_cost_model()
        daily_maintenance = 0.0  # placeholder

        # ── Step 6: SecureCare-specific ──────────────────────────────
        # Dedicated vehicle, higher driver wage (+$2-3/hr), separate insurance
        # From SecureCare Profit sheet
        # TODO: implement securecare_cost_model()
        securecare_fixed = 0.0     # placeholder
        securecare_variable = 0.0  # placeholder

        # ── Step 7: Totals ───────────────────────────────────────────
        total_daily = (
            daily_overhead
            + daily_fixed_operating
            + daily_driver_wage
            + daily_fuel
            + daily_maintenance
            + securecare_fixed
            + securecare_variable
        )

        # Cost per road hour
        total_road_hours = (
            capacity_result.road_hours_per_vehicle_per_day
            * fleet.total_vehicles
        )
        cost_per_road_hour = 0.0
        if total_road_hours > 0:
            cost_per_road_hour = total_daily / total_road_hours

        # Cost per Kent-Leg
        cost_per_kl = 0.0
        if capacity_result.expected_completed_kent_legs > 0:
            cost_per_kl = total_daily / capacity_result.expected_completed_kent_legs

        return CostEstimate(
            total_cost=total_daily,
            total_driver_wage=daily_driver_wage,
            total_gas_cost=daily_fuel,
            total_fixed_cost=daily_fixed_operating + daily_maintenance,
            total_overhead=daily_overhead,
            cost_per_road_hour=cost_per_road_hour,
            cost_per_kent_leg=cost_per_kl,
            securecare_fixed_cost=securecare_fixed,
            securecare_variable_cost=securecare_variable,
            cost_breakdown={
                "overhead": daily_overhead,
                "fixed_operating": daily_fixed_operating,
                "driver_wage": daily_driver_wage,
                "fuel": daily_fuel,
                "maintenance": daily_maintenance,
                "securecare": securecare_fixed + securecare_variable,
            },
        )

    def summarize(self, output: CostEstimate) -> Dict[str, Any]:
        return {
            "total_cost": output.total_cost,
            "cost_per_road_hour": output.cost_per_road_hour,
            "cost_per_kent_leg": output.cost_per_kent_leg,
            "breakdown": output.cost_breakdown,
        }
