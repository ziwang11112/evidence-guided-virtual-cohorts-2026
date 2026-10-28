"""Contracts and immutable submissions for evidence-guided cohort generation.

This package does not execute Agent code or provide an operating-system sandbox.
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
