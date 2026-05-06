# Contributing

Thanks for considering a contribution to ReportForge.

ReportForge is documentation-only security tooling. Contributions must preserve the project boundary: no exploitation, scanning, credential collection, stealth, persistence, destructive behavior, or unauthorized target interaction.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
```

## Good Contributions

- Better report templates.
- Additional safe exporters.
- Schema improvements for documentation workflows.
- Quality checks that prevent accidental evidence leakage.
- Tests, documentation, examples, and accessibility improvements.

## Pull Request Checklist

- Tests pass with `pytest`.
- New behavior includes tests where practical.
- Public examples use synthetic data only.
- Documentation is updated when commands, schemas, or output formats change.
- The safety scope remains intact.
