#!/usr/bin/env python3
"""
Minimal Clinejection scanner: scan GitHub issue titles for static observed payloads of indirect prompt
injection payloads (exact phrases + keyword combinations).
Input: GITHUB_TOKEN or GH_TOKEN, repos list (repos.txt or --repos).
"""

import argparse
import os
import sys
from pathlib import Path

import yaml
from github import Github


def load_payloads(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Payloads file not found: {path}")
    with open(p, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def normalize(text: str) -> str:
    return (text or "").lower()


def matches_exact(title_norm: str, exact_phrases: list[str]) -> list[str]:
    found = []
    for phrase in exact_phrases or []:
        if phrase.lower() in title_norm:
            found.append(phrase)
    return found


def matches_keywords(title_norm: str, keyword_rules: list[dict]) -> list[tuple[str, int]]:
    results = []
    for rule in keyword_rules or []:
        name = rule.get("name", "")
        keywords = [k.lower() for k in rule.get("keywords", [])]
        min_matches = rule.get("min_matches", 1)
        count = sum(1 for k in keywords if k in title_norm)
        if count >= min_matches:
            results.append((name, count))
    return results


def get_repos(repos_path: str) -> list[str]:
    p = Path(repos_path)
    if not p.exists():
        return []
    lines = p.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan GitHub issue titles for Clinejection payloads.")
    parser.add_argument("--repos", default="repos.txt", help="Path to file with owner/repo per line")
    parser.add_argument("--payloads", default="payloads.yaml", help="Path to payloads YAML")
    parser.add_argument("--state", default="open", choices=["open", "closed", "all"], help="Issue state to fetch")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print("Set GITHUB_TOKEN or GH_TOKEN.", file=sys.stderr)
        sys.exit(1)

    payloads = load_payloads(args.payloads)
    exact_phrases = payloads.get("exact_phrases", [])
    keyword_rules = payloads.get("keyword_rules", [])

    repos = get_repos(args.repos)
    if not repos:
        print("No repos found in", args.repos, file=sys.stderr)
        sys.exit(1)

    gh = Github(token)
    found_any = False

    for repo_spec in repos:
        try:
            repo = gh.get_repo(repo_spec)
        except Exception as e:
            print(f"# Skip {repo_spec}: {e}", file=sys.stderr)
            continue

        state = None if args.state == "all" else args.state
        for issue in repo.get_issues(state=state):
            if issue.pull_request:
                continue
            title = issue.title or ""
            title_norm = normalize(title)
            exact_hits = matches_exact(title_norm, exact_phrases)
            keyword_hits = matches_keywords(title_norm, keyword_rules)
            if exact_hits or keyword_hits:
                found_any = True
                print(f"{repo_spec}#{issue.number}\t{title}")
                if exact_hits:
                    print(f"  exact: {exact_hits}")
                if keyword_hits:
                    print(f"  keywords: {keyword_hits}")

    if not found_any:
        print("No suspicious issues found.")


if __name__ == "__main__":
    main()
