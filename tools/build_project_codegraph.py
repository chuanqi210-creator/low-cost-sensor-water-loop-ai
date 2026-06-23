#!/usr/bin/env python3
"""Build a lightweight project codegraph for agent orientation.

This is a local fallback for the GitHub CodeGraph skill when the CodeGraph CLI
is unavailable. It favors stable, scan-reducing artifacts over deep static
analysis: files, Python symbols, imports, experiment-agent links, test-source
links, and deliverable/output references.
"""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "deliverables" / "codegraph"
PACKET_DIR = OUTPUT_DIR / "packets"
ROOT_CODEGRAPH = ROOT / "CODEGRAPH.md"

SCAN_ROOTS = [
    "src",
    "experiments",
    "tests",
    "deliverables",
    "docs",
    "notes",
]

TEXT_SUFFIXES = {".py", ".md", ".json", ".toml", ".txt", ".csv"}
PARSE_SUFFIXES = {".py", ".md", ".json"}
IGNORE_PARTS = {
    ".venv",
    ".pytest_cache",
    "__pycache__",
    "low_cost_water_ai_loop.egg-info",
    "ppt",
}
IGNORE_SUFFIXES = {".pyc", ".pkl", ".png", ".jpg", ".jpeg", ".svg", ".docx", ".DS_Store"}

PATH_RE = re.compile(
    r"(?P<path>(?:outputs|deliverables|docs|notes|src|experiments|tests)/[A-Za-z0-9_./\\-]+)"
)
AGENT_RUN_RE = re.compile(r"run_agent(?P<num>\d+)_?(?P<slug>.*)\.py$")
TEST_RE = re.compile(r"test_(?P<slug>.+)\.py$")
MD_LINK_RE = re.compile(r"`(?P<path>(?:outputs|deliverables|docs|notes|src|experiments|tests)/[^`]+)`")


@dataclass
class Node:
    id: str
    kind: str
    label: str
    path: str | None = None
    layer: str | None = None
    tags: list[str] = field(default_factory=list)
    summary: str | None = None
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class Edge:
    source: str
    target: str
    kind: str
    confidence: str = "medium"
    evidence: str | None = None


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts & IGNORE_PARTS:
        return True
    if path.name in IGNORE_SUFFIXES:
        return True
    if path.suffix in IGNORE_SUFFIXES:
        return True
    if "deliverables" in parts and "codegraph" in parts:
        return True
    return False


def iter_project_files() -> list[Path]:
    files: list[Path] = []
    for root_name in SCAN_ROOTS:
        root = ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or should_skip(path):
                continue
            if path.suffix not in TEXT_SUFFIXES:
                continue
            files.append(path)
    root_files = [ROOT / "README.md", ROOT / "_总目录.md", ROOT / "pyproject.toml", ROOT / "requirements.txt"]
    files.extend(path for path in root_files if path.exists())
    return sorted(set(files), key=lambda p: rel(p))


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def line_count(path: Path) -> int:
    return read_text(path).count("\n") + 1


def layer_for(path: str) -> str:
    if path.startswith("src/water_ai/agents/"):
        return "agent_logic"
    if path.startswith("src/water_ai/"):
        return "core_model"
    if path.startswith("experiments/"):
        return "experiment_runner"
    if path.startswith("tests/"):
        return "verification"
    if path.startswith("deliverables/model_core_optimization/"):
        return "governance_deliverable"
    if path.startswith("deliverables/"):
        return "deliverable"
    if path.startswith("outputs/"):
        return "generated_artifact"
    if path.startswith("docs/"):
        return "specification"
    if path.startswith("notes/"):
        return "project_memory"
    return "project_root"


def tag_tokens(path: str) -> list[str]:
    stem = Path(path).stem.lower()
    tags = [token for token in re.split(r"[^a-zA-Z0-9]+", stem) if token]
    if "agent" in path:
        tags.append("agent")
    if "field" in path:
        tags.append("field")
    if "sensor" in path:
        tags.append("sensor")
    if "control" in path:
        tags.append("control")
    if "knowledge" in path or "kg" in path:
        tags.append("knowledge_graph")
    if "replay" in path:
        tags.append("replay")
    return sorted(set(tags))


def add_node(nodes: dict[str, Node], node: Node) -> None:
    existing = nodes.get(node.id)
    if existing is None:
        nodes[node.id] = node
        return
    existing.tags = sorted(set(existing.tags + node.tags))
    existing.metrics.update(node.metrics)
    if not existing.summary and node.summary:
        existing.summary = node.summary


def add_edge(edges: list[Edge], source: str, target: str, kind: str, confidence: str = "medium", evidence: str | None = None) -> None:
    edges.append(Edge(source=source, target=target, kind=kind, confidence=confidence, evidence=evidence))


def module_name_for(path: Path) -> str | None:
    rel_path = rel(path)
    if not rel_path.endswith(".py"):
        return None
    if rel_path.startswith("src/"):
        return rel_path.removeprefix("src/").removesuffix(".py").replace("/", ".")
    return rel_path.removesuffix(".py").replace("/", ".")


