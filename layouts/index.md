{{- /* A text version: one published document as Markdown, for agents.

     One template serves every entry in params.texts (hugo.toml). Hugo selects
     it for any home-page output format whose media type is text/markdown, and
     partials/text-entry.html says which document this rendering is.

     A short YAML header comes first, saying what the file is a version of: the
     canonical page, the version, the licence, and where the source lives. YAML
     because Markdown tooling already reads a leading `---` block as metadata,
     and a reader that does not loses nothing. Values go through jsonify, which
     writes a quoted string that is also valid YAML, so a title with a colon in
     it cannot break the header.

     The body is partials/text-body.html: the source, with relative links made
     absolute. */ -}}
{{- $e := partial "text-entry.html" . -}}
{{- if not $e -}}{{- errorf "no params.texts entry is written by %s — check its format name" .RelPermalink -}}{{- end -}}
---
title: {{ $e.title | jsonify }}
canonical: {{ absURL $e.page | jsonify }}
version: {{ site.Params.version | jsonify }}
published: {{ partial "published-iso.html" . | jsonify }}
license: {{ $e.license | jsonify }}
license_url: {{ $e.license_url | jsonify }}
{{- with $e.pdf }}
pdf: {{ absURL . | jsonify }}
{{- end }}
{{- with $e.data }}
data: {{ printf "%s/blob/main/%s" site.Params.repo . | jsonify }}
{{- end }}
source: {{ printf "%s/blob/main/%s" site.Params.repo $e.source | jsonify }}
---

{{ partial "text-body.html" $e -}}
