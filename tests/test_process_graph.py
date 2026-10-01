import ast
import copy
import json
import re
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

import tep_sim
from tep_sim import (REGISTRY, UPSTREAM_REVISION, BindingRelation, EdgeKind, NodeKind,
                     ProcessGraphValidationError, UnknownProcessEntity, build_process_graph,
                     load_process_graph)
from tep_sim.evaluator_bindings import (PACKAGED_EVALUATOR_FIXTURE,
                                        build_evaluator_disturbance_bindings,
                                        load_evaluator_disturbance_bindings)
from tep_sim.process import PACKAGED_GRAPH_FIXTURE, canonical_sha256

FIXTURES = Path(tep_sim.__file__).with_name("fixtures")
SRC = Path(tep_sim.__file__).parent


def raw_graph():
    return json.loads((FIXTURES / PACKAGED_GRAPH_FIXTURE).read_text(encoding="utf-8"))


def raw_evaluator():
    return json.loads((FIXTURES / PACKAGED_EVALUATOR_FIXTURE).read_text(encoding="utf-8"))


def unpinned(data):
    data["fixture_version"] = "0.1.0-test"
    return data


def codes(excinfo):
    return {issue.code for issue in excinfo.value.issues}


@pytest.fixture(scope="module")
def graph():
    return load_process_graph()


# -- acceptance 1: load the pinned structured representation -----------------------------
def test_load_pinned_graph_with_provenance(graph):
    prov = graph.provenance
    assert (prov.fixture_id, prov.fixture_version) == ("tep-process-graph", "0.2.0")
    assert prov.pinned and prov.upstream_revision == UPSTREAM_REVISION
    assert prov.content_sha256 == canonical_sha256(raw_graph())
    assert prov.source_kind == "CURATED_EQUIVALENT_GRAPH"
    assert prov.review_status == "HUMAN_VERIFIED" and prov.review_record is not None
    assert {s.source_id for s in prov.sources} == {
        "downs_vogel_1993", "upstream_constants", "sim_python_backend", "sim_fortran",
        "bathelt_ricker_jelali_2015"}
    assert len(graph.nodes()) == 17 and len(graph.edges()) == 18
    stream_numbers = sorted(e.stream_number for e in graph.edges() if e.stream_number)
    assert stream_numbers == list(range(1, 12))
    for entity in (*graph.nodes(), *graph.edges()):
        assert entity.source_refs
    for binding in graph.bindings():
        assert binding.provenance.source_refs


def test_ids_are_independent_of_source_formatting(graph, tmp_path):
    data = raw_graph()
    data["nodes"].reverse()
    data["edges"].reverse()
    data["bindings"].reverse()
    path = tmp_path / "reordered.json"
    path.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    other = load_process_graph(path)
    assert [n.node_id for n in other.nodes()] == [n.node_id for n in graph.nodes()]
    assert other.project_local("reactor") == graph.project_local("reactor")
    compact = tmp_path / "compact.json"
    compact.write_text(json.dumps(raw_graph(), separators=(",", ":")), encoding="utf-8")
    assert load_process_graph(compact).provenance.content_sha256 == \
        graph.provenance.content_sha256


# -- acceptance 2: connectivity, no silent dangling references --------------------------
def test_graph_is_connected_and_all_unbound_entities_are_explicit(graph):
    everything = {n.node_id for n in graph.nodes()}
    reached = {"reactor", *graph.upstream("reactor", max_depth=None),
               *graph.downstream("reactor", max_depth=None)}
    assert reached == everything
    for edge in graph.edges():
        assert graph.node(edge.source_node) and graph.node(edge.target_node)
    bound = {b.attached_to for b in graph.bindings()}
    warned = {w.ref for w in graph.validation_warnings}
    assert all(w.code == "INTENTIONALLY_UNBOUND" for w in graph.validation_warnings)
    assert warned == (everything | {e.edge_id for e in graph.edges()}) - bound