def internal_module_to_file(files: list[Path]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for path in files:
        module = module_name_for(path)
        if module:
            mapping[module] = rel(path)
    return mapping


def parse_python(
    path: Path,
    text: str,
    nodes: dict[str, Node],
    edges: list[Edge],
    module_to_file: dict[str, str],
) -> dict[str, Any]:
    file_id = f"file:{rel(path)}"
    stats: dict[str, Any] = {"classes": [], "functions": [], "imports": []}
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        add_node(
            nodes,
            Node(
                id=f"parse_error:{rel(path)}",
                kind="parse_error",
                label=f"Parse error in {rel(path)}",
                path=rel(path),
                layer=layer_for(rel(path)),
                summary=str(exc),
            ),
        )
        add_edge(edges, file_id, f"parse_error:{rel(path)}", "has_parse_error", "high")
        return stats

    module = module_name_for(path) or rel(path).removesuffix(".py").replace("/", ".")
    for item in ast.walk(tree):
        if isinstance(item, ast.ClassDef):
            stats["classes"].append(item.name)
            symbol_id = f"symbol:{module}.{item.name}"
            add_node(
                nodes,
                Node(
                    id=symbol_id,
                    kind="class",
                    label=item.name,
                    path=rel(path),
                    layer=layer_for(rel(path)),
                    tags=tag_tokens(item.name),
                    metrics={"line": item.lineno, "end_line": getattr(item, "end_lineno", item.lineno)},
                ),
            )
            add_edge(edges, file_id, symbol_id, "defines", "high", f"line {item.lineno}")
        elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            stats["functions"].append(item.name)
            symbol_id = f"symbol:{module}.{item.name}"
            add_node(
                nodes,
                Node(
                    id=symbol_id,
                    kind="function",
                    label=item.name,
                    path=rel(path),
                    layer=layer_for(rel(path)),
                    tags=tag_tokens(item.name),
                    metrics={"line": item.lineno, "end_line": getattr(item, "end_lineno", item.lineno)},
                ),
            )
            add_edge(edges, file_id, symbol_id, "defines", "high", f"line {item.lineno}")
        elif isinstance(item, ast.Import):
            for alias in item.names:
                stats["imports"].append(alias.name)
                add_import_edge(nodes, edges, file_id, alias.name, module_to_file)
        elif isinstance(item, ast.ImportFrom):
            mod = item.module or ""
            if item.level and module:
                mod = resolve_relative_module(module, item.level, mod)
            if mod:
                stats["imports"].append(mod)
                add_import_edge(nodes, edges, file_id, mod, module_to_file)

    for match in PATH_RE.finditer(text):
        target_path = match.group("path").rstrip(".,;)\"'")
        if target_path and target_path != rel(path):
            target_id = f"file:{target_path}"
            add_node(
                nodes,
                Node(
                    id=target_id,
                    kind="referenced_path",
                    label=Path(target_path).name,
                    path=target_path,
                    layer=layer_for(target_path),
                    tags=tag_tokens(target_path),
                ),
            )
            add_edge(edges, file_id, target_id, "references_path", "medium")

    return stats


def resolve_relative_module(current_module: str, level: int, module: str) -> str:
    parts = current_module.split(".")[:-1]
    keep = max(0, len(parts) - (level - 1))
    base = parts[:keep]
    if module:
        base.extend(module.split("."))
    return ".".join(base)


def add_import_edge(
    nodes: dict[str, Node],
    edges: list[Edge],
    file_id: str,
    module: str,
    module_to_file: dict[str, str],
) -> None:
    import_id = f"module:{module}"
    add_node(nodes, Node(id=import_id, kind="module", label=module, tags=tag_tokens(module)))
    add_edge(edges, file_id, import_id, "imports", "high")
    if module in module_to_file:
        add_edge(edges, file_id, f"file:{module_to_file[module]}", "imports_internal_file", "high")
        return
    parts = module.split(".")
    while len(parts) > 1:
        parts.pop()
        parent = ".".join(parts)
        if parent in module_to_file:
            add_edge(edges, file_id, f"file:{module_to_file[parent]}", "imports_internal_file", "medium")
            return


def parse_markdown(path: Path, text: str, nodes: dict[str, Node], edges: list[Edge]) -> dict[str, Any]:
    file_id = f"file:{rel(path)}"
    headings = [line.strip("# ").strip() for line in text.splitlines() if line.startswith("#")]
    stats = {"headings": headings[:20]}
    for heading in headings[:12]:
        heading_id = f"heading:{rel(path)}#{slugify(heading)}"
        add_node(
            nodes,
            Node(
                id=heading_id,
                kind="heading",
                label=heading,
                path=rel(path),
                layer=layer_for(rel(path)),
                tags=tag_tokens(heading),
            ),
        )
        add_edge(edges, file_id, heading_id, "has_heading", "high")
    for match in MD_LINK_RE.finditer(text):
        target_path = match.group("path").rstrip(".,;)\"'")
        add_node(
            nodes,
            Node(
                id=f"file:{target_path}",
                kind="referenced_path",
                label=Path(target_path).name,
                path=target_path,
                layer=layer_for(target_path),
                tags=tag_tokens(target_path),
            ),
        )
        add_edge(edges, file_id, f"file:{target_path}", "documents_or_references", "medium")
    return stats


def parse_json(path: Path, text: str) -> dict[str, Any]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {"json_error": True}
    if isinstance(data, dict):
        keys = list(data.keys())
        interesting = {
            key: data.get(key)
            for key in keys
            if key.endswith("status") or key.endswith("_status") or key.endswith("score") or key in {"status", "next_stage"}
        }
        return {"top_level_keys": keys[:80], "interesting_fields": interesting}
    if isinstance(data, list):
        return {"list_length": len(data)}
    return {"json_type": type(data).__name__}


def slugify(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9\u4e00-\u9fff]+", "-", text).strip("-")
    return slug[:80] or "heading"


def infer_test_edges(files: list[Path], nodes: dict[str, Node], edges: list[Edge]) -> None:
    source_by_slug: dict[str, list[str]] = defaultdict(list)
    for path in files:
        path_s = rel(path)
        if not path_s.endswith(".py"):
            continue
        stem = Path(path_s).stem
        normalized = stem.removesuffix("_agent")
        source_by_slug[normalized].append(path_s)
    for path in files:
        path_s = rel(path)
        match = TEST_RE.match(Path(path_s).name)
        if not match:
            continue
        slug = match.group("slug")
        candidates = []
        candidates.extend(source_by_slug.get(slug, []))
        candidates.extend(source_by_slug.get(f"{slug}_agent", []))
        candidates.extend(source_by_slug.get(slug.replace("_agent", ""), []))
        for candidate in sorted(set(candidates))[:4]:
            if candidate != path_s:
                add_edge(edges, f"file:{path_s}", f"file:{candidate}", "tests_or_verifies", "medium")


def infer_agent_edges(files: list[Path], nodes: dict[str, Node], edges: list[Edge]) -> list[dict[str, Any]]:
    agent_rows: list[dict[str, Any]] = []
    agent_files = {Path(rel(path)).stem.replace("_agent", ""): rel(path) for path in files if rel(path).startswith("src/water_ai/agents/") and rel(path).endswith("_agent.py")}
    deliverable_files = {Path(rel(path)).stem: rel(path) for path in files if rel(path).startswith("deliverables/") and rel(path).endswith(".md")}
    test_files = {Path(rel(path)).stem.removeprefix("test_").replace("_agent", ""): rel(path) for path in files if rel(path).startswith("tests/test_")}
    output_dirs = {path.name: rel(path) for path in (ROOT / "outputs").glob("*") if path.is_dir()} if (ROOT / "outputs").exists() else {}

    for path in files:
        path_s = rel(path)
        match = AGENT_RUN_RE.match(Path(path_s).name)
        if not match:
            continue
        number = int(match.group("num"))
        slug = match.group("slug").removesuffix("_")
        agent_id = f"agent:{number:02d}:{slug}"
        add_node(
            nodes,
            Node(
                id=agent_id,
                kind="agent_workflow",
                label=f"Agent{number} {slug}",
                path=path_s,
                layer="agent_workflow",
                tags=["agent", slug],
                metrics={"agent_number": number},
            ),
        )
        add_edge(edges, agent_id, f"file:{path_s}", "runs_experiment", "high")
        candidates = [slug, slug.replace("_", ""), f"{slug}_agent"]
        source_file = None
        for candidate in candidates:
            if candidate in agent_files:
                source_file = agent_files[candidate]
                break
        if source_file:
            add_edge(edges, agent_id, f"file:{source_file}", "implemented_by", "high")
        deliverable = deliverable_files.get(slug)
        if deliverable:
            add_edge(edges, agent_id, f"file:{deliverable}", "documented_by", "high")
        test_file = test_files.get(slug)
        if test_file:
            add_edge(edges, agent_id, f"file:{test_file}", "verified_by", "high")
        output_dir = output_dirs.get(f"agent{number}_{slug}") or output_dirs.get(slug)
        if output_dir:
            add_node(nodes, Node(id=f"dir:{output_dir}", kind="output_dir", label=Path(output_dir).name, path=output_dir, layer="generated_artifact", tags=["output", "agent"]))
            add_edge(edges, agent_id, f"dir:{output_dir}", "writes_output_dir", "medium")
        agent_rows.append(
            {
                "agent_number": number,
                "slug": slug,
                "runner": path_s,
                "source": source_file,
                "deliverable": deliverable,
                "test": test_file,
                "output_dir": output_dir,
            }
        )
    return sorted(agent_rows, key=lambda row: row["agent_number"])


def dedupe_edges(edges: list[Edge]) -> list[Edge]:
    seen: set[tuple[str, str, str]] = set()
    result: list[Edge] = []
    for edge in edges:
        key = (edge.source, edge.target, edge.kind)
        if key in seen:
            continue
        seen.add(key)
        result.append(edge)
    return result


def build_graph() -> dict[str, Any]:
    files = iter_project_files()
    module_to_file = internal_module_to_file(files)
    nodes: dict[str, Node] = {}
    edges: list[Edge] = []
    file_stats: dict[str, Any] = {}

    for path in files:
        path_s = rel(path)
        text = read_text(path) if path.suffix in PARSE_SUFFIXES or path.suffix in {".toml", ".txt"} else ""
        file_id = f"file:{path_s}"
        metrics = {"lines": line_count(path), "size_bytes": path.stat().st_size}
        add_node(
            nodes,
            Node(
                id=file_id,
                kind="file",
                label=Path(path_s).name,
                path=path_s,
                layer=layer_for(path_s),
                tags=tag_tokens(path_s),
                summary=first_summary_line(text),
                metrics=metrics,
            ),
        )
        stats: dict[str, Any] = {}
        if path.suffix == ".py":
            stats = parse_python(path, text, nodes, edges, module_to_file)
        elif path.suffix == ".md":
            stats = parse_markdown(path, text, nodes, edges)
        elif path.suffix == ".json":
            stats = parse_json(path, text)
        file_stats[path_s] = stats

    infer_test_edges(files, nodes, edges)
    agent_rows = infer_agent_edges(files, nodes, edges)
    edges = dedupe_edges(edges)

    layer_counts = Counter(node.layer or "unknown" for node in nodes.values())
    kind_counts = Counter(node.kind for node in nodes.values())
    edge_kind_counts = Counter(edge.kind for edge in edges)
    hotspot_files = compute_hotspots(nodes, edges)
    shortcuts = build_scan_shortcuts(agent_rows, hotspot_files)
    node_handles = build_node_handles(nodes)
    adjacency = build_adjacency(edges)
    task_routes = build_task_routes(agent_rows, hotspot_files)
    packets = build_packets(agent_rows, nodes, edges, adjacency)
    evaluation = build_codegraph_evaluation(summary={
        "file_count": len(files),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "agent_workflow_count": len(agent_rows),
    })

    graph = {
        "schema_version": "local-codegraph-v2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "source": {
            "skill": "lzehrung/codegraph/codegraph-skill",
            "cli_available": False,
            "fallback_reason": "codegraph CLI requires Node.js 24.10+, but node/npm/codegraph are not installed on this machine.",
        },
        "summary": {
            "file_count": len(files),
            "node_count": len(nodes),
            "edge_count": len(edges),
            "layer_counts": dict(sorted(layer_counts.items())),
            "kind_counts": dict(sorted(kind_counts.items())),
            "edge_kind_counts": dict(sorted(edge_kind_counts.items())),
            "agent_workflow_count": len(agent_rows),
        },
        "nodes": [node.__dict__ for node in sorted(nodes.values(), key=lambda item: item.id)],
        "edges": [edge.__dict__ for edge in sorted(edges, key=lambda item: (item.source, item.kind, item.target))],
        "file_stats": file_stats,
        "agent_index": agent_rows,
        "hotspot_files": hotspot_files,
        "scan_shortcuts": shortcuts,
        "node_handles": node_handles,
        "adjacency": adjacency,
        "task_routes": task_routes,
        "packets": packets,
        "fallback_evaluation": evaluation,
    }
    return graph


