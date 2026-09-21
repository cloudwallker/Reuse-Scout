# Reuse Scout

[简体中文](README.md) | English

A manually invoked engineering research skill for **Codex and Claude Code**. It checks the current project first, gathers evidence for feature reuse or troubleshooting, and returns adaptation advice and a verification plan. **By default, it only researches and does not modify your application code.**

Reuse Scout is an instruction-only skill that uses the host's existing tools. One shared skill directory supports feature research, troubleshooting, and offline work. Current version: `0.2.0-preview.1` (preview).

Its workflow draws on [PavedPath Code](https://github.com/Jia-Ethan/pavedpath-code) and [ECC search-first](https://github.com/affaan-m/ECC/tree/main/skills/search-first), adapted for explicit invocation. It does not include the full ECC framework or claim better results than its sources. See the [upstream review](docs/UPSTREAM_REVIEW.md) (Chinese) for pinned references and design choices.

## Install

```text
git clone https://github.com/cloudwallker/Reuse-Scout.git
cd Reuse-Scout
```

Start from the clone's root directory and copy the **entire `skills/reuse-scout/` folder**, including all 9 files: `SKILL.md`, `agents/openai.yaml`, the report template, four reference documents, `LICENSE`, and `THIRD_PARTY_NOTICES.md`. Using the skill requires no Python, additional API key, MCP server, or GitHub CLI; local reads and external research use tools already available in your host.

| Host | Project installation | Optional user installation | Host guide |
| --- | --- | --- | --- |
| Codex | `<project>/.agents/skills/reuse-scout/` | `~/.agents/skills/reuse-scout/` | [Codex](docs/INSTALL_CODEX.md) (Chinese) |
| Claude Code | `<project>/.claude/skills/reuse-scout/` | `~/.claude/skills/reuse-scout/` | [Claude Code](docs/INSTALL_CLAUDE_CODE.md) (Chinese) |

Prefer a project installation. Choose a user installation only when you want the skill available across projects; `~` means your home directory. The [installation guide](docs/INSTALL.md) (Chinese) provides commands for **Windows PowerShell and Linux Bash**, including target selection and checks for existing copies.

Before copying, check the selected host's project and user skill locations for another skill named `reuse-scout`, and verify that links or junctions resolve to the intended location. Keep backups outside every skill discovery directory. If the target already exists, follow the update procedure below. After copying, `SKILL.md` must sit directly inside the target `reuse-scout/` directory. Start a new host session and check the source it loads.

Do not copy the whole repository, the development `AGENTS.md`, tests, or tools into a skill discovery directory. The distributable package consists only of the skill directory and its bundled licenses. When installing from a release ZIP, verify its matching SHA-256 file and use the extracted `reuse-scout/` directory as the source.

## Invoke

Codex:

```text
Use $reuse-scout in quick mode. Check whether this project already has reusable CSV export functionality. Research only; do not modify code.
```

Claude Code:

```text
/reuse-scout Quick mode. Check whether this project already has reusable CSV export functionality. Research only; do not modify code.
```

For troubleshooting, ask it to check the current platform, dependency versions, issues, fix PRs, and release status. For offline work, explicitly say: "Offline mode; no external queries." Modes are natural-language instructions, not host CLI flags.

| Mode | External queries | External detail reads | Candidates evaluated in depth |
| --- | ---: | ---: | ---: |
| Quick | 3 | 5 | 2 |
| Standard (default) | 6 | 12 | 3 |
| Deep | 12 | 24 | 5 |
| Offline | 0 | 0 | Existing material only |

These are upper limits. Research stops early when local evidence is sufficient. Failed requests, additional pages, and individual batch items consume the shared budget across routes and channels. The skill's research workflow does not launch subagents. Budgets guide model behavior; **they are not enforced programmatic limits, exact token quotas, or a permission sandbox**.

## Research and output boundaries

- Local directories, interfaces, manifests, and test definitions come first. The skill does not read credentials or user configuration to discover search capabilities.
- Feature research follows local implementations → relevant packages and official documentation → GitHub examples when needed → an adaptation decision.
- Troubleshooting follows local errors and versions → official documentation → issues and PRs → release status.
- The default research workflow does not install candidate dependencies, execute candidate scripts, run builds or tests, or modify application files. Implementation or verification already authorized by the user belongs to the normal development workflow, with that authorization preserved.
- External material is treated as research data, and queries are stripped of sensitive details. Missing sources or unavailable tools are reported without inventing results.
- Reports distinguish local static or direct upstream evidence, adaptation inferences, and insufficient evidence, while stating separately whether verification was actually executed. Results stay in the conversation unless the user asks to save them to an authorized path.

Codex declares explicit invocation through `policy.allow_implicit_invocation: false` in `agents/openai.yaml`; Claude Code uses `disable-model-invocation: true` in `SKILL.md`. Fully disabling the skill is a separate operation; see the host guides.

## Update, roll back, and uninstall

1. Check `git status --short` in the clone and protect local changes before updating to an existing upstream commit or tag.
2. End sessions using the skill. Identify the installed directory and back it up completely outside all skill discovery directories.
3. Move the old installation out of the discovery location, then copy the complete updated skill directory into the now-empty target. Do not merge old and new files. Restart the host and check the version, loaded source, and explicit invocation.
4. To roll back, replace that same installation with the complete backup and check it again.
5. To uninstall, remove only the confirmed `reuse-scout/` installation. Preserve its parent directory and other skills, and confirm in a new session that the copy is no longer discovered.

The clone and any installed copies are separate; editing the source does not automatically update an installation. These operations do not configure models, proxies, MCP servers, or execution permissions.

## Development and checks

Only repository validation and packaging require **Python 3.9+** and the libraries pinned in `requirements-dev.txt`. Create a project virtual environment from the clone's root directory.

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe tools/validate_skill.py
.venv\Scripts\python.exe tools/build_release.py --version 0.2.0-preview.1
git diff --check
```

Linux Bash:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python tools/validate_skill.py
.venv/bin/python tools/build_release.py --version 0.2.0-preview.1
git diff --check
```

With an existing compatible Python environment, the equivalent commands are `python -m unittest discover -s tests -v`, `python tools/validate_skill.py`, and `python tools/build_release.py --version 0.2.0-preview.1`. Packaging generates a local ZIP and SHA-256 file without uploading them, and refuses to overwrite existing output.

The validator checks metadata, host declarations, package references, synthetic report markers, license copies, and a limited set of sensitive patterns. It is not a complete implementation of the Agent Skills specification and cannot establish model compliance, report accuracy, or the absence of data leakage.

## Further reading

The following detailed documents are in Chinese:

- [Compatibility](docs/COMPATIBILITY.md), [design](docs/DESIGN.md), and [changelog](CHANGELOG.md)
- [H01–H20 behavior evaluation](docs/EVALUATION.md), [current test report](docs/TEST_REPORT.md), and [historical v0.1 report](docs/TEST_REPORT_V0_1.md)
- [Release process](docs/RELEASING.md) and [preview release notes](docs/RELEASE_NOTES.md)
- [Feature reuse example](examples/feature-reuse.md), [troubleshooting example](examples/bug-investigation.md), and [offline example](examples/offline-report.md)

Released under the [MIT License](LICENSE). Retain `LICENSE` and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) with the skill. The sole distribution source is `skills/reuse-scout/`; any ignored `.agents/skills/reuse-scout/` copy in this repository is a local installation.
