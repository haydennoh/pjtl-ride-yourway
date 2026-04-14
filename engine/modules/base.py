"""
Abstract base class for all engine modules.
Enforces a consistent interface: validate -> run -> summarize.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseModule(ABC):
    """
    Every module follows the same lifecycle:
      1. validate()  -- check that required inputs are present
      2. run()       -- execute the module logic, return typed output
      3. summarize() -- return a human-readable dict for dashboarding
    """

    name: str = "BaseModule"

    @abstractmethod
    def validate(self, inputs: Dict[str, Any]) -> bool:
        """Return True if all required inputs are present and sane."""
        ...

    @abstractmethod
    def run(self, **kwargs) -> Any:
        """Execute module logic. Returns the module's typed output dataclass."""
        ...

    @abstractmethod
    def summarize(self, output: Any) -> Dict[str, Any]:
        """Convert typed output to a flat dict for reporting / dashboards."""
        ...
