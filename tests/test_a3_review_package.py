"""Mechanical checks for the A3 human-verification review package.

These tests prove that the review evidence exists, is complete, and still points at
the pinned content. They do NOT prove semantic correctness and cannot substitute for
the human sign-off recorded in docs/reviews/a3-process-graph-human-verification.md.
"""
import ast
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pytest

import tep_sim
from tep_sim import REGISTRY, UPSTREAM_REVISION, EdgeKind, load_process_graph
from tep_sim.process import PINNED_FIXTURES, canonical_sha256

ROOT = Path(__file__).resolve().parents[1]
REVIEWS = ROOT / "docs" / "reviews"
MATRIX = REVIEWS / "a3-process-graph-binding-review-v0.json"
REVIEW_DOC = REVIEWS / "a3-process-graph-human-verification.md"
FIXTURES = Path(tep_sim.__file__).with_name("fixtures")
GRAPH_FIXTURE = FIXTURES / "tep_process_graph_v0.json"
HUMAN_DECISIONS = frozenset({"PENDING", "ACCEPT", "REJECT", "NEEDS_SOURCE"})
DISTURBANCE_REF = re.compile(r"(?<![A-Za-z])IDV[\s_\-(]*\d+", re.IGNORECASE)
BINDING_FIELDS = ("semantic_entity_id", "runtime_variable_id", "runtime_variable_kind",
                  "relation", "attached_to", "quantity")

# cooling-water probe (0-based XMEAS indices into get_measurements())
XMEAS21, XMEAS22 = 20, 21
STEP_PCT, N_STEPS, SETTLE_WINDOW = 2.0, 36, 6
OWN_LOOP_RESPONSE, CROSSTALK_TOL = -0.1, 0.02


