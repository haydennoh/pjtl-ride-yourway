"""
Pipeline orchestrator -- chains the 5 modules in sequence and
produces a ViabilityReport.

Flow: Market Profile
        → M1 Demand
        → M2 Contract
        → M3 Capacity
        → M4 Cost
        → M5 Revenue & Margin
        → Viability Evaluation → Go / No-Go
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from engine.models.market import MarketProfile
from engine.models.metrics import ViabilityReport
from engine.modules.m1_demand import DemandModule
from engine.modules.m2_contract import ContractModule
from engine.modules.m3_capacity import CapacityModule
from engine.modules.m4_cost import CostModule
from engine.modules.m5_revenue_margin import RevenueMarginModule
from engine.evaluation.viability import ViabilityEvaluator

logger = logging.getLogger(__name__)


class Pipeline:
    """
    Orchestrates the full market viability evaluation.

    Supports two modes:
      1. Standard run: evaluate a market against all 9 conditions
      2. Scenario run: override specific parameters to model "what if" cases
    """

    def __init__(self) -> None:
        self.m1_demand = DemandModule()
        self.m2_contract = ContractModule()
        self.m3_capacity = CapacityModule()
        self.m4_cost = CostModule()
        self.m5_revenue = RevenueMarginModule()
        self.evaluator = ViabilityEvaluator()

    def run(
        self,
        market_profile: MarketProfile,
        historical_data: Dict[str, Any],
        external_data: Optional[Dict[str, Any]] = None,
        scenario_overrides: Optional[Dict[str, Any]] = None,
    ) -> ViabilityReport:
        """
        Execute the full pipeline and return a Go/No-Go report.

        Args:
            market_profile: User-defined market + fleet configuration
            historical_data: Ingested and normalized Q1 metrics
            external_data: Hospital, population, geographic data (optional for MVP)
            scenario_overrides: Parameter overrides for "what if" modeling
        """

        overrides = scenario_overrides or {}
        logger.info("Starting pipeline for region: %s", market_profile.region.region_name)

        # ── Module 1: Demand ─────────────────────────────────────────
        logger.info("Running M1: Demand Forecasting")
        demand = self.m1_demand.run(
            market_profile=market_profile,
            historical_baselines=historical_data.get("baselines", {}),
            external_data=external_data,
        )

        # ── Module 2: Contract Business Model ────────────────────────
        logger.info("Running M2: Contract Business Model")
        contracts = self.m2_contract.run(
            market_profile=market_profile,
            demand_forecast=demand,
            historical_contract_data=historical_data.get("contracts", {}),
        )

        # ── Module 3: Capacity & Scheduling ──────────────────────────
        logger.info("Running M3: Capacity & Scheduling")
        capacity = self.m3_capacity.run(
            market_profile=market_profile,
            demand_forecast=demand,
            contract_profile=contracts,
        )

        # ── Module 4: Cost ───────────────────────────────────────────
        logger.info("Running M4: Cost Modeling")
        cost = self.m4_cost.run(
            market_profile=market_profile,
            capacity_result=capacity,
            cost_assumptions=historical_data.get("cost_assumptions", {}),
        )

        # ── Module 5: Revenue & Margin ───────────────────────────────
        logger.info("Running M5: Revenue & Margin")
        revenue_margin = self.m5_revenue.run(
            demand_forecast=demand,
            contract_profile=contracts,
            capacity_result=capacity,
            cost_estimate=cost,
            historical_revenue_by_mode=historical_data.get("revenue_by_mode", {}),
        )

        # ── Viability Evaluation ─────────────────────────────────────
        logger.info("Running viability evaluation")
        report = self.evaluator.evaluate(
            region_name=market_profile.region.region_name,
            capacity=capacity,
            contracts=contracts,
            cost=cost,
            revenue_margin=revenue_margin,
            demand=demand,
        )

        logger.info(
            "Pipeline complete: %s -> %s (margin: %.1f%%)",
            market_profile.region.region_name,
            "GO" if report.go_decision else "NO-GO",
            report.projected_margin * 100,
        )

        return report

    def run_scenario(
        self,
        market_profile: MarketProfile,
        historical_data: Dict[str, Any],
        scenario_name: str,
        overrides: Dict[str, Any],
    ) -> ViabilityReport:
        """
        Run a "what if" scenario by applying parameter overrides.

        Example scenarios:
          - "broker_drop": {"broker_volume_pct": 0.15}
          - "price_increase": {"revenue_per_kl_override": 75.0}
          - "fleet_reduction": {"wheelchair_vehicles": 3}
        """
        logger.info("Running scenario: %s", scenario_name)

        # Apply overrides to a copy of the market profile
        # TODO: implement deep-copy + override application
        return self.run(
            market_profile=market_profile,
            historical_data=historical_data,
            scenario_overrides=overrides,
        )
