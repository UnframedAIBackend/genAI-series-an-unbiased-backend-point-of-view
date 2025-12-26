from typing import Dict, Type, Union

from src.core.database.database_engine import DatabaseEngine


class RepositoryRegistry:
    _registry: Dict[str, Type] = {}

    @classmethod
    def register(cls, name: Union[str, DatabaseEngine], repository_class: Type):
        key = name.value if isinstance(name, DatabaseEngine) else str(name)
        cls._registry[key] = repository_class

    @classmethod
    def get(cls, name: Union[str, DatabaseEngine]) -> Type:
        key = name.value if isinstance(name, DatabaseEngine) else str(name)
        repo_class = cls._registry.get(key)
        if not repo_class:
            raise ValueError(f"Repository '{key}' not found in registry. Make sure it is imported and registered.")
        return repo_class


repository_registry = RepositoryRegistry
