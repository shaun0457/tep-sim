"""A3 promotion: tep-process-graph 0.2.0 implements the signed human review record.

The promotion makes no semantic decision. These tests prove that 0.2.0 is the
0.1.0 topology/bindings with human-verified provenance, that it points to the exact
signed record, and that the evaluator-only boundary still holds.
"""
import hashlib
import json
import re

import pytest

import tep_sim
from tep_sim import REGISTRY, UPSTREAM_REVISION, BindingMethod, ReviewRecordRef, load_process_graph
from tep_sim.evaluator_bindings import (PACKAGED_EVALUATOR_FIXTURE, PACKAGED_EVALUATOR_FIXTURES,
                                        EVALUATOR_ONLY, load_evaluator_disturbance_bindings)
from tep_sim.errors import ProcessGraphValidationError
from tep_sim.process import (HUMAN_VERIFIED, PACKAGED_GRAPH_FIXTURE, PACKAGED_GRAPH_FIXTURES,
                             PENDING_HUMAN_REVIEW, PINNED_FIXTURES, canonical_sha256)
from test_a3_review_package import (DISTURBANCE_REF, FIXTURES, MATRIX, ROOT,
                                    SIGNED_RECORD_SHA256, all_rows, lf_sha256,
                                    signed_record_sha256)

GRAPH_ID, EVALUATOR_ID = "tep-process-graph", "tep-evaluator-disturbance-bindings"
OLD_GRAPH_SHA = "2b4adf9406674fd7c91f3ee48a6a96ef23992d682036059dcb6706e825d01f2b"
OLD_EVALUATOR_SHA = "b497fdca4c4e436ba084bd120b989fe51e0b33a449164fe553be1f0c6b9b6a22"
NEW_GRAPH_SHA = "cc8ccc81e9f421238863457438465877850b19d9760740279e54a52468fe9a87"
NEW_EVALUATOR_SHA = "25e4c60885d273c4abb3214411bf1d99a392ebe2d540f9d716624205b13a9cb5"
SPEC = ROOT / "docs" / "specs" / "dexpi-binding-v0.md"
F10_SOURCES = {"sim_python_backend", "sim_fortran", "bathelt_ricker_jelali_2015"}


