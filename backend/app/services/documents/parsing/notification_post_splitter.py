from __future__ import annotations

from dataclasses import dataclass
import re

from app.services.documents.parsing.notification_enhancer import NotificationParserEnhancer
from app.services.documents.parsing.notification_parser import ParsedNotification


@dataclass(frozen=True)
class NotificationPostBlock:
    """One conservatively isolated post section from a multi-post advertisement."""

    text: str
    start_offset: int
    end_offset: int
    vacancy_number: str | None
    confidence: str
    reason: str


class NotificationPostSplitter:
    """Split multi-post advertisements only when explicit vacancy boundaries exist."""

    VACANCY_PATTERN = re.compile(
        r"\bVacancy\s+No\.?\s*[:#-]?\s*(\d{8,14})\b",
        re.IGNORECASE,
    )

    def split(self, text: str) -> list[NotificationPostBlock]:
        if not text or not text.strip():
            return []

        matches = list(self.VACANCY_PATTERN.finditer(text))
        if len(matches) < 2:
            return [
                NotificationPostBlock(
                    text=text,
                    start_offset=0,
                    end_offset=len(text),
                    vacancy_number=matches[0].group(1) if matches else None,
                    confidence="low" if not matches else "medium",
                    reason="Fewer than two explicit vacancy boundaries; preserve the source as one block.",
                )
            ]

        blocks: list[NotificationPostBlock] = []
        for index, match in enumerate(matches):
            start = match.start()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            block_text = text[start:end].strip()
            if not block_text:
                continue
            blocks.append(
                NotificationPostBlock(
                    text=block_text,
                    start_offset=start,
                    end_offset=end,
                    vacancy_number=match.group(1),
                    confidence="high",
                    reason="Bounded by explicit Vacancy No. markers.",
                )
            )
        return blocks

    def parse_blocks(self, text: str) -> list[ParsedNotification]:
        """Split and parse each explicit vacancy section independently."""
        parser = NotificationParserEnhancer()
        parsed_blocks: list[ParsedNotification] = []
        for block in self.split(text):
            parsed = parser.parse(block.text)
            parsed_blocks.append(parsed)
        return parsed_blocks
