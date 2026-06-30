# GitHub Copilot QAT Labs

Training labs for QA automation with GitHub Copilot. Labs are published at:

**https://nephoseu.github.io/ghcp-qat-resources/**

---

## Repository structure

```
ghcp-qat-resources/
├── docs/                   # Lab content served as GitHub Pages (MkDocs)
│   ├── index.md
│   ├── lab1.md – lab5.md
│   └── downloads.md
├── ticket-app-django/      # Django app — test target for Lab 3
├── ticket-api/             # FastAPI app — test target for Labs 4 & 5
├── mkdocs.yml              # MkDocs site config
└── .github/workflows/
    ├── deploy-pages.yml    # Deploys docs on push to main
    └── release-apps.yml    # Builds and publishes app ZIPs on version tag
```

---

## Labs

| Lab | Topic | Where |
|-----|-------|-------|
| Lab 1 | Getting started with GitHub Copilot | GitHub Skills (hosted) |
| Lab 2 | Unit tests with GitHub Copilot | Microsoft Learn (hosted) |
| Lab 3 | Selenium → Playwright migration | `ticket-app-django/` |
| Lab 4 | JMeter load testing | `ticket-api/` |
| Lab 5 | pytest harness + test data generation | `ticket-api/` |

---

## Update cycle

### Updating lab content (docs only)

```bash
git add docs/
git commit -m "update lab content"
git push origin main
```

The Pages site rebuilds automatically in ~1 minute.

### Updating an app

```bash
git add .
git commit -m "update app"
git push origin main
git tag v1.1
git push origin v1.1
```

The tag triggers the release workflow — both ZIPs rebuild and are published to GitHub Releases. Download links in the docs update automatically.

### Updating both docs and an app

```bash
git add .
git commit -m "update docs and app"
git push origin main
git tag v1.2
git push origin v1.2
```

---

## Local preview

```bash
pip install mkdocs-material
mkdocs serve
```

Opens the site at `http://127.0.0.1:8000` with live reload.
