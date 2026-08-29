"""
Centralized Feature Catalog & Metadata Registry
"""

from typing import Dict, List, Optional
from backend.app.core.exceptions import FeatureStoreError
from backend.app.feature_store.definitions import Entity, FeatureView


class FeatureRegistry:
    """In-memory and persistent metadata catalog for entities and feature views."""

    def __init__(self):
        self._entities: Dict[str, Entity] = {}
        self._feature_views: Dict[str, FeatureView] = {}

    def register_entity(self, entity: Entity) -> Entity:
        self._entities[entity.name] = entity
        return entity

    def get_entity(self, name: str) -> Entity:
        if name not in self._entities:
            raise FeatureStoreError(f"Entity '{name}' not found in registry.")
        return self._entities[name]

    def list_entities(self) -> List[Entity]:
        return list(self._entities.values())

    def register_feature_view(self, view: FeatureView) -> FeatureView:
        # Validate that all referenced entities exist
        for entity_name in view.entities:
            if entity_name not in self._entities:
                raise FeatureStoreError(
                    f"Referenced entity '{entity_name}' does not exist in registry."
                )
        self._feature_views[view.name] = view
        return view

    def get_feature_view(self, name: str) -> FeatureView:
        if name not in self._feature_views:
            raise FeatureStoreError(f"FeatureView '{name}' not found in registry.")
        return self._feature_views[name]

    def list_feature_views(self) -> List[FeatureView]:
        return list(self._feature_views.values())


# Global singleton registry
feature_registry = FeatureRegistry()
