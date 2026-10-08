# GovCareer AI Launch Runbook

## Production architecture

- **API:** FastAPI deployed as a Vercel Python function through `api/index.py`.
- **Database:** PostgreSQL, using the Supabase transaction pooler for serverless API traffic.
- **Ingestion:** GitHub Actions runs `backend/scripts/run_ingestion.py` every 30 minutes.
- **Migrations:** Production ingestion runs `alembic upgrade head` before fetching jobs.
- **OCR:** Tesseract OCR is installed in the ingestion runner.

## Vercel environment variables

Configure these variables for the Production environment:

- `DATABASE_USER`
- `DATABASE_PASSWORD`
- `DATABASE_HOST`
- `DATABASE_PORT`
- `DATABASE_NAME`

Use the Supabase transaction-pooler connection details for the Vercel API deployment. Do not commit credentials to the repository.

After deployment, verify:

- `/health` returns `{"status":"healthy"}`.
- `/health/database` reports a successful `SELECT 1`.
- `/api/ingestion/status` returns configured source health and latest-run information.

## GitHub Actions secrets

Configure these repository secrets for the `Production Job Ingestion` workflow:

- `DATABASE_USER`
- `DATABASE_PASSWORD`
- `DATABASE_HOST`
- `DATABASE_PORT`
- `DATABASE_NAME`
- `COMPATIBILITY_DEVELOPMENT_USER_EMAIL`

The ingestion workflow must be able to connect to the same production PostgreSQL database used by the API.

## First production run

1. Confirm the Vercel API health endpoints.
2. Confirm all GitHub Actions production secrets exist.
3. Run the **Production Job Ingestion** workflow manually.
4. Confirm the workflow applies migrations and completes ingestion.
5. Inspect `/api/ingestion/status`.
6. Confirm current/upcoming jobs are visible through `/api/jobs`.
7. Confirm expired/closed jobs are excluded from the public feed.
8. Confirm each source has a useful latest-run status/error when applicable.

## Supported initial sources

- UPSC
- SSC
- RRB (initial regional implementation)
- KPSC
- Karnataka Teacher recruitment

Source coverage can be expanded independently after launch; a failed source must not prevent other sources from completing.

## Launch gate

The product is ready for public launch when:

- API health is green.
- Database health is green.
- Production ingestion completes successfully.
- At least one official source produces a verified current/upcoming job.
- Expired/closed jobs are excluded from the public feed.
- The frontend points to the production API.
