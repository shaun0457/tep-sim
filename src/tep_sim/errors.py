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

class ProcessGraphValidationError(EnvironmentError):
    """A structured process source cannot be normalized or bound without loss."""
    def __init__(self, issues):
        self.issues = tuple(issues)
        super().__init__("; ".join(f"{i.code}[{i.ref}]: {i.message}" for i in self.issues))

class UnknownProcessEntity(EnvironmentError):
    pass

class ScenarioRejected(EnvironmentError):
    """Base for semantic scenarios that did not compile to supported interventions."""
    def __init__(self, result):
        self.result = result
        super().__init__(getattr(result, "reason", repr(result)))

class UnsupportedScenarioError(ScenarioRejected, UnsupportedCapability):
    pass

class AmbiguousScenarioError(ScenarioRejected, InvalidIntervention):
    pass

class InvalidScenarioError(ScenarioRejected, InvalidIntervention):
    pass