@pytest.fixture(scope="module")
def package():
    return json.loads(MATRIX.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def graph():
    return load_process_graph()


def lf_sha256(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def vendored_upstream_head():
    """Commit actually checked out in the submodule (``.git`` file -> gitdir -> HEAD)."""
    upstream = ROOT / "vendor" / "tep-sim-upstream"
    git = upstream / ".git"
    gitdir = git if git.is_dir() else (upstream / git.read_text(encoding="utf-8")
                                       .split(":", 1)[1].strip()).resolve()
    head = (gitdir / "HEAD").read_text(encoding="utf-8").strip()
    if head.startswith("ref: "):
        head = (gitdir / head[5:]).read_text(encoding="utf-8").strip()
    return head


def text_lines(path):
    # split on "\n" only, matching editor/grep line numbers (unlike str.splitlines)
    return path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n").split("\n")


def all_rows(package):
    return package["bindings"] + package["topology"]["nodes"] + package["topology"]["edges"]


def row_key(row):
    return tuple(row[field] for field in BINDING_FIELDS)


def binding_key(binding):
    return (binding.semantic_entity_id, binding.runtime_variable_id,
            binding.runtime_variable_kind, binding.relation.value, binding.attached_to,
            binding.quantity)


def markdown_tables(text):
    """Yield (header, cells) for every review row (``B-``/``N-``/``E-`` ids)."""
    header = None
    for line in text.split("\n"):
        if not line.startswith("|"):
            header = None
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if header is None:
            header = cells
        elif re.fullmatch(r"[BNE]-\d{2}", cells[0]):
            yield header, [cell.strip("`") for cell in cells]


def expected_cells(row):
    """Markdown cells (by header label) that must render this matrix row verbatim.

    Only the compact ``Evidence`` summary column is not compared; the JSON keeps the
    full, test-anchored evidence.
    """
    notes = f"{row['finding']}: {row['agent_notes']}" if row["finding"] else ""
    common = {"Proposed disposition": row["proposed_disposition"],
              "Human decision": row["human_reviewer_decision"],
              "Human review notes": row["review_notes"]}
    if row["review_id"].startswith("B-"):
        return {**common, "Semantic entity": row["semantic_entity_id"],
                "Runtime var": row["runtime_variable_id"], "Kind": row["runtime_variable_kind"],
                "Relation": row["relation"], "Fixture attachment": row["attached_to"],
                "Runtime name": row["runtime_variable_name"],
                "Nomen.": row["nomenclature_agreement"], "Topo.": row["topology_agreement"],
                "Assessment": row["evidence_assessment"], "Agent notes": notes}
    notes = notes or row["agent_notes"]
    if row["review_id"].startswith("N-"):
        return {**common, "Node": row["node_id"], "Kind": row["kind"],
                "Material upstream": ", ".join(row["material_upstream"]) or "—",
                "Material downstream": ", ".join(row["material_downstream"]) or "—",
                "Finding / notes": notes}
    return {**common, "Edge": row["edge_id"], "Kind": row["kind"],
            "Source → target": f"{row['source_node']} → {row['target_node']}",
            "Stream #": str(row["stream_number"] or "—"),
            "Direction": row["direction_check"], "Finding / notes": notes}


def imported_modules(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            names.add(node.module or "")
            names |= {alias.name for alias in node.names}
    return names


# -- coverage: every Agent-visible binding / entity has exactly one review row ---------------
def test_every_agent_visible_binding_has_exactly_one_matching_review_row(package, graph):
    rows = package["bindings"]
    assert Counter(map(row_key, rows)) == Counter(map(binding_key, graph.bindings()))
    assert len({r["review_id"] for r in all_rows(package)}) == len(all_rows(package))


def test_every_node_and_edge_has_a_topology_row_matching_the_graph(package, graph):
    material = {EdgeKind.MATERIAL_STREAM}
    nodes = {r["node_id"]: r for r in package["topology"]["nodes"]}
    edges = {r["edge_id"]: r for r in package["topology"]["edges"]}
    assert set(nodes) == {n.node_id for n in graph.nodes()}
    assert set(edges) == {e.edge_id for e in graph.edges()}
    for node_id, row in nodes.items():
        assert row["kind"] == graph.node(node_id).kind.value, node_id
        # stable topology query behavior: recorded answers are reproduced exactly
        assert tuple(row["material_upstream"]) == \
            graph.upstream(node_id, edge_kinds=material), node_id
        assert tuple(row["material_downstream"]) == \
            graph.downstream(node_id, edge_kinds=material), node_id
    for edge_id, row in edges.items():
        trace = graph.trace_stream(edge_id)
        assert (row["source_node"], row["target_node"], row["stream_number"], row["kind"]) == \
            (trace.source.node_id, trace.target.node_id, trace.edge.stream_number,
             trace.edge.kind.value), edge_id


# -- runtime identity is resolved from the canonical registry -----------------------------------
def test_review_rows_resolve_in_canonical_registry(package):
    assert package["upstream_revision"] == UPSTREAM_REVISION
    for row in package["bindings"]:
        rid = row["runtime_variable_id"]
        assert row["runtime_variable_name"] == REGISTRY[rid].name, rid
        assert rid.startswith(row["runtime_variable_kind"] + "("), rid


# -- evidence exists, is anchored, and is never the curated fixture itself --------------------
def test_every_review_row_has_resolvable_independent_evidence(package):
    sources = package["sources"]
    for row in all_rows(package):
        assert row["evidence"], row["review_id"]
        for item in row["evidence"]:
            source = sources[item["source_id"]]
            path = ROOT / source["locator"]
            assert path.is_file(), source["locator"]
            # prior curated mapping is not independent evidence for itself
            assert "fixtures" not in Path(source["locator"]).parts, row["review_id"]
            if source["kind"] == "VENDORED_SIMULATOR_SOURCE":
                # vendored code evidence is always line-anchored
                lines = text_lines(path)
                assert 1 <= item["line"] <= len(lines), (row["review_id"], item)
                assert item["anchor"] in lines[item["line"] - 1], (row["review_id"], item)
            else:
                assert "anchor" not in item and item["where"], row["review_id"]
            if "Fig." in item.get("where", ""):
                # figure readings were made by the automated agent; a human confirms them
                assert item.get("visual_reading") is True, (row["review_id"], item)
    for row in package["bindings"]:
        kinds = {sources[item["source_id"]]["kind"] for item in row["evidence"]}
        assert {"VENDORED_SIMULATOR_SOURCE", "PRIMARY_LITERATURE"} <= kinds, row["review_id"]


def test_every_source_is_pinned(package):
    for source_id, source in package["sources"].items():
        path = ROOT / source["locator"]
        if source["locator"].endswith(".pdf"):
            # binds the source id to the file content (some file names mislead; F-11)
            assert hashlib.sha256(path.read_bytes()).hexdigest() == source["sha256"], source_id
        elif source["kind"] == "VENDORED_SIMULATOR_SOURCE":
            assert source["revision"] == package["upstream_revision"] == \
                vendored_upstream_head(), source_id
        elif source["kind"] == "CANONICAL_RUNTIME_REGISTRY":
            # the registry must still be derived verbatim from the vendored constants
            from tep import constants
            for prefix, names in (("XMEAS", constants.MEASUREMENT_NAMES),
                                  ("XMV", constants.MANIPULATED_VAR_NAMES)):
                for index, name in enumerate(names, 1):
                    assert REGISTRY[f"{prefix}({index})"].name == name, source_id
        else:
            pytest.fail(f"unpinned source kind {source['kind']!r} for {source_id}")


# -- old fixture is immutable; nothing self-promotes to human verified ------------------------
def test_pinned_fixtures_are_byte_and_content_immutable(package, graph):
    graph_subject, evaluator_subject = package["subject_fixtures"]
    assert lf_sha256(GRAPH_FIXTURE) == graph_subject["file_sha256_lf"]
    assert lf_sha256(FIXTURES / "tep_evaluator_disturbance_bindings_v0.json") == \
        evaluator_subject["file_sha256_lf"]
    raw = json.loads(GRAPH_FIXTURE.read_text(encoding="utf-8"))
    assert canonical_sha256(raw) == graph_subject["canonical_sha256"] == \
        PINNED_FIXTURES[("tep-process-graph", "0.1.0")] == graph.provenance.content_sha256
    assert PINNED_FIXTURES[("tep-evaluator-disturbance-bindings", "0.1.0")] == \
        evaluator_subject["pinned_sha256"]
    # This package proposes no candidate graph/evaluator version. A promoted version is a
    # deliberate, human-signed-off change that updates this assertion (review doc §8, §10).
    subject_ids = {"tep-process-graph", "tep-evaluator-disturbance-bindings"}
    assert {key for key in PINNED_FIXTURES if key[0] in subject_ids} == \
        {(fixture_id, "0.1.0") for fixture_id in subject_ids}
    for path in FIXTURES.glob("*.json"):
        if path.name not in (GRAPH_FIXTURE.name, "tep_evaluator_disturbance_bindings_v0.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            assert data.get("fixture_id") not in subject_ids, path.name


def test_package_stays_unsigned_until_a_human_signoff_change(package, graph):
    """No automated edit may fill a decision. Real sign-off updates this test (doc §10)."""
    assert package["status"] == "PENDING_HUMAN_SIGNOFF"
    assert graph.provenance.review_status == "PENDING_HUMAN_REVIEW"
    assert all(b.provenance.method.value == "CURATED_MAPPING" for b in graph.bindings())
    for path in [*FIXTURES.glob("*.json"), MATRIX]:
        assert "HUMAN_VERIFIED" not in path.read_text(encoding="utf-8"), path.name
    assert set(package["human_decision_values"]) == HUMAN_DECISIONS
    for row in all_rows(package):
        assert row["human_reviewer_decision"] == "PENDING", row["review_id"]
        assert row["reviewer"] is None, row["review_id"]


def test_review_document_mirrors_the_matrix_column_by_column(package):
    rendered = {}
    for header, cells in markdown_tables(REVIEW_DOC.read_text(encoding="utf-8")):
        assert len(cells) == len(header), cells[0]
        assert cells[0] not in rendered, f"duplicate review row {cells[0]}"
        rendered[cells[0]] = dict(zip(header, cells))
    rows = all_rows(package)
    assert set(rendered) == {r["review_id"] for r in rows}
    for row in rows:
        cells = rendered[row["review_id"]]
        expected = expected_cells(row)
        assert set(expected) | {"ID", "Evidence", "Evidence (location)"} >= set(cells), \
            row["review_id"]
        for column, value in expected.items():
            assert cells[column] == value, (row["review_id"], column)


def test_promotion_always_requires_a_new_human_authored_fixture_version():
    """Spec: a human-verified mapping ships as a new fixture version, never in place.

    Verification provenance alone is reason for a new version, even with unchanged
    mappings; this package must not suggest otherwise or perform the promotion.
    """
    text = REVIEW_DOC.read_text(encoding="utf-8")
    section = text.split("## 8. Fixture versions and verification promotion", 1)[1] \
        .split("\n## 9.", 1)[0]
    normalized = " ".join(section.split())
    for rule in ("permanently represents the curated",
                 "No automated component may create a human-verified fixture",
                 "**MUST** publish a new verified fixture version",
                 "**even if no topology or binding changes.**",
                 "Verification provenance is itself versioned engineering truth",
                 "only** for rows the human reviewer explicitly accepted",
                 "corresponding new evaluator fixture version must be published"):
        assert rule in normalized, rule
    assert "pointless duplicate" not in text.lower()


def test_xmeas22_adjudication_presents_all_three_options():
    text = REVIEW_DOC.read_text(encoding="utf-8")
    section = text.split("## 5. XMEAS(22) adjudication package", 1)[1].split("\n## 6.", 1)[0]
    for option in ("**Option A: retain the condenser attachment**",
                   "**Option B: change to a separator attachment.**",
                   "**Option C: unresolved / insufficient evidence.**"):
        assert option in section
    assert "not a decision" in section


# -- evaluator-only boundary -------------------------------------------------------------------
def test_agent_visible_artifacts_hold_no_disturbance_data(package):
    idv_names = [v.name.lower() for k, v in REGISTRY.items()
                 if k.startswith("IDV(") and v.name != "Unknown"]
    graph_text = GRAPH_FIXTURE.read_text(encoding="utf-8")
    visible = {"graph fixture": graph_text, "matrix": MATRIX.read_text(encoding="utf-8"),
               "review doc": REVIEW_DOC.read_text(encoding="utf-8"),
               "spec": (ROOT / "docs/specs/dexpi-binding-v0.md").read_text(encoding="utf-8")}
    for label, text in visible.items():
        assert not DISTURBANCE_REF.search(text), label
        lowered = text.lower()
        assert not [name for name in idv_names if name in lowered], label
    # the matrix header names the evaluator fixture file; the graph and rows must not
    rows_text = json.dumps([package["bindings"], package["topology"]])
    for label, text in {"graph fixture": graph_text, "matrix rows": rows_text}.items():
        assert not re.search(r"\b(fault|disturb\w*|sticking|random variation)\b",
                             text.lower()), label
    assert all(row["relation"] in ("MEASURES", "ACTUATES") for row in package["bindings"])


def test_evaluator_bindings_module_is_imported_by_nothing_in_the_package():
    # static import check only; it does not see importlib-based dynamic imports
    for module in Path(tep_sim.__file__).parent.rglob("*.py"):
        if module.name == "evaluator_bindings.py":
            continue
        assert not any("evaluator_bindings" in name for name in imported_modules(module)), \
            module.name


# -- XMEAS(22) loop identity: runtime evidence, not a semantic sign-off ----------------------
def _probe_measurements(mv_index=None):
    from tep.simulator import ControlMode, TEPSimulator
    sim = TEPSimulator(random_seed=1234, control_mode=ControlMode.MANUAL, backend="python")
    sim.initialize()
    if mv_index is not None:
        sim.set_mv(mv_index, sim.get_manipulated_vars()[mv_index - 1] + STEP_PCT)
    samples = []
    for _ in range(N_STEPS):
        assert sim.step(), "simulator shut down during the probe"
        samples.append(sim.get_measurements().copy())
    assert np.isfinite(samples).all()
    return np.mean(samples[-SETTLE_WINDOW:], axis=0)


def test_cooling_water_outlet_temperatures_respond_to_their_own_loop_flow():
    """Same seed, +2 % MV step, 36 s: XMEAS(22) follows XMV(11), XMEAS(21) follows XMV(10).

    This mechanically supports that XMEAS(22) belongs to the loop actuated by XMV(11)
    ("Condenser Cooling Water Flow"). It does not decide the review item.
    """
    baseline = _probe_measurements()
    condenser = _probe_measurements(11) - baseline
    reactor = _probe_measurements(10) - baseline
    assert condenser[XMEAS22] < OWN_LOOP_RESPONSE and abs(condenser[XMEAS21]) < CROSSTALK_TOL
    assert reactor[XMEAS21] < OWN_LOOP_RESPONSE and abs(reactor[XMEAS22]) < CROSSTALK_TOL
