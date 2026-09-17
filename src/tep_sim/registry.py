"""Runtime identity and metadata sourced exclusively from pinned upstream."""
from dataclasses import dataclass
from types import MappingProxyType
from tep import constants

UPSTREAM_REVISION = "9a6c8e5fcef4a2850778704e7793c87b0a187005"

@dataclass(frozen=True)
class Variable:
    canonical_id: str
    index: int
    name: str
    unit: str | None


def _variables(prefix, names, units):
    return {f"{prefix}({i})": Variable(f"{prefix}({i})", i, name, unit)
            for i, (name, unit) in enumerate(zip(names, units, strict=True), 1)}


REGISTRY = MappingProxyType({
    **_variables("XMEAS", constants.MEASUREMENT_NAMES, constants.MEASUREMENT_UNITS),
    **_variables("XMV", constants.MANIPULATED_VAR_NAMES,
                 ["%"] * constants.NUM_MANIPULATED_VARS),
    **_variables("IDV", constants.DISTURBANCE_NAMES,
                 [None] * constants.NUM_DISTURBANCES),
})
