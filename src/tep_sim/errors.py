"""Distinguishable request, capability, lifecycle, and execution errors."""
class EnvironmentError(Exception):
    pass

class InvalidIntervention(EnvironmentError):
    pass

class UnknownVariable(InvalidIntervention):
    pass

class UnsupportedCapability(EnvironmentError):
    pass

class IncompatibleControlMode(EnvironmentError):
    pass

class InvalidEnvironmentState(EnvironmentError):
    pass

class SimulationFailure(EnvironmentError):
    pass

class SnapshotFailure(EnvironmentError):
    pass
