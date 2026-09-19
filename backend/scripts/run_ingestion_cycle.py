from __future__ import annotations

import argparse

from app.core.database import SessionLocal
from app.services.jobs.ingestion_cycle import IngestionCycleService


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one GovCareerAI official-source ingestion cycle.")
    parser.add_argument("--process-limit", type=int, default=10)
    args = parser.parse_args()
    if not 1 <= args.process_limit <= 100:
        parser.error("--process-limit must be between 1 and 100")

    db = SessionLocal()
    try:
        result = IngestionCycleService(db).run(process_limit=args.process_limit)
        print(
            f"sources_checked={result.sources_checked} "
            f"notifications_queued={result.notifications_queued} "
            f"notifications_processed={result.notifications_processed}"
        )
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
