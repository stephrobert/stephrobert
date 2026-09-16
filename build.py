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
# Not read from the GitHub profile's `company` field. That field went stale and the
# page announced the wrong employer until someone noticed, which is the failure mode
# of every value that lives in one place and is displayed in another. It is also the
# only way to attach the logo and the link.
EMPLOYER = {
    "name": "LINAGORA",
    "url": "https://github.com/linagora",
    "site": "https://linagora.com/",
    # The organisation's own avatar: official, served by GitHub, and it follows if they
    # change it. A logo copied into this repository would not.
    "logo": "https://avatars.githubusercontent.com/u/1230365?s=48&v=4",
}
# Not /feed.xml: that one serves a 129-byte <redirect> stub that feedparser
# silently parses into zero entries.
FEED_URL = "https://blog.stephane-robert.info/rss.xml"
API = "https://api.github.com"
TIMEOUT = 20

# Repositories promoted by hand, in display order. Everything else is derived.
# Private ones are skipped silently by pick(): they show up here the day they
# are made public, and never as a 404 for a visitor in the meantime.
# The projects that get a section of their own, in display order. Everything else
# is derived from the API.
#
# Each one carries its own prose because a GitHub description is written for the
# repo page: it has to be short, it cannot say what problem the thing solves, and
# four of them stacked read as a directory listing rather than as a body of work.
#
# `ci` is the workflow file behind the CI badge, and it differs per repo: a badge
# pointing at a workflow that does not exist renders as "no status" forever, which
# looks exactly like a project nobody tests.
FEATURED = [
    {
        "name": "feint",
        "emoji": "🎭",
        "tagline": "the Scaleway, Outscale and Exoscale APIs, on your laptop",
        "ci": "go.yml",
        "problem": (
            "testing cloud automation needs a real account, real credentials and a real "
            "bill. And a pipeline that needs secrets cannot run on a pull request from a "
            "fork, which is where the contributions come from."
        ),
        "body": (
            "**feint** is a local emulator of three cloud APIs. It is not a mock written "
            "against the documentation: the vendors' **own official CLIs** drive it end to "
            "end, and Terraform and OpenTofu drive two of the three. If `scw`, `osc-cli` or "
            "`exo` cannot tell the difference, neither can your automation."
        ),
        "bullets": [
            "**No account, no credentials, nothing billed.** It runs offline, on a laptop, in CI, on a plane.",
            "**Driven by the real clients.** Conformance is proven by the vendors' CLIs, not by assertions about them.",
            "**Ships where you already are.** A [GitHub Action](https://github.com/stephrobert/setup-feint) and a [Homebrew tap](https://github.com/stephrobert/homebrew-feint) whose formula is derived from each release's signed checksums, never written by hand.",
        ],
        "snippet": (
            "feint up                      # three cloud APIs, locally\n"
            "scw instance server list      # the vendor's own CLI, unmodified\n"
            "terraform apply               # against the emulator, nothing billed"
        ),
        "demo": None,
    },
    {
        "name": "dsoxlab",
        "emoji": "🧪",
        "tagline": "hands-on DevSecOps labs that grade the machine, not your typing",
        "ci": "ci.yml",
        "problem": (
            "most hands-on labs grade you on the commands you typed. Real exams, RHCSA and "
            "LFCS, grade the state of the machine, after a reboot. That gap is exactly where "
            "candidates fail."
        ),
        "body": (
            "**dsoxlab** is a domain-agnostic CLI framework driving training labs that live "
            "in their own repositories. Each catalog declares itself through a root "
            "`meta.yml` and one `lab.yaml` per lab, so adding a domain means writing a file, "
            "not patching the engine."
        ),
        "bullets": [
            "**Validation proves, it does not trust.** Labs are graded on the actual state of the system with `pytest-testinfra`, including persistence after reboot.",
            "**Three runtimes.** A plain shell, an Incus container, or a full KVM/libvirt virtual machine, chosen per lab.",
            "**Progress that sticks.** Scores, hint costs and history persisted in a local SQLite database, XDG-compliant.",
            "**Bilingual by design.** Every user-facing string ships in English and French (`DSOXLAB_LANG=en|fr`).",
        ],
        "snippet": (
            "uv tool install dsoxlab\n"
            "dsoxlab doctor                # diagnoses (and repairs) the local toolchain\n"
            "dsoxlab list-labs             # the catalog is detected from the repo's meta.yml"
        ),
        "demo": "https://raw.githubusercontent.com/stephrobert/dsoxlab/main/docs/demo.gif",
    },
    {
        "name": "pepin",
        "emoji": "🛰️",
        "tagline": "three sovereign clouds, one axis",
        "ci": "ci.yml",
        "problem": (
            "every provider ships its own posture dashboard, so three clouds means three "
            "scores that cannot be compared, and a question nobody can answer: which of them "
            "is actually the worst?"
        ),
        "body": (
            "**pepin** evaluates Outscale, Scaleway and Exoscale against **one** baseline, "
            "anchored on SCSL, SecNumCloud, CIS and ISO. One axis, three clouds, so the "
            "comparison means something."
        ),
        "bullets": [
            "**Before it is provisioned, not after it is billed.** It reads a Terraform plan, so a misconfiguration is caught at review time.",
            "**Sovereign by construction.** No dependency on a US-hosted control plane to tell you how your European cloud is doing.",
            "**One baseline, not a crosswalk.** A control is mapped to the texts it really cites, and never invented to fill a table.",
        ],
        "snippet": (
            "pepin scan --provider outscale        # posture of a live account\n"
            "pepin scan --tf plan.json             # or of a plan, before apply"
        ),
        "demo": None,
    },
    {
        "name": "pavois",
        "emoji": "🛡️",
        "tagline": "Linux compliance that reads the running config, not the files",
        "ci": "go.yml",
        "problem": (
            "`/etc/ssh/sshd_config` can say `PermitRootLogin no` while a drop-in read later "
            "sets it to `yes`. Every file-based scanner reports the host compliant. The "
            "machine accepts root over SSH."
        ),
        "body": (
            "**pavois** asks the service instead of reading its files: `sshd -T`, `sysctl`, "
            "`systemctl show`, `auditctl -l`. The **effective** configuration, which is the "
            "only one an attacker meets. 789 controls across 9 Linux targets, graded A to E "
            "over CIS, ANSSI-BP-028, NIST, PCI-DSS and DISA STIG."
        ),
        "bullets": [
            "**It hardens, and proves it.** `harden apply --reboot` compares the kernel `boot_id` before and after, so a setting that only holds until the next boot cannot pass silently.",
            "**Evidence you can hand to an auditor.** A campaign packages into a tamper-evident bundle you sign under your own identity; pavois never holds a key.",
            "**Proven, not asserted.** Debian 12 and 13 go through the full campaign on fresh VMs, and the run itself is validated: a control that returned a verdict it never measured fails the campaign.",
        ],
        "snippet": (
            "pavois scan local --sudo              # grade this host, A to E\n"
            "pavois harden plan admin@server1      # a reviewable plan, nothing applied\n"
            "pavois bundle before.json after.json  # signable evidence"
        ),
        "demo": None,
    },
]