# -- acceptance 3: reactor topology and known bindings ------------------------------------
def test_reactor_topology_and_known_runtime_bindings(graph):
    assert graph.node("reactor").kind is NodeKind.REACTOR
    assert graph.upstream("reactor") == ("reactor_cooling_water_supply", "reactor_feed_mixer")
    assert graph.upstream("reactor", edge_kinds={EdgeKind.MATERIAL_STREAM}) == \
        ("reactor_feed_mixer",)
    assert graph.downstream("reactor") == ("condenser", "reactor_cooling_water_return")
    assert graph.downstream("reactor", max_depth=2, edge_kinds={EdgeKind.MATERIAL_STREAM}) == \
        ("condenser", "separator")
    assert graph.neighbors("reactor") == ("condenser", "reactor_cooling_water_return",
                                          "reactor_cooling_water_supply", "reactor_feed_mixer")
    assert graph.binding("XMEAS(9)").semantic_entity_id == "reactor.temperature_measurement"
    assert graph.binding("reactor_cooling.outlet_temperature").runtime_variable_id == \
        "XMEAS(21)"
    assert graph.binding("XMV(10)").semantic_entity_id == "reactor_cooling.flow_actuator"
    local = {b.runtime_variable_id for b in graph.measurements("reactor")}
    assert local == {"XMEAS(7)", "XMEAS(8)", "XMEAS(9)"}
    wide = {b.runtime_variable_id
            for b in graph.measurements("reactor", include_incident_streams=True)}
    assert {"XMEAS(9)", "XMEAS(21)", "XMEAS(6)"} <= wide
    actuators = {b.runtime_variable_id
                 for b in graph.actuators("reactor", include_incident_streams=True)}
    assert actuators == {"XMV(10)", "XMV(12)"}
    trace = graph.trace_stream("reactor_cooling_water_in")
    assert (trace.source.node_id, trace.target.node_id) == ("reactor_cooling_water_supply",
                                                            "reactor")
    assert [b.runtime_variable_id for b in trace.bindings] == ["XMV(10)"]


def test_recycle_loop_traversal_terminates_deterministically(graph):
    closure = graph.downstream("reactor_feed_mixer", max_depth=None,
                               edge_kinds={EdgeKind.MATERIAL_STREAM})
    assert "reactor_feed_mixer" not in closure
    assert closure == graph.downstream("reactor_feed_mixer", max_depth=None,
                                       edge_kinds=[EdgeKind.MATERIAL_STREAM])
    assert closure[:2] == ("reactor", "condenser")


def test_every_visible_xmeas_and_xmv_is_bound_exactly_once(graph):
    visible = sorted(k for k in REGISTRY if k.startswith(("XMEAS(", "XMV(")))
    assert sorted(b.runtime_variable_id for b in graph.bindings()) == visible
    for binding in graph.bindings():
        assert binding.relation in (BindingRelation.MEASURES, BindingRelation.ACTUATES)
        assert REGISTRY[binding.runtime_variable_id]  # identity from vendored registry


# -- acceptance 5: compact agent projection ------------------------------------------------
def test_local_projection_is_compact_immutable_and_json_safe(graph):
    projection = graph.project_local("reactor")
    data = projection.as_dict()
    text = json.dumps(data)
    assert "<" not in text and "source_refs" not in text  # no raw XML/source payload
    assert data["node"]["node_id"] == "reactor"
    assert {e["edge_id"] for e in data["incident_edges"]} == {
        "stream_6", "stream_7", "reactor_cooling_water_in", "reactor_cooling_water_out"}
    assert "separator" not in {n["node_id"] for n in data["neighbors"]}  # local only
    assert data["graph"]["content_sha256"] == graph.provenance.content_sha256
    runtime = {b["runtime_variable_id"] for b in data["bindings"]}
    assert {"XMEAS(9)", "XMEAS(21)", "XMV(10)"} <= runtime
    with pytest.raises(TypeError):
        projection.node["node_id"] = "x"
    with pytest.raises(FrozenInstanceError):
        projection.node = {}
    data["node"]["node_id"] = "mutated"
    assert graph.project_local("reactor").node["node_id"] == "reactor"
    assert graph.project_local("reactor") == projection


