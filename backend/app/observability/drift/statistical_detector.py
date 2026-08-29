"""
Statistical Drift Metrics: PSI, Kolmogorov-Smirnov (KS-Test) & Wasserstein Distance
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from scipy import stats


@dataclass
class ColumnDriftResult:
    column_name: str
    drift_detected: bool
    metric_name: str
    metric_value: float
    threshold: float
    p_value: Optional[float] = None
    baseline_stats: Optional[Dict[str, float]] = None
    current_stats: Optional[Dict[str, float]] = None


class StatisticalDriftDetector:
    """Calculates statistical divergence between reference (baseline) and target (production) data."""

    @staticmethod
    def calculate_psi(
        expected: np.ndarray,
        actual: np.ndarray,
        num_buckets: int = 10,
    ) -> float:
        """Calculate Population Stability Index (PSI).

        PSI < 0.1: No significant change
        0.1 <= PSI < 0.25: Moderate shift
        PSI >= 0.25: Significant population drift
        """
        expected = expected[~np.isnan(expected)]
        actual = actual[~np.isnan(actual)]

        if len(expected) == 0 or len(actual) == 0:
            return 0.0

        # Create quantiles on baseline data
        percentiles = np.linspace(0, 100, num_buckets + 1)
        breakpoints = np.percentile(expected, percentiles)
        breakpoints[0] -= 1e-5
        breakpoints[-1] += 1e-5

        # Avoid non-unique breakpoints
        breakpoints = np.unique(breakpoints)
        if len(breakpoints) < 2:
            return 0.0

        expected_counts, _ = np.histogram(expected, bins=breakpoints)
        actual_counts, _ = np.histogram(actual, bins=breakpoints)

        # Smooth counts with small epsilon to prevent division by zero
        eps = 1e-4
        expected_pct = (expected_counts + eps) / (len(expected) + eps * len(expected_counts))
        actual_pct = (actual_counts + eps) / (len(actual) + eps * len(actual_counts))

        psi_val = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
        return float(max(0.0, psi_val))

    @staticmethod
    def calculate_ks_test(
        expected: np.ndarray,
        actual: np.ndarray,
    ) -> Tuple[float, float]:
        """Perform two-sample Kolmogorov-Smirnov test for continuous distributions."""
        expected = expected[~np.isnan(expected)]
        actual = actual[~np.isnan(actual)]

        if len(expected) == 0 or len(actual) == 0:
            return 0.0, 1.0

        res = stats.ks_2samp(expected, actual)
        return float(res.statistic), float(res.pvalue)

    @staticmethod
    def calculate_wasserstein_distance(
        expected: np.ndarray,
        actual: np.ndarray,
    ) -> float:
        """Calculate Wasserstein-1 (Earth Mover's) distance."""
        expected = expected[~np.isnan(expected)]
        actual = actual[~np.isnan(actual)]
        if len(expected) == 0 or len(actual) == 0:
            return 0.0
        return float(stats.wasserstein_distance(expected, actual))
