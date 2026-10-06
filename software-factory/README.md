# Reference architecture — source

What the site renders for the second paper, and where the rest lives.

- `primitives.yaml` — the five primitives and the Agent Baseline outcomes each supports, from
  the paper's primitive tables.
- `signals.yaml` — the paper's "Measuring the Factory" table, as the five signals a secure
  factory shows and what each replaces.
- `maturity.yaml` — the five stages and the three maturity levels: for each level, where it
  runs, who coordinates the agents, and what it does at each stage. Rendered one level at a
  time, only while `params.softwareFactory.showMaturity` is true.
- `contributors.yaml` — the authors. Nothing renders with `confirmed: false`.

The paper's text is drafted in the working group's document and published as
`/software-factory.pdf`. Its source lands here as `software-factory.md` when the working group
moves it into this repository; until it does, the site shows no "View the source" link.
Comments go in as issues through the software-factory form, which carries the
`software-factory` label.