# -- blind-RCA candidate-leakage guard ------------------------------------------------------
def test_agent_visible_surface_cannot_enumerate_disturbance_candidates(graph):
    idv_names = [v.name for k, v in REGISTRY.items() if k.startswith("IDV(")
                 and v.name != "Unknown"]
    pattern = re.compile(r"IDV\s*\(", re.IGNORECASE)
    for node in graph.nodes():
        text = json.dumps(graph.project_local(node.node_id).as_dict())
        assert not pattern.search(text), node.node_id
        assert not any(name in text for name in idv_names), node.node_id
    for method in ("get_related_disturbances", "related_disturbances", "disturbances"):
        assert not hasattr(graph, method)
    for idv in ("IDV(4)", "IDV(14)"):
        with pytest.raises(UnknownProcessEntity):
            graph.binding(idv)
    assert all(b.runtime_variable_kind != "IDV" for b in graph.bindings())
    assert not [name for name, value in vars(tep_sim).items()
                if getattr(value, "__module__", "") == "tep_sim.evaluator_bindings"]
    with pytest.raises(ValueError):
        type(graph.project_local("reactor"))(
            graph={}, node={}, incident_edges=(), neighbors=(),
            bindings=({"runtime_variable_kind": "IDV"},))


def test_evaluator_registry_is_separate_hidden_and_version_bound(graph):
    evaluator = load_evaluator_disturbance_bindings(graph)
    assert evaluator.visibility == "EVALUATOR_ONLY"
    prov = evaluator.provenance
    assert prov.pinned and prov.graph_content_sha256 == graph.provenance.content_sha256
    bound = {b.runtime_variable_id for b in evaluator.bindings()}
    assert bound | set(evaluator.unbound_disturbances) == \
        {k for k in REGISTRY if k.startswith("IDV(")}
    assert not bound & set(evaluator.unbound_disturbances)
    assert evaluator.location_of("IDV(4)").attached_to == "reactor_cooling_water_in"
    assert {b.runtime_variable_id for b in evaluator.disturbances_at("reactor_cooling_water_in")} \
        == {"IDV(4)", "IDV(11)", "IDV(14)"}
    with pytest.raises(UnknownProcessEntity):
        evaluator.location_of("IDV(16)")
    # the evaluator load does not enrich the Agent-visible graph
    assert graph.project_local("reactor") == load_process_graph().project_local("reactor")


# -- acceptance 4 + validation negatives ----------------------------------------------------
def _find(items, key, value):
    return next(item for item in items if item[key] == value)


