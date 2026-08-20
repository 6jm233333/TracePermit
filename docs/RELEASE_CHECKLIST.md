# v1.0.0 release checklist

The source package is prepared for a fixed v1.0.0 release. The two external
identifiers remain unset until the author supplies the public GitHub URL and
publishes the archive under an authenticated account.

## GitHub

1. Create the public repository and push this `TracePermit/` directory.
2. Create a Git tag and release named `v1.0.0`.
3. Replace the pending `repository-code` comment in `CITATION.cff`, the
   repository line in `README.md`, and `metadata.json.repository_url`.
4. Regenerate `CHECKSUMS.sha256` and rerun all CI commands.

## Zenodo

Zenodo's GitHub integration can archive a tagged release, or the archive can
be uploaded through the deposit API. The account owner must enable the GitHub
repository or provide a token with `deposit:write` and `deposit:actions`
scopes. Use `.zenodo.json` as the metadata source, publish exactly the
`v1.0.0` tag, and record the returned DOI URL.

After publication, replace the pending DOI in `README.md` and `CITATION.cff`,
set `metadata.json.doi` to the returned DOI, set
`metadata.json.archive_status` to `published`, regenerate checksums, and rerun
`verify_release.py`, `summarize_results.py`, and the unit tests. Do not commit
an access token or claim a DOI before the Zenodo record is public.
