"""Run due government-job ingestion as a one-shot process."""

from app.db.session import SessionLocal
from app.services.ingestion.runner import run_due_sources


def main() -> None:
    db = SessionLocal()
    try:
        results = run_due_sources(db)
        print(f"Sources processed: {len(results)}")
        failed = 0
        for result in results:
            print(
                f"Run {result.id} | Source {result.source_id} | "
                f"Status: {result.status} | Discovered: {result.discovered} | "
                f"Created: {result.created} | Updated: {result.updated} | "
                f"Skipped: {result.skipped} | Failed: {result.failed}"
            )
            if result.status in {"failed", "completed_with_errors"}:
                failed += 1
        if failed:
            raise SystemExit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
