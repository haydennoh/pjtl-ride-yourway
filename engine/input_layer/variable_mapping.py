"""
Variable Mapping -- translates normalized metrics into the granular
internal variables that each module expects as input.

This is the bridge between "what the spreadsheet says" and "what
the engine modules need." Each module's input contract is defined
in engine/models/metrics.py.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class VariableMapper:
    """
    Maps normalized Q1 data into the historical_data dict consumed
    by Pipeline.run().
    """

    def map(self, normalized_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Produce the full historical_data payload for the pipeline.

        Returns:
            {
                "baselines": { ... },           # for Module 1
                "contracts": { ... },           # for Module 2
                "cost_assumptions": { ... },    # for Module 4
                "revenue_by_mode": { ... },     # for Module 5
            }
        """
        return {
            "baselines": self._build_baselines(normalized_data),
            "contracts": self._build_contract_data(normalized_data),
            "cost_assumptions": self._build_cost_assumptions(normalized_data),
            "revenue_by_mode": self._build_revenue_by_mode(normalized_data),
        }

    def _build_baselines(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build Module 1 baselines from historical performance.

        Maps:
          Total Performance -> per-region daily averages
            - avg_daily_rides_by_region
            - avg_daily_kent_legs_by_region
            - completion_rate_by_region
            - cancellation_rate_by_region
            - noshow_rate_by_region
            - day_of_week_distribution

          Mode Breakdown -> mode proportions
            - mode_pct (ambulatory, wheelchair, stretcher)
            - kl_multiplier_by_mode

          Regional Performance -> per-region fleet/capacity baselines
            - vehicles_by_region
            - vehicle_utilization_by_region
        """
        # TODO: implement extraction from normalized data
        return {
            "avg_daily_rides": {},
            "avg_daily_kent_legs": {},
            "completion_rate": {},
            "noshow_rate": {},
            "mode_pct": {},
            "kl_multiplier_by_mode": {},
            "day_of_week_distribution": {},
        }

    def _build_contract_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build Module 2 contract data from historical contracts.

        Maps:
          Contract Volume -> per-payer volumes and concentrations
          Revenue by Payer -> per-payer revenue and billability

        Output:
          {
              "contracts": [
                  {"payer": ..., "volume": ..., "revenue": ..., "type": ...},
              ],
              "total_volume": ...,
              "total_revenue": ...,
              "quality_volume_pct": ...,
              "filler_volume_pct": ...,
              "billable_noshow_rate": ...,
              "non_billable_noshow_rate": ...,
          }
        """
        # TODO: implement
        return {}

    def _build_cost_assumptions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build Module 4 cost inputs from Weekly Margin data.

        Maps:
          Weekly Margin -> average daily costs by category
            - daily_overhead (Fixed Overhead Cost)
            - daily_fixed_operating (Fixed Operating Cost)
            - daily_gas (Gas)
            - daily_driver_wage (Driver Wage)
            - daily_capx (CapX)

          SecureCare Profit -> SC-specific cost structure
        """
        # TODO: implement extraction from weekly margin data
        return {
            "daily_overhead": 0.0,
            "daily_fixed_operating": 0.0,
            "daily_gas": 0.0,
            "daily_driver_wage": 0.0,
            "daily_capx": 0.0,
        }

    def _build_revenue_by_mode(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Build Module 5 revenue-per-KL by mode.

        Maps:
          Mode Breakdown -> Revenue By Mode / Kent Legs by Mode
            = avg revenue per Kent Leg per mode
        """
        # TODO: implement
        return {
            "ambulatory": 0.0,
            "wheelchair": 0.0,
            "stretcher": 0.0,
            "securecare": 0.0,
        }
