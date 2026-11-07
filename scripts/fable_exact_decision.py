#!/usr/bin/env python
"""Combine exact FABLE scenarios into a decision frontier.

Every point is a real Pyculator run. The caps and floors are policy inputs, not model truths.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

for _candidate in Path(__file__).resolve().parents:
    if (_candidate / "src" / "fable_pyculator").exists():
        sys.path.insert(0, str(_candidate / "src"))
        break

__all__ = [
    "build_artifact",
    "collect_points",
    "main",
    "pareto_front",
    "select_food_first",
    "select_ghg_first",
]

OBJECTIVES = ("food_total_kcal_feas", "ghg_total_co2e", "land_total_area")
DIRECTIONS = {"food_total_kcal_feas": 1.0, "ghg_total_co2e": -1.0, "land_total_area": -1.0}
DEFAULT_ASPIRATIONS = {"food_total_kcal_feas": 1.0, "ghg_total_co2e": 0.0, "land_total_area": 0.25}
DEFAULT_WEIGHTS = {"food_total_kcal_feas": 1.0, "ghg_total_co2e": 1.0, "land_total_area": 1.0}


def main(argv: list[str] | None = None) -> int:
    """Build a decision frontier from exact scenario artifacts."""

    args = _parser().parse_args(argv)
    points = collect_points(args.input)
    if not points:
        print("no exact points with selections and objectives found", file=sys.stderr)
        return 1
    unique_points = _dedupe_points(points)
    front = pareto_front(unique_points)
    front_unique = _unique_objectives(front)
    ranked = weighted_ranking(unique_points)
    payload = {
        "input": [str(path) for path in args.input],
        "point_count": len(points),
        "unique_point_count": len(unique_points),
        "unique_objective_count": len(_unique_objectives(unique_points)),
        "objectives": list(OBJECTIVES),
        "directions": DIRECTIONS,
        "aspirations": DEFAULT_ASPIRATIONS,
        "weights": DEFAULT_WEIGHTS,
        "food_first_cap_ghg": args.food_ghg_cap,
        "ghg_first_floor_food": args.ghg_food_floor,
        "ranges": _ranges(unique_points),
        "pareto_count": len(front),
        "pareto_unique_count": len(front_unique),
        "pareto": front_unique,
        "food_first": select_food_first(unique_points, args.food_ghg_cap),
        "ghg_first": select_ghg_first(unique_points, args.ghg_food_floor),
        "food_first_views": [
            {"ghg_cap": cap, "point": select_food_first(unique_points, cap)} for cap in args.food_ghg_caps
        ],
        "ghg_first_views": [
            {"food_floor": floor, "point": select_ghg_first(unique_points, floor)} for floor in args.ghg_food_floors
        ],
        "balanced": ranked[0] if ranked else None,
        "weighted_top": ranked[: args.top],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.artifact_output is not None:
        artifact = build_artifact(
            payload=payload,
            unique_points=unique_points,
            front=front,
            front_unique=front_unique,
            ranked=ranked,
            version=args.version,
            title=args.title,
        )
        args.artifact_output.parent.mkdir(parents=True, exist_ok=True)
        args.artifact_output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"artifact: {args.artifact_output}")
    print(f"decision: {args.output}")
    print(
        f"points: {len(points)} input, {len(unique_points)} unique; "
        f"pareto: {len(front)} rows / {len(front_unique)} unique objectives"
    )
    for label in ("food_first", "ghg_first", "balanced"):
        point = payload[label]
        if point is None:
            print(f"{label}: none")
            continue
        objectives = point["objectives"]
        print(f"{label}: {objectives['food_total_kcal_feas']:.2f} kcal, {objectives['ghg_total_co2e']:.2f} MtCO2e")
    return 0


def build_artifact(
    *,
    payload: dict[str, Any],
    unique_points: list[dict[str, Any]],
    front: list[dict[str, Any]],
    front_unique: list[dict[str, Any]],
    ranked: list[dict[str, Any]],
    version: str,
    title: str,
) -> dict[str, Any]:
    """Build a compact browser-ready artifact from one decision payload."""

    ordered = sorted(
        unique_points,
        key=lambda point: (-_value(point, "food_total_kcal_feas"), _value(point, "ghg_total_co2e")),
    )
    front_keys = {_selection_key(point) for point in front}
    goal_by_key = {_selection_key(row): row["goal"] for row in ranked}
    points: list[dict[str, Any]] = []
    ids_by_key: dict[str, str] = {}
    for index, point in enumerate(ordered):
        point_id = f"p{index:03d}"
        key = _selection_key(point)
        ids_by_key[key] = point_id
        warnings = _warning_ids(point)
        points.append(
            {
                "id": point_id,
                "objectives": {name: _value(point, name) for name in OBJECTIVES},
                "goal": goal_by_key.get(key),
                "front": key in front_keys,
                "origin": _origin(point.get("source")),
                "selections": point["selections"],
                "warnings": warnings,
            }
        )
    dimensions = [
        {"key": "food_total_kcal_feas", "label": "Food", "unit": "kcal", "direction": "max"},
        {"key": "ghg_total_co2e", "label": "GHG", "unit": "MtCO2e", "direction": "min"},
        {"key": "land_total_area", "label": "Land", "unit": "ha", "direction": "min"},
        {"key": "goal", "label": "Goal score", "unit": "", "direction": "min"},
    ]
    ranges = {name: list(bounds) for name, bounds in payload["ranges"].items()}
    goals = [row["goal"] for row in ranked]
    ranges["goal"] = [min(goals), max(goals)] if goals else [0.0, 0.0]
    views = {
        "balanced": _view_entry(payload.get("balanced"), ids_by_key, "Balanced", "weighted goal"),
        "food_first": _view_entry(
            payload.get("food_first"), ids_by_key, "Food-first", f"GHG ≤ {payload['food_first_cap_ghg']:g}"
        ),
        "ghg_first": _view_entry(
            payload.get("ghg_first"), ids_by_key, "GHG-first", f"food ≥ {payload['ghg_first_floor_food']:g}"
        ),
        "food_first_views": [
            _view_entry(row.get("point"), ids_by_key, "Food-first", f"GHG ≤ {row['ghg_cap']:g}")
            for row in payload.get("food_first_views", [])
        ],
        "ghg_first_views": [
            _view_entry(row.get("point"), ids_by_key, "GHG-first", f"food ≥ {row['food_floor']:g}")
            for row in payload.get("ghg_first_views", [])
        ],
    }
    control_names = sorted({name for point in ordered for name in point.get("selections", {})})
    return {
        "artifact_version": 1,
        "version": version,
        "title": title,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "boundary": (
            "Exact Pyculator points from the local Phases 37-40 scenario set. "
            "The frontier is local, not global; caps and floors are policy inputs."
        ),
        "provenance": {
            "point_count": payload["point_count"],
            "unique_point_count": payload["unique_point_count"],
            "pareto_count": payload["pareto_count"],
            "pareto_unique_count": payload["pareto_unique_count"],
            "input": payload["input"],
            "aspirations": payload["aspirations"],
            "weights": payload["weights"],
        },
        "dimensions": dimensions,
        "ranges": ranges,
        "controls": control_names,
        "points": points,
        "pareto_ids": [ids_by_key[_selection_key(point)] for point in front_unique],
        "views": views,
    }


def _selection_key(point: dict[str, Any]) -> str:
    return json.dumps(point["selections"], sort_keys=True)


def _warning_ids(point: dict[str, Any]) -> list[str]:
    evaluation = point.get("rule_evaluation")
    if not isinstance(evaluation, dict):
        return []
    found: list[str] = []
    for key in ("errors", "warnings", "exploratory"):
        for hit in evaluation.get(key) or []:
            if isinstance(hit, dict) and hit.get("rule_id"):
                found.append(str(hit["rule_id"]))
    return sorted(set(found))


def _origin(source: Any) -> str:
    text = str(source or "")
    if "fable-exact-optimization" in text:
        return "Phase 37"
    if "fable-exact-sensitivity" in text:
        return "Phase 38"
    if "fable-exact-neighborhood" in text:
        return "Phase 39"
    if "fable-exact-decision" in text:
        return "Phase 40"
    return "Other"


def _view_entry(
    point: dict[str, Any] | None,
    ids_by_key: dict[str, str],
    label: str,
    constraint: str,
) -> dict[str, Any] | None:
    if not point:
        return None
    key = _selection_key(point)
    return {
        "label": label,
        "constraint": constraint,
        "point_id": ids_by_key.get(key),
        "objectives": point.get("objectives"),
        "selections": point.get("selections"),
    }


def collect_points(paths: list[Path]) -> list[dict[str, Any]]:
    """Collect exact point dictionaries from files and directories."""

    points: list[dict[str, Any]] = []
    for path in paths:
        candidates = sorted(path.rglob("*.json")) if path.is_dir() else [path]
        for candidate in candidates:
            if not candidate.is_file():
                continue
            try:
                payload = json.loads(candidate.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            points.extend(_extract_points(payload, candidate))
    return points


def _extract_points(payload: Any, source: Path) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        found: list[dict[str, Any]] = []
        for item in payload:
            found.extend(_extract_points(item, source))
        return found
    if not isinstance(payload, dict):
        return []
    if _is_point(payload):
        point = dict(payload)
        point.setdefault("source", str(source))
        return [point]
    found = []
    for key in ("samples", "variants", "points", "candidates"):
        value = payload.get(key)
        if isinstance(value, list):
            found.extend(_extract_points(value, source))
    baseline = payload.get("baseline")
    if isinstance(baseline, dict):
        found.extend(_extract_points(baseline, source))
    return found


def _is_point(payload: dict[str, Any]) -> bool:
    if "error" in payload:
        return False
    objectives = payload.get("objectives")
    selections = payload.get("selections")
    if not isinstance(objectives, dict) or not isinstance(selections, dict):
        return False
    return all(
        isinstance(objectives.get(name), (int, float)) and not isinstance(objectives.get(name), bool)
        for name in OBJECTIVES
    )


def _dedupe_points(points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for point in points:
        key = json.dumps(point["selections"], sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        unique.append(point)
    return unique


def _unique_objectives(points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[float, ...]] = set()
    unique: list[dict[str, Any]] = []
    for point in points:
        key = tuple(round(_value(point, name), 6) for name in OBJECTIVES)
        if key in seen:
            continue
        seen.add(key)
        unique.append(point)
    return unique


def _value(point: dict[str, Any], name: str) -> float:
    return float(point["objectives"][name])


def _ranges(points: list[dict[str, Any]]) -> dict[str, tuple[float, float]]:
    return {
        name: (min(_value(point, name) for point in points), max(_value(point, name) for point in points))
        for name in OBJECTIVES
    }


def _is_constant(values: list[float]) -> bool:
    low, high = min(values), max(values)
    return high - low <= 1e-6 * max(1.0, abs(low), abs(high))


def pareto_front(points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return non-dominated points for food(max), GHG(min), land(min)."""

    active = [name for name in OBJECTIVES if not _is_constant([_value(point, name) for point in points])]
    front: list[dict[str, Any]] = []
    for candidate in points:
        if not any(_dominates(other, candidate, active) for other in points if other is not candidate):
            front.append(candidate)
    return sorted(
        front,
        key=lambda point: (-_value(point, "food_total_kcal_feas"), _value(point, "ghg_total_co2e")),
    )