@pytest.mark.parametrize("mutate,code", [
    (lambda d: _find(d["bindings"], "runtime_variable_id", "XMEAS(9)").update(
        runtime_variable_id="XMEAS(99)"), "UNKNOWN_RUNTIME_VARIABLE"),
    (lambda d: _find(d["bindings"], "runtime_variable_id", "XMV(10)").update(
        runtime_variable_id="XMEAS(9)"), "RUNTIME_KIND_MISMATCH"),
    (lambda d: _find(d["bindings"], "runtime_variable_id", "XMEAS(8)").update(
        runtime_variable_id="XMEAS(9)"), "CONFLICTING_BINDING"),
    (lambda d: d["nodes"].append(copy.deepcopy(d["nodes"][0])), "DUPLICATE_ID"),
    (lambda d: _find(d["edges"], "edge_id", "stream_7").update(target_node="nowhere"),
     "DANGLING_EDGE"),
    (lambda d: _find(d["bindings"], "runtime_variable_id", "XMEAS(9)").update(
        attached_to="nowhere"), "DANGLING_ATTACHMENT"),
    (lambda d: _find(d["nodes"], "node_id", "reactor").update(kind="CSTR_MAGIC"),
     "UNNORMALIZABLE_ENTITY"),
    (lambda d: _find(d["nodes"], "node_id", "reactor").update(attributes={"x": [1]}),
     "UNNORMALIZABLE_ENTITY"),
    (lambda d: d["nodes"][0].update(unexpected="field"), "UNNORMALIZABLE_ENTITY"),
    (lambda d: d["expected_runtime_variables"].append("XMEAS(42)"), "EXPECTED_VARIABLE_ABSENT"),
    (lambda d: d["bindings"].remove(
        _find(d["bindings"], "runtime_variable_id", "XMEAS(9)")), "EXPECTED_VARIABLE_UNBOUND"),
    (lambda d: d["unbound_entities"].pop(), "UNDECLARED_UNBOUND_ENTITY"),
    (lambda d: d["unbound_entities"].append({"entity_id": "reactor", "reason": "x"}),
     "CONFLICTING_BINDING"),
    (lambda d: d["bindings"].append({
        "semantic_entity_id": "reactor.leak", "attached_to": "reactor", "relation": "DISTURBS",
        "runtime_variable_id": "IDV(4)", "quantity": "temperature",
        "provenance": {"method": "CURATED_MAPPING", "source_refs": ["downs_vogel_1993"]}}),
     "DISTURBANCE_BINDING_IN_VISIBLE_GRAPH"),
    (lambda d: _find(d["nodes"], "node_id", "reactor").update(
        attributes={"hint": "see IDV(4)"}), "DISTURBANCE_REFERENCE_IN_VISIBLE_GRAPH"),
    (lambda d: d.update(upstream_revision="0" * 40), "REVISION_MISMATCH"),
    (lambda d: d.update(schema_version="other/v9"), "SCHEMA_VERSION"),
    (lambda d: d["bindings"][0]["provenance"].update(source_refs=["unknown_paper"]),
     "UNKNOWN_SOURCE_REF"),
    (lambda d: d["bindings"][0].pop("provenance"), "MISSING_PROVENANCE"),
    (lambda d: d.pop("sources"), "MISSING_PROVENANCE"),
    (lambda d: d["sources"]["downs_vogel_1993"].update(note="free text"), "MISSING_PROVENANCE"),
    (lambda d: d["sources"]["downs_vogel_1993"].update(sha256="ABC"), "MISSING_PROVENANCE"),
    (lambda d: d.pop("review_record"), "MISSING_PROVENANCE"),
    (lambda d: d["review_record"].update(notes="free text"), "MISSING_PROVENANCE"),
    (lambda d: d["review_record"].update(signed_record_sha256="0" * 63), "MISSING_PROVENANCE"),
    (lambda d: d["review_record"].update(signed_record_sha256="a" * 64 + "\n"),
     "MISSING_PROVENANCE"),
    (lambda d: d["sources"]["downs_vogel_1993"].update(sha256="a" * 64 + "\n"),
     "MISSING_PROVENANCE"),
    (lambda d: d["review_record"].update(signed_on="Oct 1"), "MISSING_PROVENANCE"),
    (lambda d: d["review_record"].update(signed_on="20261001"), "MISSING_PROVENANCE"),
    (lambda d: d["source"].update(review_status="VERIFIED"), "REVIEW_STATUS_MISMATCH"),
    (lambda d: d["source"].pop("review_status"), "REVIEW_STATUS_MISMATCH"),
    (lambda d: d["source"].update(review_status="PENDING_HUMAN_REVIEW"),
     "REVIEW_STATUS_MISMATCH"),
    (lambda d: d["source"].update(notes="free text"), "MISSING_PROVENANCE"),
    (lambda d: d["bindings"][0]["provenance"].update(review_notes="free text"),
     "MISSING_PROVENANCE"),
    (lambda d: d["review_record"].update(reviewer=""), "MISSING_PROVENANCE"),
    (lambda d: d["bindings"][0]["provenance"].update(method="CURATED_MAPPING"),
     "REVIEW_STATUS_MISMATCH"),
])
def test_corrupted_fixture_is_rejected(mutate, code):
    data = unpinned(raw_graph())
    mutate(data)
    with pytest.raises(ProcessGraphValidationError) as excinfo:
        build_process_graph(data)
    assert code in codes(excinfo)


@pytest.mark.parametrize("spelling", ["see IDV(4)", "affected by IDV6", "IDV 3", "idv-3",
                                      "idv_1", "Idv14", "IDV_(12)"])
