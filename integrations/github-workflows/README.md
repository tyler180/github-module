# github-workflows local additions

Direct writes to the sibling checkout were rejected by this session's writable
root policy. `additions/` contains the complete files intended for github-workflows.
`local-additions.patch` adds them and appends TERRAFORM-addendum.md to existing
TERRAFORM.md; it does not change any existing workflow. baseline-sha256.json records
the inspected original bytes. The patch is verified against an isolated temporary
copy, not applied to the sibling repository.

Build/rebuild without modifying the sibling:

```sh
python3 scripts/build-workflows-patch.py --checkout /path/to/github-workflows
```

Review/apply later in a session that can write the sibling checkout. No push,
release, caller installation, credentials, backend, or deployment enablement is
part of this patch. All new workflows use workflow_call only.

New shared components: module validation, generic hygiene, Go pilot, offline policy
fixtures and isolated plan evaluation, hook definitions, standard-library policy
and receipt tests. Pins copied from existing workflow conventions were retained;
setup-go v6 SHA was resolved from the official action repository.

Live collection, protected accepted-record storage/writer, trustworthy plan JSON
production, and deployment-gate integration remain explicitly pending. Offline
receipts cannot authorize a live apply.
