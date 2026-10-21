# AI Automated Job Application System

An offline-first pipeline that imports JSON job postings, filters them by skills/location, generates a reviewable resume summary from verified experience bullets, and drafts outreach email text. It never submits an application or sends mail. The local pipeline and tests require no account. AI rewriting is not wired up in this edition.

```sh
python pipeline.py examples/jobs.json --profile examples/profile.json --out output
python -m unittest discover -s tests -v
```

The input shape accepts Apify-like objects with `title`, `companyName`, `description`, `url`, and `location`. Output contains one JSON manifest and separate text drafts for review. `n8n/workflow.json` documents the HTTP/JSON handoff to an external automation service; OAuth and Google Docs publication are integration points requiring credentials and have not been run here.

