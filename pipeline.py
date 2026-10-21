import argparse
import json
from pathlib import Path
import re
from urllib.parse import urlparse


def tokens(text):
    return set(re.findall(r"[a-z0-9]+", text.casefold()))


def score(job, profile):
    description = tokens(job.get("title", "") + " " + job.get("description", ""))
    skills = [skill for skill in profile["skills"] if tokens(skill) <= description]
    match = len(skills) / max(len(profile["skills"]), 1)
    location = profile.get("location", "").casefold()
    if location and location not in job.get("location", "").casefold() and "remote" not in job.get("location", "").casefold():
        match *= 0.5
    return round(match, 3), skills


def validate(job):
    for field in ("title", "companyName", "description", "url"):
        if not isinstance(job.get(field), str) or not job[field].strip():
            raise ValueError(f"missing {field}")
    parsed = urlparse(job["url"])
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("invalid posting URL")


def draft(job, profile, matched):
    relevant = [bullet for bullet in profile["experience"] if tokens(bullet) & set().union(*(tokens(s) for s in matched))]
    if not relevant:
        relevant = profile["experience"][:1]
    if not relevant:
        raise ValueError("profile needs at least one verified experience bullet")
    summary = "\n".join("- " + bullet for bullet in relevant[:3])
    email = (
        f"Subject: {job['title']} at {job['companyName']}\n\n"
        f"Hello,\n\nI'm interested in the {job['title']} role. "
        f"My relevant experience includes {relevant[0].rstrip('.').lower()}. "
        f"I would welcome the chance to discuss the role.\n\n"
        f"Posting: {job['url']}\n\nBest,\n{profile['name']}\n"
    )
    return summary, email


def build(jobs, profile):
    records, seen = [], set()
    for job in jobs:
        validate(job)
        if job["url"] in seen: continue
        seen.add(job["url"])
        value, skills = score(job, profile)
        if value < profile.get("minimum_score", 0.25): continue
        summary, email = draft(job, profile, skills)
        records.append({"title": job["title"], "company": job["companyName"], "url": job["url"], "score": value,
                        "matched_skills": skills, "resume_summary": summary, "email_draft": email})
    return sorted(records, key=lambda r: (-r["score"], r["company"]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("jobs", type=Path)
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--out", type=Path, default=Path("output"))
    args = parser.parse_args()
    jobs = json.loads(args.jobs.read_text(encoding="utf-8"))
    profile = json.loads(args.profile.read_text(encoding="utf-8"))
    results = build(jobs, profile)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "review.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    for index, item in enumerate(results, 1):
        (args.out / f"draft-{index:03}.txt").write_text(item["email_draft"] + "\nResume summary:\n" + item["resume_summary"], encoding="utf-8")
    print(f"{len(results)} drafts written to {args.out}")


if __name__ == "__main__": main()

