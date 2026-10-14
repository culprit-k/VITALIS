# Reproducible workflows

Scripts will be added only when their inputs, outputs, validation checks, and run instructions are defined. Keep local data outside the repository. Do not write patient-level data or predictions into tracked paths.

Planned workflows:
- Validate source dataset inventory and schema.
- Build cohort-level summaries without exporting patient records.
- Train transparent baseline models using patient-level splits.
- Evaluate calibration and alert burden using frozen evaluation splits.
