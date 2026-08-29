"""
Traffic Router for A/B Testing, Canary Rollouts & Shadow Serving
"""

import random
from dataclasses import dataclass
from typing import Dict, List, Optional
from backend.app.core.exceptions import ModelRegistryError


@dataclass
class RouteTarget:
    model_name: str
    version: str
    weight: float  # Percentage (e.g. 90.0, 10.0)
    is_shadow: bool = False


class TrafficRouter:
    """Dynamically routes inference requests across model variants based on weights."""

    def __init__(self):
        self._routes: Dict[str, List[RouteTarget]] = {}  # endpoint_name -> List[RouteTarget]

    def set_route(self, endpoint_name: str, targets: List[RouteTarget]) -> None:
        """Register or update routing policy for an endpoint."""
        primary_targets = [t for t in targets if not t.is_shadow]
        total_weight = sum(t.weight for t in primary_targets)
        if abs(total_weight - 100.0) > 0.01 and primary_targets:
            raise ModelRegistryError(f"Route primary targets weight must sum to 100%, got {total_weight}%")
        self._routes[endpoint_name] = targets

    def route_request(self, endpoint_name: str) -> tuple[RouteTarget, List[RouteTarget]]:
        """Select primary target using weighted random sampling, and return any shadow targets."""
        if endpoint_name not in self._routes:
            raise ModelRegistryError(f"No deployment route configured for endpoint '{endpoint_name}'")

        targets = self._routes[endpoint_name]
        primary_targets = [t for t in targets if not t.is_shadow]
        shadow_targets = [t for t in targets if t.is_shadow]

        if not primary_targets:
            raise ModelRegistryError(f"No active primary targets for endpoint '{endpoint_name}'")

        rand_val = random.uniform(0, 100.0)
        cumulative = 0.0
        selected = primary_targets[0]

        for target in primary_targets:
            cumulative += target.weight
            if rand_val <= cumulative:
                selected = target
                break

        return selected, shadow_targets


traffic_router = TrafficRouter()
