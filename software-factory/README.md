# Reference architecture — source

The second paper, "The Secure Software Factory: A Reference Architecture", and what the
site renders from it.

- `software-factory.md` — the paper. Its text is the working group's final document, word
  for word; change it here only to match a change the working group makes. `bin/build-pdf
  --paper software-factory` renders it to `/software-factory.pdf`.
- `figures/` — the paper's figures, generated. The PDF prints them and the page inlines the
  same drawings (`bin/sync-figure-partial`), so the two can't disagree.
- `boundaries.yaml` — the four security boundaries as the page lists them, in the paper's
  words, and the figure shown with them.
- `levels.yaml` — the three levels of autonomy as the page shows them, one at a time: each
  level's opening sentence, its row of the paper's level table, and its figure. Rendered
  only while `params.softwareFactory.showLevels` is true.
- `contributors.yaml` — the authors, from the paper's byline. Nothing renders with
  `confirmed: false`.

Comments go in as issues through the software-factory form, which carries the
`software-factory` label.
