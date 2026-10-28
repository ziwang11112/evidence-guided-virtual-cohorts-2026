"""Contracts and immutable submissions for evidence-guided cohort generation.

Importing or validating this package never executes Agent code. Explicit
execution uses the separately configured, generator-only WSL/bubblewrap adapter.
"""

from .contracts import (
    ContractError,
    validate_evidence,
    validate_input,
    validate_output,
    validate_spec,
    validate_task,
)

__all__ = [
    "ContractError", "validate_task", "validate_input", "validate_output",
    "validate_evidence", "validate_spec",
]