def first_summary_line(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            return stripped.strip("# ").strip()[:180]
        if stripped.startswith('"""') or stripped.startswith("'''"):
            return stripped.strip("\"' ")[:180]
        if stripped.startswith("//"):
            continue
        return stripped[:180]
    return None


def compute_hotspots(nodes: dict[str, Node], edges: list[Edge]) -> list[dict[str, Any]]:
    in_degree = Counter(edge.target for edge in edges)
    out_degree = Counter(edge.source for edge in edges)
    rows = []
    for node in nodes.values():
        if node.kind != "file" or not node.path:
            continue
        score = in_degree[node.id] * 2 + out_degree[node.id]
        if score <= 0:
            continue
        rows.append(
            {
                "path": node.path,
                "layer": node.layer,
                "in_degree": in_degree[node.id],
                "out_degree": out_degree[node.id],
                "scan_priority_score": score,
                "summary": node.summary,
            }
        )
    return sorted(rows, key=lambda row: (-row["scan_priority_score"], row["path"]))[:30]


def build_scan_shortcuts(agent_rows: list[dict[str, Any]], hotspot_files: list[dict[str, Any]]) -> dict[str, Any]:
    by_slug = {row["slug"]: row for row in agent_rows}
    focus_slugs = [
        "sensor_network_sparse_placement",
        "catalyst_activity_proxy",
        "multi_facility_collaborative_control",
        "multi_facility_replay_evaluation",
        "minimal_grey_box_physics",
        "soft_sensor_matrix_coupling",
        "knowledge_graph_reasoning",
        "main_chain_reconnection",
        "agent_architecture_consolidation",
        "pressure_resolution_replay_scenario_pack",
    ]
    focus = [by_slug[slug] for slug in focus_slugs if slug in by_slug]
    return {
        "first_read": [
            "CODEGRAPH.md",
            "notes/current_status.md",
            "deliverables/manifest.json",
            "deliverables/model_core_optimization/model_core_goal.md",
            "deliverables/model_core_optimization/quantified_goal_termination_criteria.md",
        ],
        "core_model_next_reads": focus,
        "hotspot_files": hotspot_files[:12],
        "rules": [
            "Read CODEGRAPH.md before broad scanning.",
            "Use agent_index to jump from Agent number to runner/source/test/output.",
            "Use hotspot_files only as orientation; verify behavior with tests or experiment runs.",
            "Synthetic/sample/template outputs are not field evidence.",
        ],
    }


def stable_handle(node_id: str) -> str:
    digest = hashlib.sha1(node_id.encode("utf-8")).hexdigest()[:10]
    prefix = node_id.split(":", 1)[0].replace("_", "-")
    return f"{prefix}-{digest}"


def build_node_handles(nodes: dict[str, Node]) -> dict[str, dict[str, Any]]:
    handles: dict[str, dict[str, Any]] = {}
    for node in sorted(nodes.values(), key=lambda item: item.id):
        handle = stable_handle(node.id)
        handles[handle] = {
            "node_id": node.id,
            "kind": node.kind,
            "label": node.label,
            "path": node.path,
            "layer": node.layer,
            "tags": node.tags,
        }
    return handles


def build_adjacency(edges: list[Edge]) -> dict[str, Any]:
    forward: dict[str, list[dict[str, str | None]]] = defaultdict(list)
    reverse: dict[str, list[dict[str, str | None]]] = defaultdict(list)
    for edge in edges:
        forward[edge.source].append(
            {
                "target": edge.target,
                "kind": edge.kind,
                "confidence": edge.confidence,
                "evidence": edge.evidence,
            }
        )
        reverse[edge.target].append(
            {
                "source": edge.source,
                "kind": edge.kind,
                "confidence": edge.confidence,
                "evidence": edge.evidence,
            }
        )
    return {
        "forward": {key: sorted(value, key=lambda item: (str(item["kind"]), str(item["target"]))) for key, value in forward.items()},
        "reverse": {key: sorted(value, key=lambda item: (str(item["kind"]), str(item["source"]))) for key, value in reverse.items()},
    }


def build_task_routes(agent_rows: list[dict[str, Any]], hotspot_files: list[dict[str, Any]]) -> dict[str, Any]:
    by_slug = {row["slug"]: row for row in agent_rows}
    def route(*slugs: str) -> list[dict[str, Any]]:
        return [by_slug[slug] for slug in slugs if slug in by_slug]

    return {
        "sparse_sensing_and_observation": route(
            "sensor_network_sparse_placement",
            "soft_sensor_matrix_coupling",
            "soft_sensor_field_holdout_gate",
            "weak_target_stratified_conformal",
        ),
        "grey_box_and_soft_sensor": route(
            "soft_sensor",
            "soft_sensor_uncertainty_validation",
            "soft_sensor_conformal_calibration",
            "minimal_grey_box_physics",
            "grey_box_dynamic_latency",
        ),
        "catalyst_activity_and_weak_state": route(
            "catalyst_activity_proxy",
            "weak_target_stratified_conformal",
            "minimal_grey_box_physics",
        ),
        "control_and_replay": route(
            "control_strategy",
            "multi_facility_collaborative_control",
            "multi_facility_replay_evaluation",
            "engineering_execution_constraints",
            "pressure_resolution_replay_scenario_pack",
        ),
        "field_evidence_and_release_gates": route(
            "field_replay_import",
            "timestamped_campaign_replay",
            "field_replay_calibration_gate",
            "field_replay_evidence_chain",
            "field_validation_queue_alignment",
            "claim_specific_field_package",
        ),
        "knowledge_and_governance": route(
            "knowledge_graph_curation",
            "literature_evidence",
            "knowledge_graph_reasoning",
            "main_chain_reconnection",
            "model_core_governance",
            "agent_architecture_consolidation",
        ),
        "fallback_hotspots": hotspot_files[:10],
    }


def build_packets(
    agent_rows: list[dict[str, Any]],
    nodes: dict[str, Node],
    edges: list[Edge],
    adjacency: dict[str, Any],
) -> dict[str, Any]:
    packet_slugs = {
        "sensor_network_sparse_placement",
        "catalyst_activity_proxy",
        "multi_facility_collaborative_control",
        "multi_facility_replay_evaluation",
        "minimal_grey_box_physics",
        "soft_sensor_matrix_coupling",
        "knowledge_graph_reasoning",
        "main_chain_reconnection",
        "agent_architecture_consolidation",
        "pressure_resolution_replay_scenario_pack",
    }
    node_by_id = {node.id: node for node in nodes.values()}
    edge_by_source = defaultdict(list)
    edge_by_target = defaultdict(list)
    for edge in edges:
        edge_by_source[edge.source].append(edge)
        edge_by_target[edge.target].append(edge)

    packets: dict[str, Any] = {}
    for row in agent_rows:
        if row["slug"] not in packet_slugs:
            continue
        agent_id = f"agent:{row['agent_number']:02d}:{row['slug']}"
        related_ids = {agent_id}
        for key in ("runner", "source", "deliverable", "test"):
            value = row.get(key)
            if value:
                related_ids.add(f"file:{value}")
        if row.get("output_dir"):
            related_ids.add(f"dir:{row['output_dir']}")
        for edge in edge_by_source.get(agent_id, []):
            related_ids.add(edge.target)
        for edge in edge_by_target.get(agent_id, []):
            related_ids.add(edge.source)
        packet = {
            "handle": stable_handle(agent_id),
            "agent_id": agent_id,
            "agent_number": row["agent_number"],
            "slug": row["slug"],
            "runner": row.get("runner"),
            "source": row.get("source"),
            "deliverable": row.get("deliverable"),
            "test": row.get("test"),
            "output_dir": row.get("output_dir"),
            "related_nodes": [
                node_to_packet_entry(node_by_id[node_id])
                for node_id in sorted(related_ids)
                if node_id in node_by_id
            ],
            "forward_edges": [
                edge.__dict__
                for edge in sorted(edge_by_source.get(agent_id, []), key=lambda item: (item.kind, item.target))
            ],
            "reverse_edges": [
                edge.__dict__
                for edge in sorted(edge_by_target.get(agent_id, []), key=lambda item: (item.kind, item.source))
            ],
            "how_to_use": [
                "Read runner first to understand generated artifacts and report wiring.",
                "Read source next for behavior and interfaces.",
                "Read test before editing to preserve current contract.",
                "Treat output_dir and deliverable as evidence of previous runs, not as field validation unless explicitly marked field-origin.",
            ],
        }
        packets[row["slug"]] = packet
    return packets


def node_to_packet_entry(node: Node) -> dict[str, Any]:
    return {
        "handle": stable_handle(node.id),
        "node_id": node.id,
        "kind": node.kind,
        "label": node.label,
        "path": node.path,
        "layer": node.layer,
        "summary": node.summary,
        "metrics": node.metrics,
    }


def build_codegraph_evaluation(summary: dict[str, int]) -> dict[str, Any]:
    return {
        "verdict": "hybrid_fallback_is_useful_but_not_equivalent_to_native_codegraph",
        "better_than_native_for_this_project": [
            "Encodes project-specific research main chain and agent semantics.",
            "Links agent runner/source/test/deliverable/output in a way generic CodeGraph would not infer by itself.",
            "Preserves field/synthetic/template evidence boundaries in the navigation layer.",
        ],
        "weaker_than_native_codegraph": [
            "No Tree-sitter level symbol resolution or call graph.",
            "No native packet/search/explain command surface.",
            "No duplicate detection, architecture drift, PR impact, or review artifact generation.",
            "No incremental cache or MCP server.",
        ],
        "optimization_done_in_v2": [
            "Added stable node handles.",
            "Added forward and reverse adjacency indexes.",
            "Added task route index by model workstream.",
            "Added packet-like bundles for core agents.",
            "Added explicit fallback evaluation and boundary notes.",
        ],
        "recommended_next_upgrade": [
            "Install Node.js 24.10+ and @lzehrung/codegraph when CLI-level symbol navigation becomes worth the setup cost.",
            "Keep the local project packets even after native CodeGraph is installed, because they encode research semantics.",
        ],
        "summary_at_evaluation": summary,
    }


def write_outputs(graph: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PACKET_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "project_codegraph.json").write_text(
        json.dumps(graph, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_csv(OUTPUT_DIR / "project_codegraph_nodes.csv", graph["nodes"])
    write_csv(OUTPUT_DIR / "project_codegraph_edges.csv", graph["edges"])
    (OUTPUT_DIR / "codegraph_summary.md").write_text(render_summary(graph), encoding="utf-8")
    (OUTPUT_DIR / "scan_shortcuts.md").write_text(render_scan_shortcuts(graph), encoding="utf-8")
    (OUTPUT_DIR / "task_routes.json").write_text(json.dumps(graph["task_routes"], ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTPUT_DIR / "native_vs_fallback_evaluation.md").write_text(render_fallback_evaluation(graph), encoding="utf-8")
    for slug, packet in graph["packets"].items():
        (PACKET_DIR / f"{slug}.json").write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
        (PACKET_DIR / f"{slug}.md").write_text(render_packet(packet), encoding="utf-8")
    ROOT_CODEGRAPH.write_text(render_root_codegraph(graph), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value for key, value in row.items()})


def render_summary(graph: dict[str, Any]) -> str:
    summary = graph["summary"]
    hotspots = graph["hotspot_files"][:15]
    agent_rows = graph["agent_index"]
    lines = [
        "# 项目 CodeGraph 知识图谱摘要",
        "",
        "用途：减少后续 scan 摩擦。以后进入项目时，先读根目录 `CODEGRAPH.md`，再按本图谱定位文件、agent、实验、测试和产物。",
        "",
        "## 生成信息",
        "",
        f"- 生成时间：`{graph['generated_at']}`",
        "- 来源：已安装 GitHub `lzehrung/codegraph` skill；由于当前机器没有 Node.js 24.10+ / `codegraph` CLI，本次使用项目本地 fallback 构建。",
        f"- 文件数：`{summary['file_count']}`",
        f"- 节点数：`{summary['node_count']}`",
        f"- 边数：`{summary['edge_count']}`",
        f"- Agent workflow 数：`{summary['agent_workflow_count']}`",
        "",
        "## 层级计数",
        "",
        "| 层级 | 节点数 |",
        "| --- | ---: |",
    ]
    for layer, count in summary["layer_counts"].items():
        lines.append(f"| `{layer}` | {count} |")
    lines.extend(
        [
            "",
            "## 高优先级扫描入口",
            "",
            "| 优先级 | 文件 | 层级 | 入边 | 出边 | 说明 |",
            "| ---: | --- | --- | ---: | ---: | --- |",
        ]
    )
    for idx, row in enumerate(hotspots, 1):
        lines.append(
            f"| {idx} | `{row['path']}` | `{row['layer']}` | {row['in_degree']} | {row['out_degree']} | {row.get('summary') or ''} |"
        )
    lines.extend(
        [
            "",
            "## Agent 索引",
            "",
            "| Agent | slug | runner | source | test | output |",
            "| ---: | --- | --- | --- | --- | --- |",
        ]
    )
    for row in agent_rows:
        lines.append(
            f"| {row['agent_number']} | `{row['slug']}` | `{row['runner']}` | `{row.get('source') or ''}` | `{row.get('test') or ''}` | `{row.get('output_dir') or ''}` |"
        )
    lines.extend(
        [
            "",
            "## 机器可读文件",
            "",
            "- `deliverables/codegraph/project_codegraph.json`：完整节点、边、agent 索引、hotspot 和 scan shortcut。",
            "- `deliverables/codegraph/project_codegraph_nodes.csv`：节点表。",
            "- `deliverables/codegraph/project_codegraph_edges.csv`：边表。",
            "- `deliverables/codegraph/scan_shortcuts.md`：给后续 agent 的最短阅读路径。",
            "- `deliverables/codegraph/task_routes.json`：按工作流主题组织的跳转索引。",
            "- `deliverables/codegraph/packets/`：核心 agent 的 packet 式上下文包。",
            "- `deliverables/codegraph/native_vs_fallback_evaluation.md`：原生 CodeGraph 与本地 fallback 的效果对比。",
        ]
    )
    return "\n".join(lines) + "\n"


def render_scan_shortcuts(graph: dict[str, Any]) -> str:
    shortcuts = graph["scan_shortcuts"]
    lines = [
        "# Scan Shortcuts",
        "",
        "## First Read",
        "",
    ]
    for path in shortcuts["first_read"]:
        lines.append(f"- `{path}`")
    lines.extend(["", "## Core Model Next Reads", ""])
    for row in shortcuts["core_model_next_reads"]:
        lines.append(
            f"- Agent{row['agent_number']} `{row['slug']}`：runner `{row['runner']}`；source `{row.get('source') or 'missing'}`；test `{row.get('test') or 'missing'}`。"
        )
    lines.extend(["", "## Rules", ""])
    for rule in shortcuts["rules"]:
        lines.append(f"- {rule}")
    lines.extend(
        [
            "",
            "## Packet Handles",
            "",
            "核心 agent 已生成 packet 文件。后续如果任务明确落在某个核心 agent，优先读对应 packet：",
            "",
        ]
    )
    for slug, packet in graph["packets"].items():
        lines.append(f"- `{slug}`：`deliverables/codegraph/packets/{slug}.md`，handle `{packet['handle']}`")
    return "\n".join(lines) + "\n"


def render_fallback_evaluation(graph: dict[str, Any]) -> str:
    evaluation = graph["fallback_evaluation"]
    lines = [
        "# Native CodeGraph 与本地 Fallback 效果评估",
        "",
        f"结论：`{evaluation['verdict']}`。",
        "",
        "## 本地 fallback 更适合本项目的地方",
        "",
    ]
    for item in evaluation["better_than_native_for_this_project"]:
        lines.append(f"- {item}")
    lines.extend(["", "## 不如原生 CodeGraph 的地方", ""])
    for item in evaluation["weaker_than_native_codegraph"]:
        lines.append(f"- {item}")
    lines.extend(["", "## 本轮已补的不足", ""])
    for item in evaluation["optimization_done_in_v2"]:
        lines.append(f"- {item}")
    lines.extend(["", "## 下一步升级建议", ""])
    for item in evaluation["recommended_next_upgrade"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## 使用边界",
            "",
            "- 本地图谱用于减少 scan 摩擦和定位上下文，不证明运行时行为。",
            "- 结构关系不能替代测试、实验 replay、field holdout 或人工复核。",
            "- 即便未来安装原生 CodeGraph CLI，也应保留这些项目语义 packet，因为原生工具不会天然理解本项目的研究主链和证据边界。",
        ]
    )
    return "\n".join(lines) + "\n"


def render_packet(packet: dict[str, Any]) -> str:
    lines = [
        f"# Packet: Agent{packet['agent_number']} {packet['slug']}",
        "",
        f"- Handle: `{packet['handle']}`",
        f"- Runner: `{packet.get('runner') or ''}`",
        f"- Source: `{packet.get('source') or ''}`",
        f"- Test: `{packet.get('test') or ''}`",
        f"- Deliverable: `{packet.get('deliverable') or ''}`",
        f"- Output dir: `{packet.get('output_dir') or ''}`",
        "",
        "## How To Use",
        "",
    ]
    for item in packet["how_to_use"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Related Nodes", "", "| handle | kind | path | summary |", "| --- | --- | --- | --- |"])
    for node in packet["related_nodes"]:
        lines.append(
            f"| `{node['handle']}` | `{node['kind']}` | `{node.get('path') or ''}` | {node.get('summary') or ''} |"
        )
    lines.extend(["", "## Forward Edges", "", "| kind | target | confidence |", "| --- | --- | --- |"])
    for edge in packet["forward_edges"]:
        lines.append(f"| `{edge['kind']}` | `{edge['target']}` | `{edge['confidence']}` |")
    lines.extend(["", "## Reverse Edges", "", "| kind | source | confidence |", "| --- | --- | --- |"])
    for edge in packet["reverse_edges"]:
        lines.append(f"| `{edge['kind']}` | `{edge['source']}` | `{edge['confidence']}` |")
    return "\n".join(lines) + "\n"


def render_root_codegraph(graph: dict[str, Any]) -> str:
    summary = graph["summary"]
    focus = graph["scan_shortcuts"]["core_model_next_reads"]
    lines = [
        "# CODEGRAPH",
        "",
        "这是本项目的结构化入口。后续进入项目时，先读这里，再按任务跳转；不要先全仓扫描。",
        "",
        "## 当前图谱状态",
        "",
        f"- 文件数：`{summary['file_count']}`",
        f"- 节点数：`{summary['node_count']}`",
        f"- 边数：`{summary['edge_count']}`",
        f"- Agent workflow 数：`{summary['agent_workflow_count']}`",
        "- 说明：已安装 GitHub `lzehrung/codegraph` skill；本机缺少 Node.js 24.10+ / `codegraph` CLI，所以本图谱由 `tools/build_project_codegraph.py` 生成。",
        "",
        "## 最短阅读路径",
        "",
        "1. `notes/current_status.md`：看当前模型状态和最近迭代边界。",
        "2. `deliverables/manifest.json`：看核心产物、指标和输出目录索引。",
        "3. `deliverables/model_core_optimization/model_core_goal.md`：看第一性原理和七层骨架。",
        "4. `deliverables/codegraph/codegraph_summary.md`：看完整 agent/file/edge 索引。",
        "5. `deliverables/codegraph/scan_shortcuts.md`：按当前任务选择最短后续文件。",
        "",
        "## 当前核心模型链路",
        "",
        "```mermaid",
        "graph TD",
        "  A[\"Agent48 稀疏布点/低成本观测矩阵\"] --> B[\"Agent54 软传感矩阵耦合\"]",
        "  B --> C[\"Agent53 最小灰箱物理机制\"]",
        "  C --> D[\"Agent51 催化剂活性代理观测\"]",
        "  D --> E[\"Agent49 多设施协同控制\"]",
        "  E --> F[\"Agent52 replay 离线评估\"]",
        "  F --> G[\"Agent55 工程执行约束\"]",
        "  G --> H[\"Agent56/57 KG 推理与主链回接\"]",
        "  H --> I[\"Agent60 架构复盘与减冗\"]",
        "  I --> J[\"R7/Agent44-45 真实现场包与证据门\"]",
        "```",
        "",
        "## 核心 Agent 快捷入口",
        "",
        "| Agent | 作用 | runner | source | test |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for row in focus:
        lines.append(
            f"| {row['agent_number']} | `{row['slug']}` | `{row['runner']}` | `{row.get('source') or ''}` | `{row.get('test') or ''}` |"
        )
    lines.extend(
        [
            "",
            "## 图谱产物",
            "",
            "- `deliverables/codegraph/project_codegraph.json`：完整机器可读图谱。",
            "- `deliverables/codegraph/project_codegraph_nodes.csv`：节点表。",
        "- `deliverables/codegraph/project_codegraph_edges.csv`：边表。",
        "- `deliverables/codegraph/codegraph_summary.md`：人读摘要。",
        "- `deliverables/codegraph/scan_shortcuts.md`：后续工作最短路径。",
        "- `deliverables/codegraph/task_routes.json`：按任务主题分组的跳转索引。",
        "- `deliverables/codegraph/packets/`：核心 agent 的 packet 式上下文包。",
        "- `deliverables/codegraph/native_vs_fallback_evaluation.md`：原生工具与本地 fallback 的效果比较。",
            "",
            "## 使用规则",
            "",
            "- 结构问题先看图谱，行为问题仍要跑测试或实验脚本。",
            "- 图谱里的引用关系是定位线索，不是运行时事实证明。",
            "- `synthetic/sample/template` 产物只能作为接口验证或仿真基线，不能当现场实证结论。",
            "- 若未来安装 Node.js 24.10+ 和 `@lzehrung/codegraph` CLI，可按 `codegraph.config.json` 重新生成原生 CodeGraph artifact。",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    graph = build_graph()
    write_outputs(graph)
    print(
        json.dumps(
            {
                "status": "project_codegraph_ready",
                "root": str(ROOT),
                "summary": graph["summary"],
                "outputs": [
                    "CODEGRAPH.md",
                    "deliverables/codegraph/project_codegraph.json",
                    "deliverables/codegraph/project_codegraph_nodes.csv",
                    "deliverables/codegraph/project_codegraph_edges.csv",
                    "deliverables/codegraph/codegraph_summary.md",
                    "deliverables/codegraph/scan_shortcuts.md",
                    "deliverables/codegraph/task_routes.json",
                    "deliverables/codegraph/packets/",
                    "deliverables/codegraph/native_vs_fallback_evaluation.md",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
