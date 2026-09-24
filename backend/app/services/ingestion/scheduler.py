import os
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from app.db.session import SessionLocal
from app.services.ingestion.runner import run_due_sources


scheduler = BackgroundScheduler()


def scheduled_ingestion() -> None:
    """
    Run ingestion for all sources that are due.
    """

    db = SessionLocal()

    try:
        results = run_due_sources(db)

        print("\n========== SCHEDULED INGESTION ==========")
        print(f"Sources processed: {len(results)}")

        for result in results:
            print(
                f"Run {result.id} | "
                f"Source {result.source_id} | "
                f"Status: {result.status} | "
                f"Discovered: {result.discovered} | "
                f"Created: {result.created} | "
                f"Updated: {result.updated}"
            )

        print("=========================================\n")

    except Exception as exc:
        print(
            f"Scheduled ingestion error: {exc}"
        )

    finally:
        db.close()


def start_scheduler() -> None:
    """
    Start the background ingestion scheduler.

    Vercel runs FastAPI as serverless functions, so persistent APScheduler
    workers are intentionally disabled there. Scheduled ingestion is handled
    by GitHub Actions in the deployed environment.
    """

    if os.getenv("VERCEL") == "1":
        print("Government job ingestion scheduler disabled on Vercel.")
        return

    if scheduler.running:
        return

    # Start the scheduler before the first ingestion so a slow/unavailable
    # government source can never block FastAPI startup or health checks.
    scheduler.start()

    # Queue the first ingestion immediately on the scheduler's worker thread.
    scheduler.add_job(
        scheduled_ingestion,
        "date",
        run_date=datetime.now(),
        id="government_job_ingestion_initial",
        replace_existing=True,
    )

    # Continue checking every 30 minutes.
    scheduler.add_job(
        scheduled_ingestion,
        "interval",
        minutes=30,
        id="government_job_ingestion",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    print(
        "Government job ingestion scheduler started."
    )


def stop_scheduler() -> None:
    """
    Stop the background ingestion scheduler.
    """

    if not scheduler.running:
        return

    scheduler.shutdown(
        wait=False
    )

    print(
        "Government job ingestion scheduler stopped."
    )