def test_disturbance_spellings_are_rejected_in_visible_graph(spelling):
    data = unpinned(raw_graph())
    _find(data["nodes"], "node_id", "reactor")["attributes"] = {"note": spelling}
    with pytest.raises(ProcessGraphValidationError) as excinfo:
        build_process_graph(data)
    assert codes(excinfo) == {"DISTURBANCE_REFERENCE_IN_VISIBLE_GRAPH"}


@pytest.mark.parametrize("field", ["fixture_id", "fixture_version"])
@pytest.mark.parametrize("value", [["x"], {"x": 1}, 3])
def test_non_string_fixture_identity_is_a_validation_error(field, value):
    for data, build in ((raw_graph(), build_process_graph),
                        (raw_evaluator(), lambda d: build_evaluator_disturbance_bindings(
                            d, load_process_graph()))):
        data[field] = value
        with pytest.raises(ProcessGraphValidationError) as excinfo:
            build(data)
        assert "UNNORMALIZABLE_ENTITY" in codes(excinfo)


def test_invalid_review_record_is_reported_once_not_as_a_status_mismatch():
    baseline = json.loads((FIXTURES / "tep_process_graph_v0.json").read_text(encoding="utf-8"))
    for data in (unpinned(raw_graph()), unpinned(baseline)):
        data["review_record"] = None
        with pytest.raises(ProcessGraphValidationError) as excinfo:
            build_process_graph(data)
        assert [i.code for i in excinfo.value.issues] == ["MISSING_PROVENANCE"]


def test_pinned_version_content_drift_is_rejected():
    data = raw_graph()
    _find(data["nodes"], "node_id", "reactor")["name"] = "Renamed reactor"
    with pytest.raises(ProcessGraphValidationError) as excinfo:
        build_process_graph(data)
    assert codes(excinfo) == {"PINNED_CONTENT_MISMATCH"}
    renamed = build_process_graph(unpinned(data))
    assert not renamed.provenance.pinned


def test_validation_reports_all_issues_and_unreadable_sources(tmp_path):
    data = unpinned(raw_graph())
    _find(data["bindings"], "runtime_variable_id", "XMEAS(9)")["runtime_variable_id"] = \
        "XMEAS(99)"
    _find(data["edges"], "edge_id", "stream_7")["target_node"] = "nowhere"
    with pytest.raises(ProcessGraphValidationError) as excinfo:
        build_process_graph(data)
    assert {"UNKNOWN_RUNTIME_VARIABLE", "DANGLING_EDGE"} <= codes(excinfo)
    bad = tmp_path / "bad.json"
    bad.write_text("<dexpi/>", encoding="utf-8")
    for source in (bad, tmp_path / "missing.json"):
        with pytest.raises(ProcessGraphValidationError):
            load_process_graph(source)
    for value in (None, [], {"nodes": {1, 2}}):
        with pytest.raises(ProcessGraphValidationError):
            build_process_graph(value)


@pytest.mark.parametrize("mutate,code", [
    (lambda d: d.update(visibility="AGENT_VISIBLE"), "VISIBILITY"),
    (lambda d: d.update(graph_content_sha256="0" * 64), "GRAPH_VERSION_MISMATCH"),
    (lambda d: d["unbound_runtime_variables"].pop(), "UNACCOUNTED_RUNTIME_VARIABLE"),
    (lambda d: d["bindings"][0].update(runtime_variable_id="IDV(21)"),
     "UNKNOWN_RUNTIME_VARIABLE"),
    (lambda d: d["bindings"][0].update(relation="MEASURES"), "RUNTIME_KIND_MISMATCH"),
    (lambda d: d["bindings"][0].update(attached_to="nowhere"), "DANGLING_ATTACHMENT"),
    (lambda d: d["bindings"][1].update(runtime_variable_id="IDV(1)"), "CONFLICTING_BINDING"),
    (lambda d: d["unbound_runtime_variables"].append(
        {"runtime_variable_id": "IDV(4)", "reason": "x"}), "CONFLICTING_BINDING"),
    (lambda d: d["unbound_runtime_variables"].append(
        {"runtime_variable_id": "XMEAS(1)", "reason": "x"}), "UNNORMALIZABLE_ENTITY"),
    (lambda d: d["unbound_runtime_variables"].append(
        {"runtime_variable_id": ["IDV(16)"], "reason": "x"}), "UNNORMALIZABLE_ENTITY"),
])
def test_corrupted_evaluator_bindings_are_rejected(graph, mutate, code):
    data = unpinned(raw_evaluator())
    mutate(data)
    with pytest.raises(ProcessGraphValidationError) as excinfo:
        build_evaluator_disturbance_bindings(data, graph)
    assert code in codes(excinfo)


