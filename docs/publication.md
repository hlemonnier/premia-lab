# Publishing the project safely

The existing private repository contains externally supplied material in its Git history. A clean current working tree or deleted branches do not remove old Git objects. Do not switch that legacy repository to public and assume the old content is hidden.

The prepared route publishes **a new repository with a clean root commit**, called `premia-lab`, and keeps the old history private. The reviewed code, documentation and filtered research archive are copied; the original benchmark data, scorer and specification are not.

On a machine with Git, Python and the GitHub CLI installed and authenticated, run from this project:

```bash
python tools/publish_public.py             # validate and preview; no remote writes
python tools/publish_public.py --publish   # create OWNER/premia-lab, public, only main
```

The script refuses to overwrite an existing destination. It uses `gh`'s existing authentication; do not paste tokens into chat. It does not delete the private repository or transfer its history. A software license is a separate decision and is not silently selected by this operation.

The original branch consolidation preserves all branch heads as parents in the private repository before removing the corresponding branch references. The public archive explicitly records retained source/report files, redactions and omissions. A historical source snapshot is not a claim that all experiments were rerun during publication.

References: GitHub's documentation on [removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository) and the [GitHub CLI repository creation command](https://cli.github.com/manual/gh_repo_create).
