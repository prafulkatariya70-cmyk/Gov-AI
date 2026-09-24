# GovCareerAI deployment: Vercel + Supabase

## Architecture

- Vercel Hobby hosts the FastAPI API from `api/index.py`.
- Supabase Free hosts the existing PostgreSQL database.
- GitHub Actions runs production ingestion every 30 minutes.
- The local APScheduler remains available for local development, but is disabled automatically on Vercel.

Vercel's current FastAPI deployment model serves the FastAPI application as a Vercel Function. Supabase recommends the shared transaction-mode pooler for serverless workloads.

## Supabase connection modes

Use the Supabase **shared pooler** for the two IPv4-only deployment environments:

| Component | Supabase mode | Port | Purpose |
|---|---|---:|---|
| Vercel FastAPI | Shared pooler — Transaction mode | 6543 | Short-lived serverless API connections |
| GitHub Actions | Shared pooler — Session mode | 5432 | Alembic migrations + ingestion |
| Local Windows backend | Direct connection when IPv6 works; otherwise Session pooler | 5432 | Development |
| Expo app | FastAPI only | — | Never expose PostgreSQL credentials |

Supabase documents the shared pooler as IPv4-only on all plans. Direct connections on the Free plan are IPv6-only, while GitHub Actions and Vercel are IPv4-only. Session mode uses port 5432 and transaction mode uses port 6543.

For Vercel, the application disables psycopg prepared statements because transaction pooling does not support them.

For GitHub Actions, use the **Session pooler** shown in Supabase Connect. Do not use the IPv6-only Direct Connection from the Free plan.

## One-time Supabase setup

1. Create the Supabase project on the Free plan.
2. Open **Connect**.
3. For the Vercel API, copy the **Shared pooler / Transaction mode** connection.
4. For GitHub Actions, copy the **Shared pooler / Session mode** connection.
5. Keep the database password private. Percent-encode reserved characters if they are placed into a URL connection string.

The application reads these environment variables:

- `DATABASE_USER`
- `DATABASE_PASSWORD`
- `DATABASE_HOST`
- `DATABASE_PORT`
- `DATABASE_NAME`
- `COMPATIBILITY_DEVELOPMENT_USER_EMAIL`

Recommended Vercel values:

- `DATABASE_USER` = the Supabase shared-pooler username (for example `postgres.<project-ref>`)
- `DATABASE_PASSWORD` = Supabase database password
- `DATABASE_HOST` = the shared pooler host
- `DATABASE_PORT` = `6543`
- `DATABASE_NAME` = `postgres`
- `COMPATIBILITY_DEVELOPMENT_USER_EMAIL` = a stable internal development email

Recommended GitHub Actions values:

- `DATABASE_USER` = the same shared-pooler username
- `DATABASE_PASSWORD` = Supabase database password
- `DATABASE_HOST` = the shared pooler host
- `DATABASE_PORT` = `5432`
- `DATABASE_NAME` = `postgres`
- `COMPATIBILITY_DEVELOPMENT_USER_EMAIL` = the same stable internal development email

## One-time Vercel setup

1. Import `prafulkatariya70-cmyk/Gov-AI` into Vercel.
2. Keep the repository root as the Vercel project root.
3. Vercel will detect the FastAPI app through `api/index.py`.
4. Add the six environment variables above to **Production**.
5. Deploy.
6. Verify `/health`, `/health/database`, and `/api/jobs`.

Do not add an APScheduler cron to Vercel Hobby. This project needs more frequent ingestion, so GitHub Actions provides the scheduler instead.

## One-time GitHub Actions setup

In the repository's **Settings → Secrets and variables → Actions**, add these repository secrets:

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
