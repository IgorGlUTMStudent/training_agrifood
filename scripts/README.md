# Script lifecycle

## ACTIVE TOOLING

`scripts/verify.ps1` is the maintained developer verification helper: it runs the backend pytest suite, then the frontend production build. It may evolve when the repository verification workflow legitimately changes and may be modified under a bounded future contract. It is not historical analytical evidence. Dependency setup and the full local gate are documented in the [root README](../README.md#checks).

## FROZEN / PROVENANCE-SENSITIVE EVIDENCE REPRODUCTION

- `scripts/vdr04a_predictability.py`
- `scripts/vdr04b_telemetry_ablation.py`
- `scripts/vdr05_logistics_signal_audit.py`

These VDR scripts are accepted evidence / reproduction tooling with a provenance-sensitive lifecycle. They belong to accepted analytical evidence history. Do not opportunistically refactor, format, or clean them up; byte-level changes can invalidate recorded provenance and hashes. Do not wire them into ordinary PR CI without a separate evidence decision. Application dependencies intentionally do not include their full scientific analysis environment.

`docs/data_recon/*_results.json` files are accepted generated evidence artifacts, not disposable build output. Research output is not automatically canon; promotion requires the accepted project decision process.

### Required output rule

All three scripts support `--output`, and their defaults target accepted result artifacts under `docs/data_recon/`. Every exploratory or reproduction run must pass an explicit `--output` path outside the repository or in a disposable scratch location. Never target accepted artifacts or rely on the defaults for these runs.

For example, from the repository root in a separately prepared analysis environment, choose the relevant command with a disposable output in the system temporary directory:

```powershell
python scripts/vdr04a_predictability.py --output "$env:TEMP\vdr04a-scratch-results.json"
python scripts/vdr04b_telemetry_ablation.py --output "$env:TEMP\vdr04b-scratch-results.json"
python scripts/vdr05_logistics_signal_audit.py --output "$env:TEMP\vdr05-scratch-results.json"
```

These commands retain each script's existing input defaults. VDR-04B reads the accepted VDR-04A results for comparison; VDR-05 reads the accepted VDR-04B results. Reproduction does not authorize replacing those accepted artifacts.
