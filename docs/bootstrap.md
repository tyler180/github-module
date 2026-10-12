# Bootstrap provenance

One generic template source lives in templates/generic. `scripts/render-template.py`
materializes `.in` files with supplied owner/reviewer and full workflow/hook SHAs
into a **new local directory** only. It refuses existing destinations. The optional
Go caller is the one language pilot; no Go module path is guessed.

Record actual template identity, source SHA observed immediately before/after
creation, generated initial commit, tree comparison, bootstrap PR/merged commit,
workflow pins, hook pins, and the relevant root commit/run IDs. Store the reviewed
record in the consuming configuration repository. No renderer output claims live
provenance, and no real evidence files are supplied here.

Provider template supports owner, repository, and include_all_branches, not a ref.
The module copies only the default branch. Reading source SHA before creation
does not pin the template; before/after equality and tree comparison strengthen
evidence but cannot remove all races. It is a creation-time copy, not ongoing sync.

For exact reproducibility, create a basic repository and open a bootstrap PR with
tracked files taken from an exact reviewed source commit plus explicit substitutions.
Record source tree and destination commits. Subsequent updates always use PRs.
CODEOWNERS must name actual authorized owners; template placeholders cannot be
left in a published template. Required-check contexts must be observed rather than
inferred from the workflow filename or the job name platform-ci.

References: [template provider contract](https://github.com/integrations/terraform-provider-github/blob/v6.13.0/docs/resources/repository.md),
[GitHub template behavior](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template).
