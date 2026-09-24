# GovCareerAI deployment: Vercel + Supabase

## Architecture

- Vercel Hobby hosts the FastAPI API from `api/index.py`.
- Supabase Free hosts the existing PostgreSQL database.
- GitHub Actions runs production ingestion every 30 minutes.
- The local APScheduler remains available for local development, but is disabled automatically on Vercel.

Vercel's current FastAPI deployment model serves the FastAPI application as a Vercel Function. Supabase recommends the shared transaction-mode pooler for serverless workloads.

## One-time Supabase setup

1. Create a Supabase project on the Free plan.
2. Open **Connect** and copy the PostgreSQL connection details.
3. For the Vercel API, use the **shared pooler / transaction mode** connection (port 6543).
4. For GitHub Actions migrations/ingestion, the same pooler can be used for this project; a direct connection is also appropriate for migrations if your network supports it.

The application currently reads these environment variables:

- `DATABASE_USER`
- `DATABASE_PASSWORD`
- `DATABASE_HOST`
- `DATABASE_PORT`
- `DATABASE_NAME`
- `COMPATIBILITY_DEVELOPMENT_USER_EMAIL`

Recommended Vercel values are the Supabase transaction-pooler host/user/password, port `6543`, and database `postgres`.

## One-time Vercel setup

1. Import `prafulkatariya70-cmyk/Gov-AI` into Vercel.
2. Keep the repository root as the Vercel project root.
3. Vercel will detect the FastAPI app through `api/index.py`.
4. Add the six environment variables above to **Production**.
5. Deploy.
6. Verify `/health`, `/health/database`, and `/api/jobs`.

Do not add an APScheduler cron to Vercel Hobby. Vercel Hobby cron scheduling is limited to daily execution, while this project needs more frequent ingestion. GitHub Actions provides the 30-minute scheduler instead.

## One-time GitHub Actions setup

In the repository's **Settings → Secrets and variables → Actions**, add the same database values as repository secrets:

- `DATABASE_USER`
- `DATABASE_PASSWORD`
- `DATABASE_HOST`
- `DATABASE_PORT`
- `DATABASE_NAME`
- `COMPATIBILITY_DEVELOPMENT_USER_EMAIL`

The workflow `.github/workflows/production-ingestion.yml` then runs:

1. database migrations
2. due-source detection
3. UPSC/SSC/RRB/Karnataka/KPSC ingestion through the existing adapter registry
4. persistence and eligibility parsing

It also supports **workflow_dispatch** for a manual production sync.

## Frontend

After the Vercel API is live, set the Expo production environment variable:

`EXPO_PUBLIC_BACKEND_URL=https://<your-vercel-project>.vercel.app`

Then build the mobile app with the existing EAS profiles.

## Free-tier note

Vercel Hobby is currently $0/month, but its terms limit Hobby usage to personal/non-commercial use. Supabase Free is $0/month with a 500 MB database quota and projects can pause after one week of inactivity. Revisit the hosting plan before enabling commercial monetization such as paid subscriptions or advertising.
