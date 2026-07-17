#!/usr/bin/env python3
"""Render README.md from README-TEMPLATE.j2.

Every dynamic value comes from a first-party source (GitHub REST API, the blog
RSS feed). No third-party README widget service is involved: the profile must
not break the day someone else's free Vercel deployment goes down.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

import feedparser
import requests
from jinja2 import Environment, FileSystemLoader, StrictUndefined

USER = "stephrobert"
# Not /feed.xml: that one serves a 129-byte <redirect> stub that feedparser
# silently parses into zero entries.
FEED_URL = "https://blog.stephane-robert.info/rss.xml"
API = "https://api.github.com"
TIMEOUT = 20

# Repositories promoted by hand, in display order. Everything else is derived.
# Private ones are skipped silently by pick(): they show up here the day they
# are made public, and never as a 404 for a visitor in the meantime.
FLAGSHIP = "dsoxlab"
# Kept out of the GitHub description, which is written for the repo page and is
# too long for a heading.
FLAGSHIP_TAGLINE = "a CLI framework for hands-on DevSecOps labs"
SECURITY_REPOS = [
    "pavois",
    # "confkit",   # superseded by pavois
    # "scankit",   # still private, to be published later
    "secure-python-pipeline",
]
TRAINING_REPOS = [
    "linux-dsoxlab-training",
    "containers-training",
    "ansible-training",
    "python-training",
    "github-actions-training",
]


@dataclass
class Repo:
    name: str
    description: str
    stars: int
    language: str
    url: str
    topics: list[str] = field(default_factory=list)


def session() -> requests.Session:
    s = requests.Session()
    s.headers["Accept"] = "application/vnd.github+json"
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        s.headers["Authorization"] = f"Bearer {token}"
    return s


def fetch_repos(s: requests.Session) -> dict[str, Repo]:
    repos: dict[str, Repo] = {}
    page = 1
    while True:
        r = s.get(
            f"{API}/users/{USER}/repos",
            params={"per_page": 100, "page": page, "type": "owner", "sort": "pushed"},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        for item in batch:
            if item.get("fork"):
                continue
            repos[item["name"]] = Repo(
                name=item["name"],
                description=(item.get("description") or "").strip(),
                stars=item.get("stargazers_count", 0),
                language=item.get("language") or "",
                url=item["html_url"],
                topics=item.get("topics") or [],
            )
        page += 1
    return repos


def pick(repos: dict[str, Repo], names: list[str]) -> list[Repo]:
    """Keep the requested repos, in order, skipping the private/missing ones."""
    return [repos[n] for n in names if n in repos]


def strip_name_prefix(name: str, description: str) -> str:
    """Drop a leading "name — " from a description: the name is already the link."""
    for sep in (" — ", " - ", ": "):
        prefix = f"{name}{sep}"
        if description.lower().startswith(prefix.lower()):
            rest = description[len(prefix) :]
            return rest[:1].upper() + rest[1:]
    return description


def latest_posts(limit: int = 5) -> list[dict[str, str]]:
    feed = feedparser.parse(FEED_URL)
    if feed.bozo and not feed.entries:
        raise RuntimeError(f"unusable feed {FEED_URL}: {feed.bozo_exception}")
    # An empty feed means the URL moved, not that I stopped writing. Fail loudly
    # rather than render a blog section with no blog in it.
    if not feed.entries:
        raise RuntimeError(f"no entries in {FEED_URL} (HTTP {feed.get('status')})")
    entries = sorted(
        feed.entries,
        key=lambda e: e.get("published_parsed") or e.get("updated_parsed"),
        reverse=True,
    )
    return [
        {"title": e.title.strip(), "link": e.link, "date": _fmt(e)}
        for e in entries[:limit]
    ]


def _fmt(entry) -> str:
    t = entry.get("published_parsed") or entry.get("updated_parsed")
    return f"{t.tm_year}-{t.tm_mon:02d}-{t.tm_mday:02d}" if t else ""


def main() -> int:
    s = session()

    user = s.get(f"{API}/users/{USER}", timeout=TIMEOUT)
    user.raise_for_status()
    user = user.json()

    repos = fetch_repos(s)
    if FLAGSHIP not in repos:
        raise RuntimeError(f"flagship repo {FLAGSHIP!r} not found in the API response")

    for repo in repos.values():
        repo.description = strip_name_prefix(repo.name, repo.description)

    context = {
        "user": user,
        "followers": user["followers"],
        "total_stars": sum(r.stars for r in repos.values()),
        "public_repos": len(repos),
        "flagship": repos[FLAGSHIP],
        "flagship_tagline": FLAGSHIP_TAGLINE,
        "security_repos": pick(repos, SECURITY_REPOS),
        "training_repos": pick(repos, TRAINING_REPOS),
        "posts": latest_posts(),
    }

    env = Environment(
        loader=FileSystemLoader("."),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        autoescape=False,
    )
    rendered = env.get_template("README-TEMPLATE.j2").render(**context)

    with open("README.md", "w", encoding="utf-8") as fh:
        fh.write(rendered)

    print(
        f"README.md rendered: {context['public_repos']} repos, "
        f"{context['total_stars']} stars, {len(context['posts'])} posts"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
