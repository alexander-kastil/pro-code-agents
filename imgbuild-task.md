## Devcontainer Image Build & Maintenance Task Guide

This document captures the end-to-end workflow for building, testing, publishing, switching, and maintaining the prebuilt devcontainer image used by this repository. It also clarifies when to use the Windows host vs. the in-container build path.

### 1. Goal

Speed up developer onboarding (Codespaces + local) by publishing a ready-to-use image to GHCR: `ghcr.io/alexander-kastil/pro-code-agents-dev:latest`.

### 2. Build Paths Overview

- **CI (GitHub Action)**: Canonical build. Triggered on changes to `.devcontainer/**`. Produces `latest`, commit SHA, and tag-based images.
- **Devcontainer (inside container)**: Quick sanity check that the Dockerfile still builds. Single-arch, slower layering.
- **Windows Host (Docker Desktop)**: Recommended for iterative optimization, multi-arch builds, and caching. Can use WSL2 backend.

### 3. Prerequisites (Windows Host)

1. Install Docker Desktop (with WSL2 backend enabled if desired).
2. Ensure you are authenticated to GitHub Container Registry (GHCR) or have a Personal Access Token (classic) with `read:packages`, `write:packages`.
3. (Optional) Enable experimental features for buildx multi-arch.

### 4. Clone & Branch

```bash
git clone https://github.com/alexander-kastil/pro-code-agents.git
cd pro-code-agents
git checkout -b image-maintenance
```

### 5. Local Build (Single Arch) – Windows / WSL

```bash
docker build -t ghcr.io/alexander-kastil/pro-code-agents-dev:local -f .devcontainer/Dockerfile .
```

Validate core tools:

```bash
docker run --rm ghcr.io/alexander-kastil/pro-code-agents-dev:local node -v
docker run --rm ghcr.io/alexander-kastil/pro-code-agents-dev:local dotnet --list-sdks | head -n 3
docker run --rm ghcr.io/alexander-kastil/pro-code-agents-dev:local az version | head -n 1
```

### 6. Multi-Arch Build (amd64 + arm64)

```bash
# Create / use a buildx instance
docker buildx create --name devx --use || docker buildx use devx
docker buildx inspect --bootstrap

# Build and push directly (skips local load)
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f .devcontainer/Dockerfile \
  -t ghcr.io/alexander-kastil/pro-code-agents-dev:latest \
  -t ghcr.io/alexander-kastil/pro-code-agents-dev:$(git rev-parse --short HEAD) \
  --push .
```

### 7. GHCR Login (if pushing manually)

```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u alexander-kastil --password-stdin
# or with PAT: echo $PAT | docker login ghcr.io -u alexander-kastil --password-stdin
```

### 8. Tagging Strategy

- `latest`: Always the most recent successful build from `master`.
- `sha`: Immutable per commit (`<short-sha>`).
- Optional semantic tags (e.g. `v1.0.0`) when making workshop-stable snapshots.
- Pin a version in `devcontainer.json` by replacing `latest` with desired tag.

### 9. Switch Between Source Build and Prebuilt Image

Source build config is preserved as: `.devcontainer/devcontainer-source.json`.
Steps:

```bash
mv .devcontainer/devcontainer.json .devcontainer/devcontainer-image.json   # backup current image config
cp .devcontainer/devcontainer-source.json .devcontainer/devcontainer.json  # restore Dockerfile build mode
```

Reopen / rebuild container. To go back:

```bash
mv .devcontainer/devcontainer.json .devcontainer/devcontainer-source.json
mv .devcontainer/devcontainer-image.json .devcontainer/devcontainer.json
```

### 10. CI Workflow (Already Added)

File: `.github/workflows/devcontainer-image.yml`
Actions:

1. Checkout
2. Setup buildx
3. Login GHCR
4. Metadata (tags + labels)
5. Build & push (current: single arch) – can be extended for multi-arch.

To force a fresh publish without Dockerfile changes: manual dispatch in GitHub UI (Actions tab → workflow → Run workflow).

### 11. Extending Workflow (Future Enhancements)

- Multi-arch: add `platforms: linux/amd64,linux/arm64` to build-push step.
- Vulnerability scan: integrate `aquasecurity/trivy-action` post-build.
- Digest pinning: output `${{ steps.build.outputs.digest }}` for reproducible references.
- Scheduled rebuild (weekly) to pick up base image security updates.
- Automatic semver tagging on annotated git tags.

### 12. Testing the Image After CI Publish

```bash
docker pull ghcr.io/alexander-kastil/pro-code-agents-dev:latest
docker run --rm ghcr.io/alexander-kastil/pro-code-agents-dev:latest func --version
docker run --rm ghcr.io/alexander-kastil/pro-code-agents-dev:latest pwsh -c "$PSVersionTable.PSVersion"
```

### 13. Updating the Devcontainer to Pin a Version

Edit `.devcontainer/devcontainer.json`:

```jsonc
{
  "image": "ghcr.io/alexander-kastil/pro-code-agents-dev:3a1f2c7" // example
}
```

Reopen container to ensure reproducibility for a workshop.

### 14. Cleanup Old Local Images

```bash
docker images | grep pro-code-agents-dev
docker image prune -f
docker rmi <image-id>  # remove specific old tags
```

### 15. Common Pitfalls & Fixes

| Issue                           | Cause                              | Fix                                                            |
| ------------------------------- | ---------------------------------- | -------------------------------------------------------------- |
| Image pull fails                | Missing GHCR auth for private repo | `docker login ghcr.io` with valid token                        |
| Extensions missing              | Old cached image                   | `docker pull` then reopen container                            |
| Multi-arch mismatch             | Only built amd64                   | Rebuild with buildx multi-platform                             |
| Long build times locally        | Layer cache invalidated            | Avoid unnecessary Dockerfile reorder; keep stable early layers |
| Permissions issues in workspace | Host volume ownership              | Run `bash .devcontainer/post-create.sh` inside container       |

### 16. Periodic Maintenance Checklist

- [ ] Review Dockerfile for redundant installations (e.g., duplicate Node sources)
- [ ] Run vulnerability scan
- [ ] Rebuild image weekly for patches
- [ ] Validate tool versions haven’t regressed (`validate-setup.sh`)
- [ ] Prune unused tags in GHCR (optional)

### 17. Optional: Add Trivy Scan Locally

```bash
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image ghcr.io/alexander-kastil/pro-code-agents-dev:latest
```

### 18. Rollback Strategy

If a new image breaks workflows:

1. Pin previous digest/tag in `devcontainer.json`.
2. Investigate diff between Dockerfile versions.
3. Re-run CI with fix; remove rollback pin when stable.

### 19. Decision Matrix (Where to Build)

| Scenario                           | Recommended Path                          |
| ---------------------------------- | ----------------------------------------- |
| Quick Dockerfile syntax check      | Devcontainer build                        |
| Performance optimization iteration | Windows host build                        |
| Multi-arch release                 | Windows host buildx (then automate in CI) |
| Official published image           | GitHub Action                             |
| Workshop freezing version          | Pin SHA/tag in `devcontainer.json`        |

### 20. Next Potential Improvements

- Add caching layer for npm global installs through separate COPY stage.
- Split base runtime from tooling (two-stage) for faster updates.
- Add provenance / SBOM generation (`docker buildx build --sbom` + `cosign` if needed).
- Optional layer: move PowerShell modules install to build arg toggle.

---

Keep this file updated whenever process or workflow changes.
