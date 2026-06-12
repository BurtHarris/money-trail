# Airflow hosts the project docs browser

We expose the curated repository markdown set inside the Airflow UI through a plugin-backed external view instead of a separate docs site. That keeps operational and reference material in one authenticated browser session, supports print-friendly review, and lets the docs render directly from the repo files without a separate publishing step.
