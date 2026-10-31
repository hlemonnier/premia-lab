# Public repository and discovery

## Current status

The owner renamed the existing repository to
[`hlemonnier/premia-lab`](https://github.com/hlemonnier/premia-lab) and made it public.
Both settings were verified on 31 October 2026. This was an in-place change, not a
new clean-history repository. `main` remains the maintained branch.

The older [migration record](project-migration.md) describes the state and proposed
publication route at that earlier point. It is retained as a historical record,
not a statement that the repository is still private.

## Licensing and citation

Original maintained code and associated documentation are MIT-licensed; see
[LICENSE](../LICENSE) and [NOTICE.md](../NOTICE.md) for scope and external-material
exceptions. [CITATION.cff](../CITATION.cff) contains the canonical repository URL,
author and research keywords. Cite an exact commit for reproducibility.

## Repository description and topics

The intended About description is:

> Characteristic-factor forecasts, conditional risk and cost-aware portfolios, with causal tests and an auditable research archive.

Recommended GitHub topics:

```text
quantitative-finance, quantitative-research, factor-models,
portfolio-optimization, risk-management, transaction-costs,
backtesting, time-series, statistical-learning,
reproducible-research, synthetic-data, python
```

These are repository settings, not inferred automatically from a README or citation
file. Committing this document does **not** apply them. An authenticated repository
administrator can apply the description and add the topics without changing code,
visibility, branches or history:

```bash
gh repo edit hlemonnier/premia-lab \
  --description "Characteristic-factor forecasts, conditional risk and cost-aware portfolios, with causal tests and an auditable research archive." \
  --add-topic quantitative-finance,quantitative-research,factor-models,portfolio-optimization,risk-management,transaction-costs,backtesting,time-series,statistical-learning,reproducible-research,synthetic-data,python
```

Read back the actual settings with:

```bash
gh api repos/hlemonnier/premia-lab --jq '{name: .full_name, visibility: .visibility, description: .description, topics: .topics, license: .license.spdx_id}'
```

No RL, deep-learning or live-trading topic is suggested: those would misdescribe
the maintained implementation.

## Legacy history

The maintained tree excludes raw benchmark inputs and the external scorer and
specification. Renaming or changing visibility does not remove older Git objects.
The existing history was not sanitized by the public-facing documentation update.
No project license grants rights to third-party material in earlier revisions.

`tools/publish_public.py` is retained as a clean-snapshot export utility. Its preview
performs no remote write; its publish mode refuses an existing destination. It is
not needed to publish this already-public repository, and must not be used to
replace it accidentally. Never put an access token in a document or chat.

References: [GitHub CLI repository editing](https://cli.github.com/manual/gh_repo_edit),
[repository topics](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics),
and [citation files](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files).