def _dominates(left: dict[str, Any], right: dict[str, Any], objectives: list[str]) -> bool:
    left_values = [_value(left, name) * DIRECTIONS[name] for name in objectives]
    right_values = [_value(right, name) * DIRECTIONS[name] for name in objectives]
    return all(a >= b for a, b in zip(left_values, right_values, strict=True)) and any(
        a > b for a, b in zip(left_values, right_values, strict=True)
    )


def select_food_first(points: list[dict[str, Any]], ghg_cap: float) -> dict[str, Any] | None:
    """Return the highest-food point under a GHG cap."""

    eligible = [point for point in points if _value(point, "ghg_total_co2e") <= ghg_cap]
    return max(eligible, key=lambda point: _value(point, "food_total_kcal_feas"), default=None)


def select_ghg_first(points: list[dict[str, Any]], food_floor: float) -> dict[str, Any] | None:
    """Return the lowest-GHG point above a food floor."""

    eligible = [point for point in points if _value(point, "food_total_kcal_feas") >= food_floor]
    return min(eligible, key=lambda point: _value(point, "ghg_total_co2e"), default=None)


def weighted_ranking(
    points: list[dict[str, Any]],
    *,
    aspirations: dict[str, float] | None = None,
    weights: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    """Rank points by weighted squared distance to normalized aspirations."""

    aspirations = aspirations or DEFAULT_ASPIRATIONS
    weights = weights or DEFAULT_WEIGHTS
    ranges = _ranges(points)
    ranked: list[dict[str, Any]] = []
    for point in points:
        components: dict[str, float] = {}
        for name in OBJECTIVES:
            low, high = ranges[name]
            values = [_value(item, name) for item in points]
            normalized = 0.5 if _is_constant(values) else (_value(point, name) - low) / (high - low)
            components[name] = weights[name] * (normalized - aspirations[name]) ** 2
        goal = sum(components.values()) / sum(weights.values())
        ranked.append(
            {
                "selections": point["selections"],
                "objectives": point["objectives"],
                "source": point.get("source"),
                "goal": goal,
                "components": components,
            }
        )
    return sorted(ranked, key=lambda row: (row["goal"], json.dumps(row["selections"], sort_keys=True)))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", nargs="+", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--food-ghg-cap", type=float, default=110.0)
    parser.add_argument("--ghg-food-floor", type=float, default=3000.0)
    parser.add_argument("--version", default="2024", help="Workbook version label for the artifact.")
    parser.add_argument("--title", default="FABLE 2024 exact decision frontier")
    parser.add_argument("--artifact-output", type=Path, default=None)
    parser.add_argument(
        "--food-ghg-caps",
        nargs="+",
        type=float,
        default=[80.0, 90.0, 100.0, 110.0, 120.0, 150.0],
    )
    parser.add_argument(
        "--ghg-food-floors",
        nargs="+",
        type=float,
        default=[2000.0, 2200.0, 2400.0, 2800.0, 3000.0, 3200.0],
    )
    parser.add_argument("--top", type=int, default=20)
    return parser


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
