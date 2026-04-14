"""
Module 2: Contract Business Model

Encodes RYW's internal billing rules, no-show policies, and contract
quality/filler classification. Determines what fraction of completed
trips actually generate revenue.

Key rules:
  - SNF contracts: 100% billable no-show if cancelled within 12hr of pickup
  - Broker/insurance (SafeRide, MTM, etc.): no-shows are never billable
  - SecureCare: no-shows never billable, demand is spontaneous (ED-driven)
  - VA: flat rate per trip
  - No single contract > 20% of volume or revenue
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from engine.modules.base import BaseModule
from engine.models.market import MarketProfile, ProspectiveContract
from engine.models.metrics import DemandForecast, ContractProfile
from engine.config import NOSHOW_TIERS, VIABILITY


class ContractModule(BaseModule):
    name = "M2_Contract"

    def validate(self, inputs: Dict[str, Any]) -> bool:
        required = ["market_profile", "demand_forecast"]
        return all(k in inputs for k in required)

    def run(
        self,
        market_profile: MarketProfile,
        demand_forecast: DemandForecast,
        historical_contract_data: Optional[Dict[str, Any]] = None,
    ) -> ContractProfile:
        """
        Contract business model pipeline:

        1. Classify each prospective contract as quality or filler
        2. Apply no-show billing rules per contract tier
        3. Calculate expected billable vs non-billable no-show rates
        4. Compute blended revenue per Kent-Leg across all contracts
        5. Check contract concentration (no single contract > 20%)
        6. Flag bad-revenue contracts (below $67.50/KL for wheelchair)
        """

        contracts = market_profile.prospective_contracts

        # ── Step 1: Quality vs Filler classification ─────────────────
        # Quality: SNF, hospital, VA, recurring medical
        # Filler: broker-based (SafeRide, MTM, ModivCare, Feonix)
        # TODO: implement classify_contracts()
        quality_contracts: List[ProspectiveContract] = []
        filler_contracts: List[ProspectiveContract] = []

        quality_volume_pct = 0.0  # placeholder
        filler_volume_pct = 0.0   # placeholder

        # ── Step 2: No-show billing rules ────────────────────────────
        # For each contract, look up its NOSHOW_TIER and compute:
        #   - billable_noshow_rate
        #   - non_billable_noshow_rate
        # TODO: implement apply_noshow_rules()
        billable_noshow_rate = 0.0      # placeholder
        non_billable_noshow_rate = 0.0  # placeholder

        # ── Step 3: Billed utilization forecast ──────────────────────
        # billed_util = completed_util + billable_noshow_contribution
        # TODO: implement billed_utilization_calc()
        billed_utilization = 0.0  # placeholder

        # ── Step 4: Blended revenue per Kent-Leg ─────────────────────
        # weighted avg across all contracts by expected volume
        # TODO: implement blended_revenue_calc()
        blended_revenue = 0.0  # placeholder

        # ── Step 5: Concentration check ──────────────────────────────
        # No single contract > 20% of total volume or revenue
        # TODO: implement concentration_check()
        top_volume_pct = 0.0   # placeholder
        top_revenue_pct = 0.0  # placeholder
        concentration_flag = (
            top_volume_pct > VIABILITY.contract_concentration_max
            or top_revenue_pct > VIABILITY.contract_concentration_max
        )

        # ── Step 6: Bad-revenue flagging ─────────────────────────────
        # TODO: implement per-contract revenue check
        bad_revenue_flag = False  # placeholder

        return ContractProfile(
            quality_volume_pct=quality_volume_pct,
            filler_volume_pct=filler_volume_pct,
            billed_utilization_forecast=billed_utilization,
            blended_revenue_per_kent_leg=blended_revenue,
            expected_billable_noshow_rate=billable_noshow_rate,
            expected_non_billable_noshow_rate=non_billable_noshow_rate,
            top_contract_volume_pct=top_volume_pct,
            top_contract_revenue_pct=top_revenue_pct,
            concentration_flag=concentration_flag,
            bad_revenue_flag=bad_revenue_flag,
        )

    def summarize(self, output: ContractProfile) -> Dict[str, Any]:
        return {
            "quality_volume_pct": output.quality_volume_pct,
            "filler_volume_pct": output.filler_volume_pct,
            "billed_utilization": output.billed_utilization_forecast,
            "blended_rev_per_kl": output.blended_revenue_per_kent_leg,
            "non_billable_noshow_rate": output.expected_non_billable_noshow_rate,
            "concentration_flag": output.concentration_flag,
            "bad_revenue_flag": output.bad_revenue_flag,
        }