SECURITY_REPOS = [
    "scankit",
    # "confkit",   # superseded by pavois
    "secure-python-pipeline",
]
TRAINING_REPOS = [
    "linux-dsoxlab-training",
    "kubernetes-dsoxlab-training",
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


def featured(repos: dict[str, Repo]) -> list[dict]:
    """Merge the hand-written pitch with the live repo data, skipping what is not public.

    A project that is still private simply does not appear, and appears the day it is
    published, rather than rendering as a 404 for a visitor in the meantime. The stars and
    the badges come from the API; only the prose is written here.
    """
    out = []
    for entry in FEATURED:
        repo = repos.get(entry["name"])
        if repo is None:
            continue
        out.append({**entry, "repo": repo})
    return out


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
    # A featured project that is still private is skipped silently by featured(), which is
    # what makes it safe to list one before publishing it. But ALL of them missing means the
    # API answered something unexpected, and rendering a page with an empty "What I build"
    # would look like a profile with no work on it.
    if not any(f["name"] in repos for f in FEATURED):
        names = ", ".join(f["name"] for f in FEATURED)
        raise RuntimeError(f"none of the featured repos ({names}) is in the API response")

    for repo in repos.values():
        repo.description = strip_name_prefix(repo.name, repo.description)

    context = {
        "user": user,
        "employer": EMPLOYER,
        "followers": user["followers"],
        "total_stars": sum(r.stars for r in repos.values()),
        "public_repos": len(repos),
        "featured": featured(repos),
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
