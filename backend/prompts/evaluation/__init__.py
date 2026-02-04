"""
Prompt Evaluation Suite.

Provides test cases and metrics for evaluating prompt effectiveness.
"""

from .test_cases import TEST_CASES, run_evaluation
from .metrics import PromptMetrics, evaluate_response

__all__ = [
    "TEST_CASES",
    "run_evaluation",
    "PromptMetrics",
    "evaluate_response",
]
