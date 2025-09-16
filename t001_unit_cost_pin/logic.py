"""Core calculations for the Unit Cost Pin utility."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CostBreakdown:
    """Represents the derived metrics for a task run."""

    cost_per_attempt: float
    expected_attempts: float
    success_probability: float
    cost_per_task: float
    monthly_cost: float
    breakeven_value: Optional[float]
    roi_per_task: Optional[float]


def _clamp_probability(p: float) -> float:
    return max(0.0, min(1.0, p))


def compute(
    pr_in_1k: float,
    pr_out_1k: float,
    tok_in: float,
    tok_out: float,
    p: float,
    r: int,
    overhead: float,
    volume: float,
    vps: Optional[float] = None,
) -> CostBreakdown:
    """Compute the core metrics for the Unit Cost Pin.

    >>> result = compute(0.003, 0.015, 1500, 1000, 0.8, 1, 1.15, 2000, 2.0)
    >>> round(result.cost_per_attempt, 5)
    0.0195
    >>> round(result.expected_attempts, 2)
    1.2
    >>> round(result.success_probability, 2)
    0.96
    >>> round(result.cost_per_task, 5)
    0.02691
    >>> round(result.monthly_cost, 2)
    53.82
    >>> round(result.breakeven_value or 0, 5)
    0.02803
    >>> round(result.roi_per_task or 0, 3)
    1.893
    """

    probability = _clamp_probability(p)
    retries = max(0, int(r))
    overhead_multiplier = max(overhead, 0.0)
    monthly_volume = max(volume, 0.0)

    cost_per_attempt = (tok_in / 1000.0) * pr_in_1k + (tok_out / 1000.0) * pr_out_1k

    if probability <= 0:
        expected_attempts = retries + 1.0
        success_probability = 0.0
    elif probability >= 1:
        expected_attempts = 1.0
        success_probability = 1.0
    else:
        failure_rate = 1.0 - probability
        success_probability = 1.0 - failure_rate ** (retries + 1)
        expected_attempts = (1.0 - failure_rate ** (retries + 1)) / probability

    cost_per_task = cost_per_attempt * expected_attempts * overhead_multiplier
    monthly_cost = cost_per_task * monthly_volume

    breakeven_value: Optional[float]
    if success_probability > 0:
        breakeven_value = cost_per_task / success_probability
    else:
        breakeven_value = None

    roi_per_task: Optional[float] = None
    if vps is not None:
        roi_per_task = vps * success_probability - cost_per_task

    return CostBreakdown(
        cost_per_attempt=cost_per_attempt,
        expected_attempts=expected_attempts,
        success_probability=success_probability,
        cost_per_task=cost_per_task,
        monthly_cost=monthly_cost,
        breakeven_value=breakeven_value,
        roi_per_task=roi_per_task,
    )
