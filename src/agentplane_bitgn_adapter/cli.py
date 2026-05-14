from __future__ import annotations

import argparse
import os
import textwrap
from typing import Literal

from .agent import run_agent
from .models import AdapterConfig, TrialResult


def parse_runtime(value: str | None) -> Literal["sandbox", "pcm", "ecom"]:
    if value == "sandbox":
        return "sandbox"
    if value == "ecom":
        return "ecom"
    return "pcm"


def env_config(args: argparse.Namespace) -> AdapterConfig:
    return AdapterConfig(
        host=args.host or os.getenv("BITGN_HOST") or "https://api.bitgn.com",
        benchmark_id=args.benchmark_id
        or os.getenv("BENCHMARK_ID")
        or os.getenv("BENCH_ID")
        or "bitgn/pac1-dev",
        bitgn_api_key=args.api_key or os.getenv("BITGN_API_KEY") or "",
        runtime=parse_runtime(args.runtime or os.getenv("BITGN_RUNTIME")),
        model=args.model or os.getenv("MODEL_ID") or "gpt-5.4",
        run_name=args.run_name or os.getenv("RUN_NAME") or "AgentPlane BitGN Codex",
        max_steps=args.max_steps,
        artifact_dir=args.artifact_dir,
    )


def run_benchmark(config: AdapterConfig, task_filter: list[str]) -> list[TrialResult]:
    from bitgn.harness_connect import HarnessServiceClientSync
    from bitgn.harness_pb2 import (
        EndTrialRequest,
        GetBenchmarkRequest,
        StartPlaygroundRequest,
        StartRunRequest,
        StartTrialRequest,
        StatusRequest,
        SubmitRunRequest,
    )

    client = HarnessServiceClientSync(config.host)
    print("Connecting to BitGN", client.status(StatusRequest()), flush=True)
    benchmark = client.get_benchmark(GetBenchmarkRequest(benchmark_id=config.benchmark_id))
    print(
        textwrap.dedent(
            f"""
            Benchmark: {benchmark.benchmark_id}
            Tasks: {len(benchmark.tasks)}
            Runtime: {config.runtime}
            Model: {config.model}
            """
        ).strip(),
        flush=True,
    )
    results: list[TrialResult] = []
    if config.benchmark_id == "bitgn/sandbox":
        for task in benchmark.tasks:
            if task_filter and task.task_id not in task_filter:
                continue
            trial = client.start_playground(
                StartPlaygroundRequest(
                    benchmark_id=config.benchmark_id,
                    task_id=task.task_id,
                )
            )
            print(f"=== {trial.task_id} ===", flush=True)
            try:
                run_agent(
                    config=config,
                    harness_url=trial.harness_url,
                    instruction=trial.instruction,
                    task_id=trial.task_id,
                    trial_id=trial.trial_id,
                )
            except Exception as exc:
                print(f"{trial.task_id}: agent failed: {type(exc).__name__}: {exc}", flush=True)
            result = client.end_trial(EndTrialRequest(trial_id=trial.trial_id))
            trial_result = TrialResult(
                task_id=trial.task_id,
                trial_id=trial.trial_id,
                score_available=result.score_available,
                score=result.score if result.score_available else None,
                score_detail=list(result.score_detail),
            )
            results.append(trial_result)
            if result.score_available:
                print(f"{trial.task_id}: {result.score:0.2f}", flush=True)
                if result.score_detail:
                    print("\n".join(result.score_detail), flush=True)
            else:
                print(f"{trial.task_id}: score not available", flush=True)
        return results

    run = client.start_run(
        StartRunRequest(
            name=config.run_name,
            benchmark_id=config.benchmark_id,
            api_key=config.bitgn_api_key,
        )
    )
    try:
        for trial_id in run.trial_ids:
            trial = client.start_trial(StartTrialRequest(trial_id=trial_id))
            if task_filter and trial.task_id not in task_filter:
                continue
            print(f"=== {trial.task_id} ===", flush=True)
            try:
                run_agent(
                    config=config,
                    harness_url=trial.harness_url,
                    instruction=trial.instruction,
                    task_id=trial.task_id,
                    trial_id=trial.trial_id,
                )
            except Exception as exc:
                print(f"{trial.task_id}: agent failed: {type(exc).__name__}: {exc}", flush=True)
            result = client.end_trial(EndTrialRequest(trial_id=trial.trial_id))
            trial_result = TrialResult(
                task_id=trial.task_id,
                trial_id=trial.trial_id,
                score_available=result.score_available,
                score=result.score if result.score_available else None,
                score_detail=list(result.score_detail),
            )
            results.append(trial_result)
            if result.score_available:
                print(f"{trial.task_id}: {result.score:0.2f}", flush=True)
                if result.score_detail:
                    print("\n".join(result.score_detail), flush=True)
            else:
                print(f"{trial.task_id}: score not available", flush=True)
    finally:
        client.submit_run(SubmitRunRequest(run_id=run.run_id, force=True))
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AgentPlane-backed Codex on BitGN.")
    parser.add_argument("tasks", nargs="*", help="Optional BitGN task ids to run.")
    parser.add_argument("--host")
    parser.add_argument("--benchmark-id")
    parser.add_argument("--api-key")
    parser.add_argument("--runtime", choices=["sandbox", "pcm", "ecom"])
    parser.add_argument("--model")
    parser.add_argument("--run-name")
    parser.add_argument("--max-steps", type=int, default=30)
    parser.add_argument("--artifact-dir", default=".agentplane-bitgn")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    config = env_config(args)
    from connectrpc.errors import ConnectError

    try:
        run_benchmark(config, args.tasks)
    except ConnectError as exc:
        raise SystemExit(f"{exc.code}: {exc.message}") from exc


if __name__ == "__main__":
    main()
