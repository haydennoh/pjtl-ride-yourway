"""
Module 3: Capacity & Scheduling

Determines how well RYW's deployed fleet can meet the projected demand
(Module 1) given the billing realities (Module 2). This is where
vehicle utilization, road time, and Kent-Leg throughput are calculated.

Inputs:
  - Demand forecast by mode/daypart/zone (from Module 1)
  - Fleet deployment (user choice)
  - No-show/cancellation rates by mode (from Module 2)
  - Overbooking policy
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from engine.modules.base import BaseModule
from engine.models.market import MarketProfile
from engine.models.metrics import DemandForecast, ContractProfile, CapacityResult
from engine.config import VIABILITY, OPERATIONS, HIGH_ACUITY_MODES


class CapacityModule(BaseModule):
    name = "M3_Capacity"

    def validate(self, inputs: Dict[str, Any]) -> bool:
        required = ["market_profile", "demand_forecast", "contract_profile"]
        return all(k in inputs for k in required)

    def run(
        self,
        market_profile: MarketProfile,
        demand_forecast: DemandForecast,
        contract_profile: ContractProfile,
    ) -> CapacityResult:
        """
        Capacity & scheduling pipeline:

        1. Calculate total fleet capacity (vehicles * KL/vehicle/shift)
        2. Match demand to capacity by mode and vehicle type
        3. Apply overbooking policy to determine total scheduled volume
        4. Calculate vehicle utilization = scheduled_KL / capacity_KL
        5. Apply Module 2 billability rates -> billed utilization
        6. Calculate road hours per vehicle per day
        7. Calculate expected mileage and deadhead
        8. Determine high-acuity trip mix percentage
        9. Check all capacity-dependent viability metrics
        """

        fleet = market_profile.fleet

        # ── Step 1: Fleet capacity ───────────────────────────────────
        # capacity = total_vehicles * kent_legs_per_vehicle_per_shift
        total_capacity_kl = (
            fleet.total_vehicles * OPERATIONS.kent_legs_per_vehicle_per_shift
        )
        # TODO: break down by vehicle type (WC, AMB, Stretcher, SC)

        # ── Step 2: Demand-to-capacity matching ──────────────────────
        # Match demand by mode to appropriate vehicle types
        # TODO: implement mode_to_vehicle_matching()
        # Key: wheelchair rides need WC vehicles, stretcher needs stretcher, etc.

        # ── Step 3: Overbooking ──────────────────────────────────────
        overbooking = market_profile.overbooking_limit
        scheduled_volume = demand_forecast.expected_kent_legs * overbooking
        # TODO: apply smarter overbooking (non-quality volume overbooked more)

        # ── Step 4: Vehicle utilization ──────────────────────────────
        vehicle_utilization = 0.0  # placeholder
        if total_capacity_kl > 0:
            vehicle_utilization = demand_forecast.expected_kent_legs / total_capacity_kl

        # ── Step 5: Billed utilization ───────────────────────────────
        billed_utilization = (
            vehicle_utilization
            * (1 - contract_profile.expected_non_billable_noshow_rate)
            + contract_profile.expected_billable_noshow_rate
        )
        # TODO: refine this calculation with per-mode billability

        # ── Step 6: Road hours ───────────────────────────────────────
        # road_hours = total operational hours / total vehicles
        # TODO: implement from historical road-time data (Vehicle Breakdown sheet)
        road_hours_per_vehicle = 0.0  # placeholder

        # ── Step 7: Mileage and deadhead ─────────────────────────────
        # loaded_mileage = total_mileage * OPERATIONS.loaded_mileage_pct
        # deadhead_mileage = total_mileage * (1 - loaded_mileage_pct)
        # TODO: implement from historical mileage data
        expected_mileage = 0.0     # placeholder
        deadhead_pct = 1 - OPERATIONS.loaded_mileage_pct  # ~58% deadhead

        # ── Step 8: High-acuity mix ──────────────────────────────────
        high_acuity_mix = sum(
            demand_forecast.mode_mix.get(m, 0.0) for m in HIGH_ACUITY_MODES
        )

        # ── Step 9: Volume pool ──────────────────────────────────────
        total_volume_pool = 0.0  # placeholder
        # TODO: quality_pool + filler_pool = total_volume_pool (target: 120%+)

        # ── Step 10: Viability checks ────────────────────────────────
        capacity_pass = all([
            vehicle_utilization >= VIABILITY.vehicle_utilization_min,
            billed_utilization >= VIABILITY.billed_utilization_min,
            road_hours_per_vehicle >= VIABILITY.road_hours_per_vehicle_min,
        ])

        return CapacityResult(
            vehicle_utilization=vehicle_utilization,
            billed_utilization=billed_utilization,
            non_billable_noshow_pct=contract_profile.expected_non_billable_noshow_rate,
            road_hours_per_vehicle_per_day=road_hours_per_vehicle,
            expected_completed_kent_legs=demand_forecast.expected_kent_legs,
            expected_mileage=expected_mileage,
            high_acuity_trip_mix=high_acuity_mix,
            total_volume_pool_pct=total_volume_pool,
            contract_concentration_ok=not contract_profile.concentration_flag,
            deadhead_time_pct=deadhead_pct,
            capacity_pass=capacity_pass,
        )

    def summarize(self, output: CapacityResult) -> Dict[str, Any]:
        return {
            "vehicle_utilization": output.vehicle_utilization,
            "billed_utilization": output.billed_utilization,
            "non_billable_noshow_pct": output.non_billable_noshow_pct,
            "road_hours_per_vehicle": output.road_hours_per_vehicle_per_day,
            "high_acuity_mix": output.high_acuity_trip_mix,
            "volume_pool_pct": output.total_volume_pool_pct,
            "capacity_pass": output.capacity_pass,
        }
