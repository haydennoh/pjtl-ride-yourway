"""
Dashboard output formatting for the viability report.

Produces structured output suitable for:
  - CLI printing (for development)
  - JSON export (for web dashboards)
  - Spreadsheet generation (for sharing with stakeholders)
"""

from __future__ import annotations

import json
from typing import Any, Dict

from engine.models.metrics import ViabilityReport, ConditionResult


class DashboardFormatter:
    """Formats a ViabilityReport into various output representations."""

    def to_cli(self, report: ViabilityReport) -> str:
        """Pretty-print the viability report for terminal output."""

        lines = []
        lines.append("=" * 70)
        lines.append(f"  MARKET VIABILITY REPORT: {report.region_name.upper()}")
        lines.append("=" * 70)
        lines.append("")

        # Go / No-Go banner
        decision = "GO -- MARKET IS LAUNCH-READY" if report.go_decision else "NO-GO -- CONDITIONS NOT MET"
        lines.append(f"  Decision:  {decision}")
        lines.append(f"  Projected Margin:  {report.projected_margin:.1%}")
        lines.append(f"  Conditions Passing:  {report.passing_count} / {len(report.conditions)}")
        lines.append("")

        # Condition detail table
        lines.append("-" * 70)
        lines.append(f"  {'#':<4}{'Condition':<35}{'Target':<18}{'Actual':<12}{'Status'}")
        lines.append("-" * 70)

        for c in report.conditions:
            status = "PASS" if c.passed else "FAIL"
            actual_str = self._format_value(c)
            lines.append(f"  {c.metric_number:<4}{c.name:<35}{c.target:<18}{actual_str:<12}{status}")

        lines.append("-" * 70)
        lines.append("")

        # Mitigations
        if report.recommended_mitigations:
            lines.append("  RECOMMENDED MITIGATIONS:")
            for i, m in enumerate(report.recommended_mitigations, 1):
                lines.append(f"    {i}. {m}")
            lines.append("")

        lines.append("=" * 70)
        return "\n".join(lines)

    def to_dict(self, report: ViabilityReport) -> Dict[str, Any]:
        """Convert report to a JSON-serializable dict."""
        return {
            "region": report.region_name,
            "go_decision": report.go_decision,
            "projected_margin": report.projected_margin,
            "passing": report.passing_count,
            "failing": report.failing_count,
            "conditions": [
                {
                    "metric": c.metric_number,
                    "name": c.name,
                    "target": c.target,
                    "actual": c.actual_value,
                    "passed": c.passed,
                    "gap": c.gap,
                }
                for c in report.conditions
            ],
            "mitigations": report.recommended_mitigations,
        }

    def to_json(self, report: ViabilityReport, indent: int = 2) -> str:
        """Serialize report to JSON string."""
        return json.dumps(self.to_dict(report), indent=indent)

    @staticmethod
    def _format_value(condition: ConditionResult) -> str:
        """Format the actual value based on the metric type."""
        v = condition.actual_value
        if condition.metric_number in (4, 9):  # dollar values
            return f"${v:.2f}"
        elif condition.metric_number == 7:  # hours
            return f"{v:.1f} hrs"
        else:  # percentages
            return f"{v:.1%}"
