# ADR 009: One language pilot

Status: generic source and Go caller implemented locally.

Decision: one generic template, Go workflow pilot with explicit version/path.
Alternative: four templates and automatic language detection now. Consequence:
minimal maintenance and no guessed module path; Terraform/mixed profiles follow
demonstrated pilot success. Terraform module validation already has its own workflow.
