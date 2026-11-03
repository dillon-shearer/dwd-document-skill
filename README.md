# DWD Document Skill

Document branding skill for Data With Dillon (DWD): rules and templates any AI agent can read to produce on-brand Word, PowerPoint and other documents. It follows the open Agent Skills format, with `SKILL.md` at the root, rules under `references/` and templates under `assets/`. Everything is plain markdown. GitHub: https://github.com/dillon-shearer/dwd-document-skill

## How to point an agent at it

1. Clone the repo and tell the agent to read the folder, starting with `SKILL.md`.
2. Give the agent the raw URL of the skill: https://raw.githubusercontent.com/dillon-shearer/dwd-document-skill/main/SKILL.md
3. Install it as a Claude Code skill: copy the folder into `.claude/skills/` (for example `.claude/skills/dwd-document-skill/`) in your project or home directory.

## Formats covered

- Brand rules shared by all formats: done
- Word (.docx): done
- PowerPoint (.pptx): done
- Markdown (.md): done
- Excel (.xlsx): done
- HTML: done

## Choose the brand

1. Open `docs/brand-picker.html` in a browser (double-click it; no server or install needed).
2. Pick one option in each of the 13 sections. Option A always matches the DWD website. Choices save in the browser as you go.
3. Add anything else in the Notes box, then press Copy choices.
4. Paste the copied block into the board notepad. If the clipboard is blocked, select the text in the Copied text box and copy it by hand.

## How to check

Run `python check.py` from the repo root. It exits 0 when every check passes or is skipped.

## License

MIT. See [LICENSE](LICENSE).
