"""Build normalized evidence report for deploy workflow runs."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build deploy run evidence report from GitHub Actions API")
    parser.add_argument("--owner", default="", help="GitHub owner (defaults to GITHUB_OWNER env)")
    parser.add_argument("--repo", default="", help="GitHub repo (defaults to GITHUB_REPO env)")
    parser.add_argument(
        "--workflow-file",
        default="deploy_yc_function_main.yml",
        help="Workflow file name (default: deploy_yc_function_main.yml)",
    )
    parser.add_argument("--run-id", type=int, default=0, help="Optional specific workflow run id")
    parser.add_argument("--per-page", type=int, default=5, help="Number of latest runs to fetch")
    parser.add_argument(
        "--output-file",
        default="",
        help="Optional output JSON file path. If omitted, prints report JSON to stdout.",
    )
    return parser.parse_args()


def _headers_from_env() -> dict[str, str]:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _get_json(url: str, headers: dict[str, str]) -> dict:
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def _normalize_run(run: dict) -> dict:
    return {
        "run_id": run.get("id"),
        "workflow_name": run.get("name"),
        "status": run.get("status"),
        "conclusion": run.get("conclusion"),
        "head_branch": run.get("head_branch"),
        "head_sha": run.get("head_sha"),
        "created_at": run.get("created_at"),
        "updated_at": run.get("updated_at"),
        "html_url": run.get("html_url"),
    }


def _normalize_jobs(jobs_payload: dict) -> list[dict]:
    normalized = []
    for job in jobs_payload.get("jobs", []):
        steps = []
        for step in job.get("steps", []):
            steps.append(
                {
                    "name": step.get("name"),
                    "status": step.get("status"),
                    "conclusion": step.get("conclusion"),
                    "number": step.get("number"),
                }
            )
        normalized.append(
            {
                "job_id": job.get("id"),
                "name": job.get("name"),
                "status": job.get("status"),
                "conclusion": job.get("conclusion"),
                "started_at": job.get("started_at"),
                "completed_at": job.get("completed_at"),
                "html_url": job.get("html_url"),
                "steps": steps,
            }
        )
    return normalized


def main() -> int:
    load_dotenv(".env")
    args = parse_args()
    owner = args.owner or os.environ.get("GITHUB_OWNER", "").strip()
    repo = args.repo or os.environ.get("GITHUB_REPO", "").strip()
    if not owner or not repo:
        raise SystemExit("owner/repo is required (set GITHUB_OWNER/GITHUB_REPO or pass --owner/--repo)")

    headers = _headers_from_env()
    base = f"https://api.github.com/repos/{owner}/{repo}"
    if args.run_id:
        run_payload = _get_json(f"{base}/actions/runs/{args.run_id}", headers=headers)
        runs = [run_payload]
    else:
        runs_payload = _get_json(
            f"{base}/actions/workflows/{args.workflow_file}/runs?per_page={args.per_page}",
            headers=headers,
        )
        runs = runs_payload.get("workflow_runs", [])

    report_runs = []
    for run in runs:
        run_id = run.get("id")
        jobs_payload = _get_json(f"{base}/actions/runs/{run_id}/jobs", headers=headers)
        report_runs.append(
            {
                "run": _normalize_run(run),
                "jobs": _normalize_jobs(jobs_payload),
            }
        )

    report = {
        "artifact": "deploy_run_evidence_report",
        "owner": owner,
        "repo": repo,
        "workflow_file": args.workflow_file,
        "runs": report_runs,
    }

    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output_file:
        out_file = Path(args.output_file)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(payload, encoding="utf-8")
        print(f"deploy_run_evidence_file={out_file}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