def raw(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def without_provenance(data):
    """Drop exactly the fields a promotion may change; everything else must match."""
    data = {k: v for k, v in data.items()
            if k not in ("fixture_version", "review_record", "sources")}
    data["source"] = {k: v for k, v in data["source"].items()
                      if k not in ("description", "review_status")}
    for key in ("nodes", "edges"):
        data[key] = [{k: v for k, v in item.items() if k != "source_refs"}
                     for item in data[key]]
    data["bindings"] = [{**b, "provenance": sorted(b["provenance"])} for b in data["bindings"]]
    return data


@pytest.fixture(scope="module")
def package():
    return json.loads(MATRIX.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def old():
    return load_process_graph(FIXTURES / PACKAGED_GRAPH_FIXTURES["0.1.0"])


@pytest.fixture(scope="module")
def new():
    return load_process_graph(FIXTURES / PACKAGED_GRAPH_FIXTURES["0.2.0"])


def binding_semantics(graph):
    return sorted((b.semantic_entity_id, b.runtime_variable_id, b.runtime_variable_kind,
                   b.relation.value, b.attached_to, b.quantity) for b in graph.bindings())


# -- 1, 2: 0.1.0 history is immutable ---------------------------------------------------------
def test_historical_graph_and_evaluator_0_1_0_are_byte_and_content_immutable(package):
    graph_subject, evaluator_subject = package["subject_fixtures"]
    graph_file = FIXTURES / PACKAGED_GRAPH_FIXTURES["0.1.0"]
    evaluator_file = FIXTURES / PACKAGED_EVALUATOR_FIXTURES["0.1.0"]
    assert lf_sha256(graph_file) == graph_subject["file_sha256_lf"]
    assert lf_sha256(evaluator_file) == evaluator_subject["file_sha256_lf"]
    assert canonical_sha256(raw(graph_file.name)) == OLD_GRAPH_SHA == \
        PINNED_FIXTURES[(GRAPH_ID, "0.1.0")]
    assert canonical_sha256(raw(evaluator_file.name)) == OLD_EVALUATOR_SHA == \
        PINNED_FIXTURES[(EVALUATOR_ID, "0.1.0")]


# -- 3, 4, 5, 6: promoted graph identity, status and bindings ---------------------------------
def test_promoted_graph_is_pinned_0_2_0_and_human_verified(new):
    prov = new.provenance
    assert (prov.fixture_id, prov.fixture_version) == (GRAPH_ID, "0.2.0")
    assert prov.pinned and prov.content_sha256 == NEW_GRAPH_SHA == \
        PINNED_FIXTURES[(GRAPH_ID, "0.2.0")] == canonical_sha256(raw(PACKAGED_GRAPH_FIXTURE))
    assert prov.review_status == HUMAN_VERIFIED == "HUMAN_VERIFIED"
    assert prov.source_kind == "CURATED_EQUIVALENT_GRAPH"  # Q7: accepted source form


def test_all_53_bindings_are_human_verified_and_resolve_in_the_registry(new):
    bindings = new.bindings()
    assert len(bindings) == 53
    assert {b.provenance.method for b in bindings} == {BindingMethod.HUMAN_VERIFIED_MAPPING}
    visible = {k for k in REGISTRY if k.startswith(("XMEAS(", "XMV("))}
    assert {b.runtime_variable_id for b in bindings} == visible
    for binding in bindings:
        assert binding.runtime_variable_kind in ("XMEAS", "XMV")
        assert binding.describe()["runtime_variable_name"] == \
            REGISTRY[binding.runtime_variable_id].name


# -- 7, 13: semantic equivalence with 0.1.0 -------------------------------------------------
def test_0_2_0_is_semantically_identical_to_0_1_0(old, new):
    assert without_provenance(raw(PACKAGED_GRAPH_FIXTURES["0.1.0"])) == \
        without_provenance(raw(PACKAGED_GRAPH_FIXTURES["0.2.0"]))
    node = lambda n: (n.node_id, n.kind, n.name, n.tag, dict(n.attributes))  # noqa: E731
    edge = lambda e: (e.edge_id, e.kind, e.source_node, e.target_node, e.name,  # noqa: E731
                      e.stream_number, dict(e.attributes))
    assert list(map(node, old.nodes())) == list(map(node, new.nodes()))
    assert list(map(edge, old.edges())) == list(map(edge, new.edges()))
    assert binding_semantics(old) == binding_semantics(new)
    assert old.validation_warnings == new.validation_warnings
    for node_id in (n.node_id for n in new.nodes()):
        local_old, local_new = old.project_local(node_id).as_dict(), \
            new.project_local(node_id).as_dict()
        assert local_old.pop("graph") != local_new.pop("graph")
        assert local_old == local_new, node_id
    # what differs is exactly the version/review provenance
    assert (old.provenance.fixture_version, new.provenance.fixture_version) == ("0.1.0", "0.2.0")
    assert (old.provenance.review_status, new.provenance.review_status) == \
        (PENDING_HUMAN_REVIEW, HUMAN_VERIFIED)
    assert old.provenance.review_record is None and new.provenance.review_record is not None
    assert {b.provenance.method for b in old.bindings()} == {BindingMethod.CURATED_MAPPING}


def test_no_condensate_return_or_other_new_edge_is_introduced(old, new):
    assert [e.edge_id for e in new.edges()] == [e.edge_id for e in old.edges()]
    assert len(new.edges()) == 18 and len(new.nodes()) == 17
    steam = [e for e in new.edges() if "stripper" in (e.source_node, e.target_node)
             and e.kind.value == "UTILITY_STREAM"]
    assert [(e.edge_id, e.source_node, e.target_node) for e in steam] == \
        [("stripper_steam", "stripper_steam_supply", "stripper")]


# -- 8-12: recorded decisions Q1-Q4 carried forward ----------------------------------------
def test_q1_xmeas22_keeps_condenser_cooling_water_attachment_and_runtime_name(new):
    binding = new.binding("XMEAS(22)")
    assert (binding.semantic_entity_id, binding.attached_to) == \
        ("condenser_cooling.outlet_temperature", "condenser_cooling_water_out")
    assert REGISTRY["XMEAS(22)"].name == "Separator Cooling Water Outlet Temp"  # not renamed
    assert binding.describe()["runtime_variable_name"] == REGISTRY["XMEAS(22)"].name


def test_q2_xmeas16_stays_on_stripper_with_ptv_source_in_the_signed_record(new, package):
    binding = new.binding("XMEAS(16)")
    assert (binding.semantic_entity_id, binding.attached_to) == \
        ("stripper.pressure_measurement", "stripper")
    assert binding.provenance.method is BindingMethod.HUMAN_VERIFIED_MAPPING
    # the PTV runtime source is recorded once, in the signed record the fixture references
    row = next(r for r in package["bindings"] if r["runtime_variable_id"] == "XMEAS(16)")
    assert row["human_reviewer_decision"] == "ACCEPT" and row["attached_to"] == "stripper"
    assert "PTV" in row["review_notes"] and "keep attachment on stripper" in row["review_notes"]
    assert "PTV" in package["signoff"]["decisions"]["Q2"]
    assert new.provenance.review_record.signed_record_sha256 == signed_record_sha256(package)
    spec = " ".join(SPEC.read_text(encoding="utf-8").split())
    assert ("A ProcessGraph semantic attachment identifies the engineering quantity/equipment "
            "relation exposed to the Agent. It does not require the simulator to maintain a "
            "distinct physical state variable at that exact graph node.") in spec
    assert "the simulator numerical source is `PTV`, the modeled vapor-zone pressure" in spec


def test_q3_cooling_water_actuators_stay_on_inlet_edges_as_functional_control(new):
    for runtime_id, edge_id in (("XMV(10)", "reactor_cooling_water_in"),
                                ("XMV(11)", "condenser_cooling_water_in")):
        binding = new.binding(runtime_id)
        assert binding.attached_to == edge_id and binding.relation.value == "ACTUATES"
        assert new.trace_stream(edge_id).edge.kind.value == "UTILITY_STREAM"
    spec = " ".join(SPEC.read_text(encoding="utf-8").split())
    assert ("`ACTUATES` v0 represents functional control of the associated process/utility "
            "path. It is not a geometric assertion about the exact valve symbol location in "
            "a P&ID.") in spec


def test_q4_cooling_water_line_numbers_stay_null(new):
    for edge_id in ("reactor_cooling_water_in", "reactor_cooling_water_out",
                    "condenser_cooling_water_in", "condenser_cooling_water_out"):
        assert new.edge(edge_id).stream_number is None, edge_id
    assert sorted(e.stream_number for e in new.edges() if e.stream_number) == list(range(1, 12))


# -- 14, 15: F-10 source provenance and the signed review record -------------------------------
def test_f10_sources_are_the_review_package_identities_and_cited_per_row(new, package):
    sources = {s.source_id: s for s in new.provenance.sources}
    assert F10_SOURCES <= set(sources)
    for source_id, source in sources.items():
        expected = package["sources"][source_id]
        assert (source.title, source.locator, source.revision, source.sha256) == \
            (expected["title"], expected["locator"], expected.get("revision"),
             expected.get("sha256")), source_id
        path = ROOT / source.locator
        if source.sha256:
            assert hashlib.sha256(path.read_bytes()).hexdigest() == source.sha256, source_id
        else:
            assert source.revision == UPSTREAM_REVISION and path.is_file(), source_id

    def cited(row):
        return tuple(sorted({item["source_id"] for item in row["evidence"]}))

    rows = {r["semantic_entity_id"]: r for r in package["bindings"]}
    for binding in new.bindings():
        refs = binding.provenance.source_refs
        assert refs == cited(rows[binding.semantic_entity_id]), binding.semantic_entity_id
        assert {"sim_python_backend", "sim_fortran", "bathelt_ricker_jelali_2015"} <= set(refs)
    topology = {**{r["node_id"]: r for r in package["topology"]["nodes"]},
                **{r["edge_id"]: r for r in package["topology"]["edges"]}}
    for entity in (*new.nodes(), *new.edges()):
        entity_id = getattr(entity, "node_id", None) or entity.edge_id
        assert entity.source_refs == cited(topology[entity_id]), entity_id


def test_review_record_reference_is_the_exact_signed_record(new, package):
    record = new.provenance.review_record
    assert isinstance(record, ReviewRecordRef)
    assert record == ReviewRecordRef(
        review_package_id=package["review_package_id"],
        review_package_version=package["review_package_version"],
        reviewer=package["signoff"]["reviewer"], signed_on=package["signoff"]["date"],
        locator=MATRIX.relative_to(ROOT).as_posix(),
        signed_record_sha256=SIGNED_RECORD_SHA256)
    assert (record.review_package_version, record.reviewer, record.signed_on) == \
        ("0.2.0", "chengting", "2026-10-01")
    assert signed_record_sha256(package) == SIGNED_RECORD_SHA256
    assert package["status"] == "HUMAN_SIGNOFF_RECORDED"
    assert package["signoff"]["package_decision"] == "ACCEPT"
    assert {r["human_reviewer_decision"] for r in all_rows(package)} == {"ACCEPT"}
    assert len(all_rows(package)) == 88


# -- 16, 17: evaluator 0.2.0 ----------------------------------------------------------------
def test_promoted_evaluator_is_bound_to_graph_0_2_0_with_unchanged_mappings(old, new):
    evaluator = load_evaluator_disturbance_bindings(new)
    historical = load_evaluator_disturbance_bindings(
        old, FIXTURES / PACKAGED_EVALUATOR_FIXTURES["0.1.0"])
    prov = evaluator.provenance
    assert (prov.fixture_id, prov.fixture_version, prov.pinned) == (EVALUATOR_ID, "0.2.0", True)
    assert prov.content_sha256 == NEW_EVALUATOR_SHA == PINNED_FIXTURES[(EVALUATOR_ID, "0.2.0")]
    assert (prov.graph_fixture_id, prov.graph_fixture_version, prov.graph_content_sha256) == \
        (GRAPH_ID, "0.2.0", NEW_GRAPH_SHA)
    assert historical.provenance.graph_content_sha256 == OLD_GRAPH_SHA
    assert evaluator.visibility == historical.visibility == EVALUATOR_ONLY
    assert raw(PACKAGED_EVALUATOR_FIXTURE)["visibility"] == EVALUATOR_ONLY
    semantics = lambda e: sorted((b.semantic_entity_id, b.runtime_variable_id,  # noqa: E731
                                  b.relation.value, b.attached_to, b.quantity)
                                 for b in e.bindings())
    assert semantics(evaluator) == semantics(historical)
    assert dict(evaluator.unbound_disturbances) == dict(historical.unbound_disturbances)
    # the default evaluator follows the graph version; a mismatched pair is rejected
    assert load_evaluator_disturbance_bindings(old).provenance == historical.provenance
    for graph, version in ((old, "0.2.0"), (new, "0.1.0")):
        with pytest.raises(ProcessGraphValidationError):
            load_evaluator_disturbance_bindings(
                graph, FIXTURES / PACKAGED_EVALUATOR_FIXTURES[version])


# -- 18: evaluator-only leakage boundary ----------------------------------------------------
def test_promoted_agent_visible_graph_holds_no_disturbance_information(new):
    idv_names = [v.name.lower() for k, v in REGISTRY.items()
                 if k.startswith("IDV(") and v.name != "Unknown"]
    text = (FIXTURES / PACKAGED_GRAPH_FIXTURE).read_text(encoding="utf-8")
    projections = json.dumps([new.project_local(n.node_id).as_dict() for n in new.nodes()])
    record = json.dumps(vars(new.provenance.review_record))
    for label, visible in {"fixture": text, "projections": projections,
                           "review record": record}.items():
        assert not DISTURBANCE_REF.search(visible), label
        assert not [name for name in idv_names if name in visible.lower()], label
        assert not re.search(r"\b(fault|disturb\w*|sticking|random variation|evaluator)\b",
                             visible.lower()), label
    assert {b.relation.value for b in new.bindings()} == {"MEASURES", "ACTUATES"}
    assert {b["runtime_variable_kind"] for local in json.loads(projections)
            for b in local["bindings"]} == {"XMEAS", "XMV"}
    # Q1: the XMEAS(22) projection carries only the measurement, no cause information
    condenser = new.project_local("condenser").as_dict()
    xmeas22 = next(b for b in condenser["bindings"] if b["runtime_variable_id"] == "XMEAS(22)")
    assert set(xmeas22) == {"semantic_entity_id", "attached_to", "relation",
                            "runtime_variable_id", "runtime_variable_kind",
                            "runtime_variable_name", "unit", "quantity"}


def test_agent_graph_loading_never_reaches_evaluator_contents(new):
    assert not hasattr(new, "disturbances_at") and not hasattr(new, "location_of")
    assert not {f for f in vars(new.provenance) if "evaluator" in f or "disturb" in f}
    assert not [name for name, value in vars(tep_sim).items()
                if getattr(value, "__module__", "") == "tep_sim.evaluator_bindings"]
    before = new.project_local("reactor")
    load_evaluator_disturbance_bindings(new)
    assert new.project_local("reactor") == before == load_process_graph().project_local("reactor")


# -- 19, 20: canonical default and historical access ------------------------------------------
def test_default_loader_is_the_verified_graph_and_0_1_0_stays_accessible(old):
    default = load_process_graph()
    assert PACKAGED_GRAPH_FIXTURE == PACKAGED_GRAPH_FIXTURES["0.2.0"]
    assert PACKAGED_EVALUATOR_FIXTURE == PACKAGED_EVALUATOR_FIXTURES["0.2.0"]
    assert (default.provenance.fixture_version, default.provenance.review_status) == \
        ("0.2.0", HUMAN_VERIFIED)
    assert default.provenance.content_sha256 == NEW_GRAPH_SHA
    assert load_evaluator_disturbance_bindings(default).provenance.graph_content_sha256 == \
        NEW_GRAPH_SHA
    assert (old.provenance.fixture_version, old.provenance.review_status,
            old.provenance.pinned) == ("0.1.0", PENDING_HUMAN_REVIEW, True)
    assert old.provenance.content_sha256 == OLD_GRAPH_SHA
    for version, name in PACKAGED_GRAPH_FIXTURES.items():
        assert raw(name)["fixture_version"] == version
    for version, name in PACKAGED_EVALUATOR_FIXTURES.items():
        assert raw(name)["fixture_version"] == raw(name)["graph_fixture_version"] == version
