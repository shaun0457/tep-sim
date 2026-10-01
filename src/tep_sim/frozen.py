"""Deep immutability for caller-visible authoritative data, and JSON-safe thawing."""
from types import MappingProxyType
from typing import Any, Mapping


def deep_freeze(value: Any) -> Any:
    """Recursively copy mappings to read-only proxies and sequences to tuples."""
    if isinstance(value, Mapping):
        return MappingProxyType({key: deep_freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple, set, frozenset)):
        items = sorted(value) if isinstance(value, (set, frozenset)) else value
        return tuple(deep_freeze(item) for item in items)
    return value


def thaw(value: Any) -> Any:
    """Fresh, mutable, JSON-safe copy of a frozen structure (for persistence/export)."""
    if isinstance(value, Mapping):
        return {key: thaw(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [thaw(item) for item in value]
    return value