def test_unknown_entities_and_bad_query_arguments_fail_explicitly(graph):
    for call in (lambda: graph.node("nope"), lambda: graph.edge("nope"),
                 lambda: graph.upstream("nope"), lambda: graph.project_local("stream_6"),
                 lambda: graph.measurements("nope"), lambda: graph.trace_stream("reactor"),
                 lambda: graph.binding("XMEAS(99)"), lambda: graph.node(["unhashable"])):
        with pytest.raises(UnknownProcessEntity):
            call()
    for kwargs in ({"max_depth": 0}, {"max_depth": True}, {"edge_kinds": set()},
                   {"edge_kinds": {"MATERIAL_STREAM"}}):
        with pytest.raises(ValueError):
            graph.upstream("reactor", **kwargs)


# -- separation of topology semantics from runtime simulator state ------------------------
def test_graph_is_immutable_and_holds_no_runtime_state(graph):
    with pytest.raises(AttributeError):
        graph._nodes = {}
    with pytest.raises(TypeError):
        graph.node("reactor").attributes["agitated"] = False
    with pytest.raises(FrozenInstanceError):
        graph.node("reactor").name = "x"
    for module in ("process.py", "bindings.py", "evaluator_bindings.py"):
        tree = ast.parse((SRC / module).read_text(encoding="utf-8"))
        imported = {(node.module or "") for node in ast.walk(tree)
                    if isinstance(node, ast.ImportFrom)}
        imported |= {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import)
                     for alias in node.names}
        forbidden = {"environment", "snapshot", "contracts", "tep", "numpy",
                     "industrial_agent_runtime", "tep_agent_lab", "langgraph"}
        assert not {name.lstrip(".").split(".")[0] for name in imported} & forbidden, module


def test_graph_queries_are_unaffected_by_simulation(graph, tmp_path):
    from tep_sim import ControlMode, DisturbanceIntervention, EnvironmentConfig, TEPEnvironment
    before = graph.project_local("reactor")
    env = TEPEnvironment(EnvironmentConfig(7, "python", ControlMode.CLOSED_LOOP, 3,
                                           UPSTREAM_REVISION, tmp_path))
    env.reset()
    env.apply(DisturbanceIntervention("IDV(4)", 1))
    env.step()
    env.close()
    assert graph.project_local("reactor") == before
    assert load_process_graph().provenance == graph.provenance


def test_xmeas22_known_nomenclature_disagreement_is_verified_without_renaming(graph):
    """XMEAS(22) is a recorded source disagreement, not a silent re-binding.

    Upstream/Fortran names it "Separator Cooling Water Outlet Temp"; the topology
    attaches it to the condenser cooling-water outlet per the TEP flowsheet. The
    human reviewer kept that attachment (Q1) in the new 0.2.0 version; 0.1.0 stays
    the curated, pending baseline.
    """
    assert REGISTRY["XMEAS(22)"].name == "Separator Cooling Water Outlet Temp"
    binding = graph.binding("XMEAS(22)")
    assert binding.attached_to == "condenser_cooling_water_out"
    assert binding.provenance.method.value == "HUMAN_VERIFIED_MAPPING"
    assert graph.provenance.review_status == "HUMAN_VERIFIED"
    assert graph.provenance.fixture_version == "0.2.0" and graph.provenance.pinned
    baseline = load_process_graph(FIXTURES / "tep_process_graph_v0.json")
    assert baseline.binding("XMEAS(22)").attached_to == binding.attached_to
    assert baseline.binding("XMEAS(22)").provenance.method.value == "CURATED_MAPPING"
    assert baseline.provenance.review_status == "PENDING_HUMAN_REVIEW"
