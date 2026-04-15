# auto-upgrade

LangGraph-based Python package upgrade agent, powered by Claude Opus 4.6.

This is a standalone sub-project that lives under `src/` of the
`python-auto-package-mgiration` repository. It does **not** depend on, and never
modifies, the sibling `package-upgrade/` Claude Code Skill.

## Install (dev mode)

```bash
cd src
pip install -e ".[dev]"          # core + tests
# or, to enable SqliteSaver checkpointer:
pip install -e ".[dev,sqlite]"
```

## Usage

```bash
export ANTHROPIC_API_KEY=sk-ant-...

auto-upgrade ~/projects/myapp --package requests --version 2.32.0
auto-upgrade ~/projects/myapp --cve CVE-2024-35195
auto-upgrade ~/projects/myapp --package django --version 5.1 \
    --model claude-sonnet-4-6 \
    --test-command "tox -e py311" \
    --checkpointer sqlite
```

See `AutoUpgradePackageDesign_with_LangGraph.md` at the repository root for the
full system design.

## Run tests

```bash
pytest
```
