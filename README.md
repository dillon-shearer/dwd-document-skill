# DWD Document Skill

Document branding skill for Data With Dillon (DWD): rules and templates any AI agent can read to produce on-brand Word, PowerPoint and other documents. It follows the open Agent Skills format, with `SKILL.md` at the root, rules under `references/` and templates under `assets/`. Everything is plain markdown. GitHub: https://github.com/dillon-shearer/dwd-document-skill

## How to point an agent at it

1. Clone the repo and tell the agent to read the folder, starting with `SKILL.md`.
2. Give the agent the raw URL of the skill: https://raw.githubusercontent.com/dillon-shearer/dwd-document-skill/main/SKILL.md
3. Install it as a Claude Code skill: copy the folder into `.claude/skills/` (for example `.claude/skills/dwd-document-skill/`) in your project or home directory.

## Formats covered

- Brand rules shared by all formats: in progress
- Word (.docx): in progress
- PowerPoint (.pptx): in progress

## How to check

Run `python check.py` from the repo root. It exits 0 when every check passes or is skipped.

## License

MIT. See [LICENSE](LICENSE).
