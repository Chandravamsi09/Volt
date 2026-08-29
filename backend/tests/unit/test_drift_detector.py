"""
Unit Tests for Statistical Data & Model Drift Detection
"""

import numpy as np
import pytest
from backend.app.observability.drift.drift_monitor import DriftMonitor
from backend.app.observability.drift.statistical_detector import StatisticalDriftDetector


def test_psi_identical_distributions():
    detector = StatisticalDriftDetector()
    np.random.seed(42)
    baseline = np.random.normal(0, 1, 1000)
    current = np.random.normal(0, 1, 1000)

    psi_val = detector.calculate_psi(baseline, current)
    # PSI for same distribution should be tiny (< 0.1)
    assert psi_val < 0.1


def test_psi_and_ks_shifted_distributions():
    detector = StatisticalDriftDetector()
    np.random.seed(42)
    baseline = np.random.normal(0, 1, 1000)
    current_shifted = np.random.normal(3, 1.5, 1000)  # Strong mean and variance shift

    psi_val = detector.calculate_psi(baseline, current_shifted)
    ks_stat, p_val = detector.calculate_ks_test(baseline, current_shifted)

    assert psi_val > 0.25  # Substantial drift
    assert p_val < 0.001  # Statistically significant rejection of null hypothesis
