"""
Viability Evaluator -- the 9-condition binary Go/No-Go check.

This is the core deliverable. A market is launch-ready IFF all
9 conditions pass simultaneously. If any fail, the evaluator
identifies what must change and suggests mitigation levers.
"""

from __future__ import annotations

from typing import List, Optional

from engine.models.metrics import (
    CapacityResult,
    ContractProfile,
    CostEstimate,
    RevenueMarginResult,
    DemandForecast,
    ViabilityReport,
    ConditionResult,
)
from engine.config import VIABILITY


class ViabilityEvaluator:
    """Evaluates all 9 launch-readiness conditions and produces a report."""

    def evaluate(
        self,
        region_name: str,
        capacity: CapacityResult,
        contracts: ContractProfile,
        cost: CostEstimate,
        revenue_margin: RevenueMarginResult,
        demand: Optional[DemandForecast] = None,
    ) -> ViabilityReport:
        conditions = self._check_all_conditions(
            capacity, contracts, cost, revenue_margin
        )

        passing = [c for c in conditions if c.passed]
        failing = [c for c in conditions if not c.passed]

        mitigations = self._suggest_mitigations(failing)

        return ViabilityReport(
            region_name=region_name,
            go_decision=len(failing) == 0,
            conditions=conditions,
            passing_count=len(passing),
            failing_count=len(failing),
            projected_margin=revenue_margin.operating_margin_pct,
            recommended_mitigations=mitigations,
            demand=demand,
            contracts=contracts,
            capacity=capacity,
            cost=cost,
            revenue_margin=revenue_margin,
        )

    def _check_all_conditions(
        self,
        capacity: CapacityResult,
        contracts: ContractProfile,
        cost: CostEstimate,
        revenue_margin: RevenueMarginResult,
    ) -> List[ConditionResult]:
        """Evaluate each of the 9 viability conditions."""

        t = VIABILITY
        return [
            ConditionResult(
                metric_number=1,
                name="Vehicle Utilization",
                target=f">= {t.vehicle_utilization_min:.0%}",
                actual_value=capacity.vehicle_utilization,
                passed=capacity.vehicle_utilization >= t.vehicle_utilization_min,
                gap=capacity.vehicle_utilization - t.vehicle_utilization_min,
            ),
            ConditionResult(
                metric_number=2,
                name="Billed Utilization",
                target=f">= {t.billed_utilization_min:.0%}",
                actual_value=capacity.billed_utilization,
                passed=capacity.billed_utilization >= t.billed_utilization_min,
                gap=capacity.billed_utilization - t.billed_utilization_min,
            ),
            ConditionResult(
                metric_number=3,
                name="Total Volume Pool",
                target=f">= {t.total_volume_pool_min:.0%}",
                actual_value=capacity.total_volume_pool_pct,
                passed=capacity.total_volume_pool_pct >= t.total_volume_pool_min,
                gap=capacity.total_volume_pool_pct - t.total_volume_pool_min,
            ),
            ConditionResult(
                metric_number=4,
                name="Avg Revenue per Kent-Leg",
                target=f">= ${t.revenue_per_kent_leg_min:.2f}",
                actual_value=revenue_margin.avg_revenue_per_kent_leg,
                passed=revenue_margin.avg_revenue_per_kent_leg >= t.revenue_per_kent_leg_min,
                gap=revenue_margin.avg_revenue_per_kent_leg - t.revenue_per_kent_leg_min,
            ),
            ConditionResult(
                metric_number=5,
                name="High-Acuity Trip Mix (SA/SC)",
                target=f">= {t.high_acuity_mix_min:.0%}",
                actual_value=capacity.high_acuity_trip_mix,
                passed=capacity.high_acuity_trip_mix >= t.high_acuity_mix_min,
                gap=capacity.high_acuity_trip_mix - t.high_acuity_mix_min,
            ),
            ConditionResult(
                metric_number=6,
                name="Non-Billable No-Shows",
                target=f"< {t.non_billable_noshow_max:.0%}",
                actual_value=capacity.non_billable_noshow_pct,
                passed=capacity.non_billable_noshow_pct < t.non_billable_noshow_max,
                gap=t.non_billable_noshow_max - capacity.non_billable_noshow_pct,
            ),
            ConditionResult(
                metric_number=7,
                name="Road Hours per Vehicle per Day",
                target=f">= {t.road_hours_per_vehicle_min:.0f} hrs",
                actual_value=capacity.road_hours_per_vehicle_per_day,
                passed=capacity.road_hours_per_vehicle_per_day >= t.road_hours_per_vehicle_min,
                gap=capacity.road_hours_per_vehicle_per_day - t.road_hours_per_vehicle_min,
            ),
            ConditionResult(
                metric_number=8,
                name="Contract Concentration",
                target=f"< {t.contract_concentration_max:.0%} per contract",
                actual_value=max(
                    contracts.top_contract_volume_pct,
                    contracts.top_contract_revenue_pct,
                ),
                passed=capacity.contract_concentration_ok,
                gap=t.contract_concentration_max - max(
                    contracts.top_contract_volume_pct,
                    contracts.top_contract_revenue_pct,
                ),
            ),
            ConditionResult(
                metric_number=9,
                name="Cost per Road Hour",
                target=f"<= ${t.cost_per_road_hour_max:.2f}",
                actual_value=cost.cost_per_road_hour,
                passed=cost.cost_per_road_hour <= t.cost_per_road_hour_max,
                gap=t.cost_per_road_hour_max - cost.cost_per_road_hour,
            ),
        ]

    def _suggest_mitigations(
        self, failing: List[ConditionResult]
    ) -> List[str]:
        """Suggest actionable mitigation levers for each failing condition."""

        mitigation_map = {
            1: "Increase demand density (add contracts) or reduce fleet size to improve vehicle utilization.",
            2: "Shift contract mix toward billable no-show contracts (SNF over broker) to lift billed utilization.",
            3: "Add broker/filler volume to reach 120% volume pool, or increase overbooking limit.",
            4: "Negotiate higher per-trip rates, increase high-acuity (SA/SC) mix, or reduce wheelchair-only dependency.",
            5: "Pursue Stretcher Alternative and SecureCare contracts to reach 5% high-acuity mix.",
            6: "Strengthen no-show billing clauses in contracts; reduce broker volume share.",
            7: "Extend operating hours or add early-morning/evening shifts to reach 9+ road hours.",
            8: "Diversify contract base; no single contract should exceed 20% of volume or revenue.",
            9: "Reduce driver wages, negotiate better fuel rates, or increase road-hour productivity to lower cost/hr.",
        }

        return [
            mitigation_map.get(c.metric_number, f"Review Metric #{c.metric_number}")
            for c in failing
        ]
