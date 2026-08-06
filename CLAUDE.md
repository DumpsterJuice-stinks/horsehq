# CLAUDE.md

Guidance for Claude Code and other AI assistants working in this repository.

## What this repository is

`horsehq` is a **content repository** for TheHorseHQ, an equestrian product.
It holds marketing and copywriting assets written as Markdown. There is no
application code here.

Read that literally before you start work:

- No `package.json`, `pyproject.toml`, `Makefile`, or any other manifest.
- No source directories, no dependencies, no build step.
- No test suite, no linter, no CI workflows (`.github/` does not exist).
- Nothing to install, compile, serve, or run.

If a task seems to call for running a build or a test, the correct response is
that this repository has none — not to scaffold one. Only add tooling when the
user explicitly asks for it.

## Layout

```
horsehq/
└── marketing/
    └── facebook-group-post-prompt.md
```

`marketing/` holds go-to-market assets. Today that is a single file; new
copywriting, prompts, and channel playbooks belong alongside it. Create a new
top-level directory only when content genuinely does not fit under an existing
one, and prefer descriptive kebab-case filenames (`facebook-group-post-prompt.md`,
not `fb_prompt.md` or `Prompt2.md`).

## The product

TheHorseHQ is described in the existing copy as an app for tracking horse care
and costs — vet, farrier, worming, feed, competition entries — per horse, with
reminders and export.

**Treat that as unverified.** `marketing/facebook-group-post-prompt.md` flags it
explicitly as an assumption for its worked example, and there is no product
brief, spec, or source of truth in this repository. Do not state product
features, pricing, or claims as fact in new copy. Either use the bracketed-slot
approach the existing prompt uses, or ask the user for the real brief.

## Content conventions

The one existing document sets the house style. Match it.

**Structure.** Title as a single `#` heading, one-line description underneath,
then `---`-separated sections. Sections are short and load-bearing: the prompt
itself, a table of what matters when filling it in, a worked example, and a
pre-flight checklist. Do not pad with preamble or a summary of what the reader
just read.

**Prompts are fenced and copy-pasteable.** Reusable prompts live in a plain
` ``` ` block with `[bracketed slots]` for the caller to fill. The block should
survive a copy-paste into any LLM with no editing beyond the slots.

**Examples are blockquoted.** Sample output uses `>` so it is unmistakably
distinct from instructions to the reader.

**Tables carry consequences, not definitions.** The existing table's second
column is "Get this wrong and…". Prefer that framing — tell the reader what
breaks — over restating what a field is.

**Voice.** Direct, second person, contractions, short sentences. Concrete over
abstract. British English (`favourite`, `£`) and a UK equestrian audience.
No hype, no emoji decoration, no exclamation marks.

**Honesty about claims.** The existing prompt ends by naming the riskiest
checkable claim in each variant, and instructs against inventing features,
prices, or results. Carry that discipline into anything new: if a line is only
true under an assumption, say so where the reader will see it.

## Git workflow

- The remote default branch is `claude/thehorsehq-facebook-post-gunfit`.
  **There is no `main` or `master`** — do not assume one exists, and check
  `git remote show origin` rather than guessing a base branch.
- Work happens on `claude/<topic>` branches, one topic per branch.
- Commit messages: an imperative one-line subject (`Add Facebook group post
  prompt for TheHorseHQ`), a blank line, then a short body explaining what the
  change contains and why.
- Push with `git push -u origin <branch-name>`.
- Do not open a pull request unless the user asks for one.

## Working here

- Commit content changes; a Markdown file is the deliverable, not an
  intermediate artifact.
- Keep prose wrapped to roughly the width of the surrounding file (~90 columns
  in the existing document) so diffs stay readable.
- When editing an existing document, preserve its section order and heading
  levels unless restructuring is the point of the task.
- Do not add license headers, badges, or a README unless asked.
