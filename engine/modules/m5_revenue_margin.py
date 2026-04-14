"""
Module 5: Revenue & Margin

The terminal module -- combines demand, contract quality, capacity,
and cost to produce the final projected P&L and operating margin.

This is where the 25% margin question gets answered.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from engine.modules.base import BaseModule
from engine.models.metrics import (
    DemandForecast,
    ContractProfile,
    CapacityResult,
    CostEstimate,
    RevenueMarginResult,
)
from engine.config import ORDER_MODES


class RevenueMarginModule(BaseModule):
    name = "M5_RevenueMargin"

    def validate(self, inputs: Dict[str, Any]) -> bool:
        required = [
            "demand_forecast",
            "contract_profile",
            "capacity_result",
            "cost_estimate",
        ]
        return all(k in inputs for k in required)

    def run(
        self,
        demand_forecast: DemandForecast,
        contract_profile: ContractProfile,
        capacity_result: CapacityResult,
        cost_estimate: CostEstimate,
        historical_revenue_by_mode: Optional[Dict[str, float]] = None,
    ) -> RevenueMarginResult:
        """
        Revenue & margin pipeline:

        1. Calculate revenue per mode:
           completed_KL_by_mode * avg_revenue_per_KL_by_mode
        2. Sum to total revenue
        3. Pull total cost from Module 4
        4. Calculate operating margin = (revenue - cost) / revenue
        5. Calculate unit economics (avg rev/KL, avg margin/KL)
        """

        rev_by_mode = historical_revenue_by_mode or {}

        # ── Step 1: Revenue by mode ──────────────────────────────────
        # For each mode: expected_KL * revenue_per_KL
        # Revenue per KL by mode comes from Revenue by Payer sheet
        # TODO: implement per-mode revenue calculation
        revenue_by_mode: Dict[str, float] = {}
        for mode in ORDER_MODES:
            mode_kl = (
                capacity_result.expected_completed_kent_legs
                * demand_forecast.mode_mix.get(mode, 0.0)
            )
            rev_per_kl = rev_by_mode.get(mode, 0.0)
            revenue_by_mode[mode] = mode_kl * rev_per_kl

        # ── Step 2: Total revenue ────────────────────────────────────
        # Adjust for billed utilization (some no-shows are billable)
        total_revenue = sum(revenue_by_mode.values())
        # TODO: add billable no-show revenue contribution

        # ── Step 3: Total cost ───────────────────────────────────────
        total_cost = cost_estimate.total_cost

        # ── Step 4: Operating margin ─────────────────────────────────
        margin = 0.0
        margin_pct = 0.0
        if total_revenue > 0:
            margin = total_revenue - total_cost
            margin_pct = margin / total_revenue

        # ── Step 5: Unit economics ───────────────────────────────────
        completed_kl = capacity_result.expected_completed_kent_legs
        avg_rev_per_kl = total_revenue / completed_kl if completed_kl > 0 else 0.0
        avg_margin_per_kl = margin / completed_kl if completed_kl > 0 else 0.0

        return RevenueMarginResult(
            total_revenue=total_revenue,
            total_cost=total_cost,
            total_margin=margin,
            operating_margin_pct=margin_pct,
            avg_revenue_per_kent_leg=avg_rev_per_kl,
            avg_margin_per_kent_leg=avg_margin_per_kl,
            revenue_by_mode=revenue_by_mode,
        )

    def summarize(self, output: RevenueMarginResult) -> Dict[str, Any]:
        return {
            "total_revenue": output.total_revenue,
            "total_cost": output.total_cost,
            "operating_margin_pct": output.operating_margin_pct,
            "avg_revenue_per_kent_leg": output.avg_revenue_per_kent_leg,
            "revenue_by_mode": output.revenue_by_mode,
        }
