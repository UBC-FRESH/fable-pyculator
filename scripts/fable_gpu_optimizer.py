#!/usr/bin/env python
"""Train a Torch surrogate and run a GPU population search over FABLE selections."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path
from typing import Any

try:
    import numpy as np
    import torch
    from torch import nn
except ModuleNotFoundError as error:  # pragma: no cover - CLI boundary
    raise SystemExit(
        "fable_gpu_optimizer requires torch and numpy; run it with a GPU-capable Python environment"
    ) from error

__all__ = ["main"]


def main(argv: list[str] | None = None) -> int:
    """Train the pilot surrogate and run the GA."""

    args = _parser().parse_args(argv)
    dataset = json.loads(args.dataset.read_text(encoding="utf-8"))
    controls = dataset["controls"]
    samples = [sample for sample in dataset["samples"] if "error" not in sample]
    if len(samples) < 4:
        raise SystemExit("need at least four exact samples to train the pilot surrogate")
    objective_names = tuple(samples[0]["objectives"])
    objectives = _parse_objectives(args.objective, objective_names)
    variable_names = dataset.get("variable_controls")
    if variable_names:
        controls = [control for control in controls if control["name"] in set(variable_names)]
    baseline_selections = dataset.get("baseline_selections") or {
        control["name"]: control["default"] for control in controls
    }
    X, Y, baseline = _encode(dataset, samples, controls, objectives, baseline_selections)
    device = args.device if args.device != "auto" else ("cuda" if torch.cuda.is_available() else "cpu")
    result = _run(
        controls=controls,
        objectives=objectives,
        X=X,
        Y=Y,
        baseline=baseline,
        baseline_selections=baseline_selections,
        population=args.population,
        generations=args.generations,
        epochs=args.epochs,
        top_k=args.top_k,
        seed=args.seed,
        device=device,
        ensemble_size=args.ensemble_size,
        uncertainty_penalty=args.uncertainty_penalty,
    )
    result.update(
        {
            "dataset": str(args.dataset),
            "version": dataset.get("version"),
            "sample_count": len(samples),
            "controls": controls,
        }
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("device", "metrics", "top_candidates")}, indent=2)[:4000])
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True, help="Exact sample dataset JSON.")
    parser.add_argument("--output", type=Path, required=True, help="Output candidate JSON.")
    parser.add_argument("--population", type=int, default=256)
    parser.add_argument("--generations", type=int, default=200)
    parser.add_argument("--epochs", type=int, default=800)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--ensemble-size", type=int, default=5)
    parser.add_argument("--uncertainty-penalty", type=float, default=0.5)
    parser.add_argument("--device", default="auto", help="auto, cuda, cuda:0, or cpu")
    parser.add_argument(
        "--objective",
        action="append",
        default=None,
        help=(
            "Objective spec name:direction:weight. direction is max, min, or target. "
            "Defaults to food max, GHG min, land target."
        ),
    )
    return parser


def _parse_objectives(specs: list[str] | None, names: tuple[str, ...]) -> list[dict[str, Any]]:
    if specs:
        entries = []
        for spec in specs:
            name, direction, weight = spec.split(":", 2)
            if name not in names:
                raise SystemExit(f"unknown objective {name!r}; available: {', '.join(names)}")
            if direction not in {"max", "min", "target"}:
                raise SystemExit(f"invalid direction {direction!r}")
            entries.append({"name": name, "direction": direction, "weight": float(weight)})
        return entries
    defaults = [
        {"name": "food_total_kcal_feas", "direction": "max", "weight": 1.0},
        {"name": "ghg_total_co2e", "direction": "min", "weight": 1.0},
        {"name": "land_total_area", "direction": "target", "weight": 0.1},
    ]
    return [entry for entry in defaults if entry["name"] in names]


def _encode(
    dataset: dict[str, Any],
    samples: list[dict[str, Any]],
    controls: list[dict[str, Any]],
    objectives: list[dict[str, Any]],
    baseline_selections: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray, list[int]]:
    index = {
        control["name"]: {str(option): position for position, option in enumerate(control["options"])}
        for control in controls
    }
    X = np.zeros((len(samples), len(controls)), dtype=np.int64)
    for row, sample in enumerate(samples):
        selections = sample["selections"]
        for column, control in enumerate(controls):
            value = str(selections.get(control["name"], control["default"]))
            if value not in index[control["name"]]:
                raise SystemExit(f"sample uses unknown option {value!r} for {control['name']!r}")
            X[row, column] = index[control["name"]][value]
    Y = np.array(
        [[float(sample["objectives"][objective["name"]]) for objective in objectives] for sample in samples],
        dtype=np.float64,
    )
    baseline = [
        index[control["name"]][str(baseline_selections.get(control["name"], control["default"]))]
        for control in controls
    ]
    return X, Y, baseline


def _run(
    *,
    controls: list[dict[str, Any]],
    objectives: list[dict[str, Any]],
    X: np.ndarray,
    Y: np.ndarray,
    baseline: list[int],
    baseline_selections: dict[str, Any],
    population: int,
    generations: int,
    epochs: int,
    top_k: int,
    seed: int,
    device: str,
    ensemble_size: int,
    uncertainty_penalty: float,
) -> dict[str, Any]:
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    option_counts = [len(control["options"]) for control in controls]
    offsets = np.cumsum([0, *option_counts[:-1]]).tolist()
    one_hot_size = int(sum(option_counts))
    y_min = Y.min(axis=0)
    y_span = Y.max(axis=0) - y_min
    y_span[y_span == 0] = 1.0
    Y_norm = (Y - y_min) / y_span
    baseline_row = int(np.where((X == np.asarray(baseline)).all(axis=1))[0][0])
    aspirations = np.array(
        [
            Y_norm[:, index].max()
            if objective["direction"] == "max"
            else Y_norm[:, index].min()
            if objective["direction"] == "min"
            else Y_norm[baseline_row, index]
            for index, objective in enumerate(objectives)
        ]
    )
    weights = np.array([objective["weight"] for objective in objectives], dtype=np.float64)

    x_tensor = torch.as_tensor(X, dtype=torch.long, device=device)
    y_tensor = torch.as_tensor(Y_norm, dtype=torch.float32, device=device)
    order = torch.randperm(len(X), device=device)
    split = max(1, int(len(X) * 0.8))
    train_idx = order[:split]
    val_idx = order[split:] if split < len(X) else order[:split]

    def encode_batch(batch: torch.Tensor) -> torch.Tensor:
        one_hot = torch.zeros((batch.shape[0], one_hot_size), dtype=torch.float32, device=device)
        rows = torch.arange(batch.shape[0], device=device)
        for column, (offset, count) in enumerate(zip(offsets, option_counts)):
            one_hot[rows, offset + batch[:, column]] = 1.0
        return one_hot

    models: list[nn.Module] = []
    for member in range(max(1, ensemble_size)):
        torch.manual_seed(seed + member)
        model = nn.Sequential(
            nn.Linear(one_hot_size, 128),
            nn.SiLU(),
            nn.Linear(128, 128),
            nn.SiLU(),
            nn.Linear(128, len(objectives)),
        ).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        for _ in range(epochs):
            optimizer.zero_grad()
            prediction = model(encode_batch(x_tensor))
            loss = torch.mean((prediction - y_tensor) ** 2)
            loss.backward()
            optimizer.step()
        model.eval()
        models.append(model)

    def predict_batch(batch: torch.Tensor) -> tuple[np.ndarray, np.ndarray]:
        with torch.no_grad():
            predictions = np.stack([model(encode_batch(batch)).cpu().numpy() for model in models])
        return predictions.mean(axis=0), predictions.std(axis=0)

    predicted, predicted_std = predict_batch(x_tensor)
    metrics = {
        "train_mse": float(np.mean((predicted[train_idx.cpu().numpy()] - Y_norm[train_idx.cpu().numpy()]) ** 2)),
        "validation_mse": float(np.mean((predicted[val_idx.cpu().numpy()] - Y_norm[val_idx.cpu().numpy()]) ** 2)),
        "rank_correlation": _mean_rank_correlation(predicted, Y_norm),
        "ensemble_size": len(models),
        "mean_ensemble_std": float(np.mean(predicted_std)),
        "objective_names": [objective["name"] for objective in objectives],
        "aspirations_normalized": aspirations.tolist(),
    }

    rng = torch.Generator(device=device)
    rng.manual_seed(seed)
    counts = torch.tensor(option_counts, dtype=torch.long, device=device)
    population_tensor = torch.stack(
        [torch.randint(0, int(count), (population,), generator=rng, device=device) for count in counts],
        dim=1,
    )
    population_tensor[0] = torch.tensor(baseline, dtype=torch.long, device=device)
    elite_count = max(2, int(population * 0.1))
    best_history: list[float] = []
    best_genome = population_tensor[0].clone()
    best_loss = math.inf

    def loss_for(batch: torch.Tensor) -> torch.Tensor:
        normalized, spread = predict_batch(batch)
        deviations = []
        for index, objective in enumerate(objectives):
            if objective["direction"] == "max":
                deviation = np.maximum(0.0, aspirations[index] - normalized[:, index])
                tie_break = 1.0 - normalized[:, index]
            elif objective["direction"] == "min":
                deviation = np.maximum(0.0, normalized[:, index] - aspirations[index])
                tie_break = normalized[:, index]
            else:
                deviation = np.abs(normalized[:, index] - aspirations[index])
                tie_break = deviation
            deviations.append(deviation + 0.001 * tie_break)
        scalar = np.sum(np.stack(deviations, axis=1) * weights, axis=1)
        scalar = scalar + uncertainty_penalty * np.sum(spread * weights, axis=1)
        return torch.as_tensor(scalar, dtype=torch.float32, device=device)

    for generation in range(generations):
        losses = loss_for(population_tensor)
        generation_best = int(torch.argmin(losses).item())
        if float(losses[generation_best].item()) < best_loss:
            best_loss = float(losses[generation_best].item())
            best_genome = population_tensor[generation_best].clone()
        best_history.append(best_loss)
        elite_indices = torch.argsort(losses)[:elite_count]
        elites = population_tensor[elite_indices]
        tournament = torch.randint(0, population, (population, 3), generator=rng, device=device)
        winners = tournament[torch.arange(population, device=device), torch.argmin(losses[tournament], dim=1)]
        winner_genomes = population_tensor[winners]
        left = winner_genomes[torch.randint(0, population, (population,), generator=rng, device=device)]
        right = winner_genomes[torch.randint(0, population, (population,), generator=rng, device=device)]
        mask = torch.rand((population, len(controls)), generator=rng, device=device) < 0.5
        children = torch.where(mask, left, right)
        mutation_mask = torch.rand((population, len(controls)), generator=rng, device=device) < 0.05
        for column, count in enumerate(option_counts):
            replacements = torch.randint(0, int(count), (population,), generator=rng, device=device)
            children[:, column] = torch.where(mutation_mask[:, column], replacements, children[:, column])
        population_tensor = torch.cat([elites, children], dim=0)[:population]

    final_losses = loss_for(population_tensor)
    order = torch.argsort(final_losses)
    top: list[dict[str, Any]] = []
    seen: set[tuple[int, ...]] = set()
    predictions, prediction_std = predict_batch(population_tensor)

    def normalized_to_raw(values: np.ndarray) -> list[float]:
        return (values * y_span + y_min).tolist()

    for index in order.tolist():
        genome = tuple(int(value) for value in population_tensor[index].tolist())
        if genome in seen:
            continue
        seen.add(genome)
        selections = dict(baseline_selections)
        selections.update({control["name"]: control["options"][option] for control, option in zip(controls, genome)})
        raw = normalized_to_raw(predictions[index])
        raw_std = (prediction_std[index] * y_span).tolist()
        top.append(
            {
                "selection_indices": list(genome),
                "selections": selections,
                "surrogate_goal": float(final_losses[index].item()),
                "surrogate_objectives": {objective["name"]: value for objective, value in zip(objectives, raw)},
                "surrogate_std": {objective["name"]: value for objective, value in zip(objectives, raw_std)},
            }
        )
        if len(top) >= top_k:
            break
    return {
        "device": device,
        "metrics": metrics,
        "best_loss": best_loss,
        "best_genome": best_genome.tolist(),
        "best_history": best_history,
        "top_candidates": top,
    }


def _mean_rank_correlation(predicted: np.ndarray, actual: np.ndarray) -> float:
    values = []
    for column in range(actual.shape[1]):
        if np.std(predicted[:, column]) == 0 or np.std(actual[:, column]) == 0:
            continue
        values.append(float(np.corrcoef(_rank(predicted[:, column]), _rank(actual[:, column]))[0, 1]))
    return float(np.mean(values)) if values else 0.0


def _rank(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values)
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(len(values), dtype=np.float64)
    return ranks


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
