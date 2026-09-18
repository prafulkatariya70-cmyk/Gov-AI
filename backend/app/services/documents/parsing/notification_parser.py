from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class ParsedField:
    value: object
    evidence: Optional[str] = None
    confidence: str = "low"


@dataclass
class ParsedNotification:
    organization_name: ParsedField
    title: ParsedField
    vacancy_count: ParsedField
    opportunity_type: ParsedField

    minimum_age: ParsedField
    maximum_age: ParsedField

    education_level: ParsedField
    degree: ParsedField
    branch: ParsedField

    minimum_experience_years: ParsedField

    requires_government_service: ParsedField
    service_requirement: ParsedField

    qualification_text: ParsedField
    experience_requirement: ParsedField
    department_requirement: ParsedField
    special_requirements: ParsedField

    pay_level: ParsedField
    salary_text: ParsedField

    application_start: ParsedField
    application_end: ParsedField


class NotificationParser:
    """
    Rule-based parser for Indian government recruitment notifications.

    The parser is intentionally conservative:

    - Avoids guessing when evidence is weak.
    - Keeps evidence alongside extracted values.
    - Separates education level from degree.
    - Separates general experience from government-service conditions.
    - Avoids treating generic words such as "Degree" as a specific degree.
    - Avoids treating ambiguous "MS" occurrences as a degree.
    - Extracts qualification text when possible.
    - Extracts application dates when identifiable.
    """

    # ================================================================
    # PUBLIC API
    # ================================================================

    def parse(self, text: str) -> ParsedNotification:
        text = self._normalize_text(text)

        return ParsedNotification(
            organization_name=self._parse_organization(text),
            title=self._parse_title(text),
            vacancy_count=self._parse_vacancy_count(text),
            opportunity_type=self._parse_opportunity_type(text),

            minimum_age=self._parse_minimum_age(text),
            maximum_age=self._parse_maximum_age(text),

            education_level=self._parse_education_level(text),
            degree=self._parse_degree(text),
            branch=self._parse_branch(text),

            minimum_experience_years=self._parse_minimum_experience(text),

            requires_government_service=(
                self._parse_requires_government_service(text)
            ),
            service_requirement=(
                self._parse_service_requirement(text)
            ),

            qualification_text=(
                self._parse_qualification_text(text)
            ),
            experience_requirement=(
                self._parse_experience_requirement(text)
            ),
            department_requirement=(
                self._parse_department_requirement(text)
            ),
            special_requirements=(
                self._parse_special_requirements(text)
            ),

            pay_level=self._parse_pay_level(text),
            salary_text=self._parse_salary(text),

            application_start=self._parse_application_start(text),
            application_end=self._parse_application_end(text),
        )

    # ================================================================
    # COMMON HELPERS
    # ================================================================

    def _normalize_text(self, text: str) -> str:
        if not text:
            return ""

        replacements = {
            "\xa0": " ",
            "\u2018": "'",
            "\u2019": "'",
            "\u201c": '"',
            "\u201d": '"',
            "\u2013": "-",
            "\u2014": "-",
            "\u2212": "-",
            "\uf0b7": " ",
            "\uf0d8": " ",
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        text = re.sub(
            r"\r\n?",
            "\n",
            text,
        )

        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        text = re.sub(
            r"\n[ \t]*\n+",
            "\n\n",
            text,
        )

        return text.strip()

    def _clean(
        self,
        value: Optional[str],
    ) -> Optional[str]:

        if value is None:
            return None

        value = re.sub(
            r"\s+",
            " ",
            value,
        ).strip()

        value = value.strip(
            " :-;|"
        )

        return value or None

    def _field(
        self,
        value=None,
        evidence: Optional[str] = None,
        confidence: str = "low",
    ) -> ParsedField:

        return ParsedField(
            value=value,
            evidence=self._clean(evidence),
            confidence=confidence,
        )

    def _first_match(
        self,
        text: str,
        patterns: list[str],
        flags: int = re.IGNORECASE,
    ):
        for pattern in patterns:
            match = re.search(
                pattern,
                text,
                flags,
            )

            if match:
                return match

        return None

    # ================================================================
    # DATE HELPERS
    # ================================================================

    def _parse_date(
        self,
        value: str,
    ) -> Optional[date]:

        value = value.strip()

        formats = [
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%d.%m.%Y",
            "%d/%m/%y",
            "%d-%m-%y",
            "%d.%m.%y",
            "%d %B %Y",
            "%d %b %Y",
            "%d-%B-%Y",
            "%d-%b-%Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(
                    value,
                    fmt,
                ).date()
            except (ValueError, AttributeError):
                pass

        return None

    def _extract_date_from_match(
        self,
        match,
    ) -> Optional[date]:

        if not match:
            return None

        for group in match.groups():

            if not group:
                continue

            parsed = self._parse_date(
                group
            )

            if parsed:
                return parsed

        return None

    # ================================================================
    # APPLICATION START
    # ================================================================

    def _parse_application_start(
        self,
        text: str,
    ) -> ParsedField:

        patterns = [
            (
                r"(?:online\s+)?applications?\s+"
                r"(?:will\s+)?(?:be\s+)?"
                r"(?:received|accepted)"
                r".{0,100}?"
                r"(?:from|starting\s+from|start(?:s|ing)?\s+on)"
                r"\s*"
                r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
            ),
            (
                r"opening\s+date\s*[:\-]?\s*"
                r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
            ),
            (
                r"application\s+start(?:s|ing)?\s+date"
                r"\s*[:\-]?\s*"
                r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
            ),
            (
                r"start\s+date\s*[:\-]?\s*"
                r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
            ),
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE | re.DOTALL,
            )

            if not match:
                continue

            parsed = self._extract_date_from_match(
                match
            )

            if parsed:
                return self._field(
                    parsed,
                    match.group(0),
                    "high",
                )

        return self._field()

    # ================================================================
    # APPLICATION END
    # ================================================================

    def _parse_application_end(
        self,
        text: str,
    ) -> ParsedField:

        patterns = [
            (
                r"last\s+date\s+for\s+"
                r"(?:receipt\s+of\s+)?"
                r"(?:applications?|application)"
                r".{0,100}?"
                r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
            ),
            (
                r"last\s+date\s*[:\-]?\s*"
                r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
            ),
            (
                r"closing\s+date\s*[:\-]?\s*"
                r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
            ),
            (
                r"application\s+end(?:s|ing)?\s+date"
                r"\s*[:\-]?\s*"
                r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
            ),
            (
                r"end\s+date\s*[:\-]?\s*"
                r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
            ),
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE | re.DOTALL,
            )

            if not match:
                continue

            parsed = self._extract_date_from_match(
                match
            )

            if parsed:
                return self._field(
                    parsed,
                    match.group(0),
                    "high",
                )

        return self._field()

    # ================================================================
    # ORGANIZATION
    # ================================================================

    def _parse_organization(
        self,
        text: str,
    ) -> ParsedField:

        patterns = [
            r"Staff Selection Commission\s*\(HQ\)",
            r"Union Public Service Commission",
            r"Railway Recruitment Board",
            r"Institute of Banking Personnel Selection",
            r"Banking Personnel Selection Institute",
        ]

        match = self._first_match(
            text,
            patterns,
        )

        if match:

            value = self._clean(
                match.group(0)
            )

            return self._field(
                value,
                match.group(0),
                "high",
            )

        return self._field()

    # ================================================================
    # TITLE
    # ================================================================

    def _parse_title(
        self,
        text: str,
    ) -> ParsedField:

        patterns = [
            (
                r"Filling up\s+\d+\s+"
                r"(?:\([^)]+\)\s+)?"
                r"ex-?Cadre posts of\s+"
                r"(.+?)"
                r"\s+in\s+various"
            ),
            (
                r"Filling up\s+\d+\s+"
                r"(?:\([^)]+\)\s+)?"
                r"ex-?Cadre posts of\s+"
                r"(.+?)"
                r"\s+in\s+Staff Selection Commission"
            ),
            (
                r"posts\s+of\s+"
                r"([A-Za-z][A-Za-z0-9/&().,\- ]+?)"
                r"\s+on\s+(?:deputation|contract)"
            ),
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE | re.DOTALL,
            )

            if not match:
                continue

            value = self._clean(
                match.group(1)
            )

            if not value:
                continue

            value = value.split("\n")[0]
            value = self._clean(value)

            if value:

                return self._field(
                    value,
                    match.group(0),
                    "high",
                )

        return self._field()

    # ================================================================
    # VACANCY
    # ================================================================

    def _parse_vacancy_count(
        self,
        text: str,
    ) -> ParsedField:

        patterns = [
            (
                r"filling up\s+0*(\d+)\s+"
                r"\([^)]+\)\s+"
                r"ex-?Cadre posts"
            ),
            (
                r"filling up\s+0*(\d+)\s+"
                r"(?:\([^)]+\)\s+)?"
                r"posts"
            ),
            (
                r"invites applications for filling up\s+"
                r"0*(\d+)\s+"
                r"\([^)]+\)\s+"
                r"ex-?Cadre posts"
            ),
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE | re.DOTALL,
            )

            if match:

                return self._field(
                    int(match.group(1)),
                    match.group(0),
                    "high",
                )

        match = re.search(
            r"No\.\s+of\s+posts.{0,200}?\b0*(\d+)\b",
            text,
            re.IGNORECASE | re.DOTALL,
        )

        if match:

            return self._field(
                int(match.group(1)),
                match.group(0),
                "medium",
            )

        return self._field()

    # ================================================================
    # OPPORTUNITY TYPE
    # ================================================================

    def _parse_opportunity_type(
        self,
        text: str,
    ) -> ParsedField:

        patterns = [
            (
                r"\bon\s+deputation\s+basis\b",
                "DEPUTATION",
            ),
            (
                r"\bon\s+deputation\b",
                "DEPUTATION",
            ),
            (
                r"\bdeputation\s+basis\b",
                "DEPUTATION",
            ),
            (
                r"\bshort[- ]term\s+contract\b",
                "SHORT_TERM_CONTRACT",
            ),
            (
                r"\bon\s+contract\s+basis\b",
                "CONTRACT",
            ),
            (
                r"\bcontract\s+basis\b",
                "CONTRACT",
            ),
        ]

        for pattern, value in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:

                return self._field(
                    value,
                    match.group(0),
                    "high",
                )

        return self._field()

    # ================================================================
    # AGE
    # ================================================================

    def _parse_minimum_age(
        self,
        text: str,
    ) -> ParsedField:

        patterns = [
            (
                r"minimum age(?: limit)?\s*"
                r"(?:of|is|:)?\s*"
                r"(\d{1,2})\s*years?"
            ),
            (
                r"not less than\s*"
                r"(\d{1,2})\s*years?"
            ),
            (
                r"at least\s*"
                r"(\d{1,2})\s*years?"
            ),
            (
                r"minimum\s+age\s*[:\-]?\s*"
                r"(\d{1,2})"
            ),
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:

                return self._field(
                    int(match.group(1)),
                    match.group(0),
                    "high",
                )

        return self._field()

    # ================================================================
    # MAXIMUM AGE
    # ================================================================

    def _parse_maximum_age(
        self,
        text: str,
    ) -> ParsedField:

        patterns = [
            (
                r"maximum age limit.*?"
                r"not exceed(?:ing)?\s*"
                r"(\d{1,2})\s*years?"
            ),
            (
                r"maximum age.*?"
                r"(\d{1,2})\s*years?"
            ),
            (
                r"not exceeding\s*"
                r"(\d{1,2})\s*years?"
            ),
            (
                r"maximum age.*?"
                r"of\s*(\d{1,2})\s*years?"
            ),
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE | re.DOTALL,
            )

            if match:

                return self._field(
                    int(match.group(1)),
                    match.group(0),
                    "high",
                )

        return self._field()

    # ================================================================
    # EDUCATION LEVEL
    # ================================================================

    def _parse_education_level(
        self,
        text: str,
    ) -> ParsedField:

        """
        Determine the minimum educational level required.

        Priority:

        1. Professional/service-specific qualification
        2. Post-graduation
        3. PhD
        4. Graduation
        5. 12th
        6. 10th

        The parser first looks for qualification-specific sections
        instead of blindly scanning the complete notification.

        Generic "Degree" is never treated as a specific degree.
        """

        # ============================================================
        # QUALIFICATION SECTION EXTRACTION
        # ============================================================

        qualification_text = None

        qualification_section_patterns = [
            (
                r"(?:educational\s+qualification|"
                r"educational\s+qualifications|"
                r"essential\s+qualification|"
                r"essential\s+qualifications|"
                r"minimum\s+educational\s+qualification|"
                r"educational\s+qualification\s+required)"
                r"\s*[:\-]?\s*"
                r"(.{0,1500})"
            ),
            (
                r"(?:possessing\s+the\s+following\s+"
                r"qualifications\s+and\s+experience)"
                r"\s*[:\-]?\s*"
                r"(.{0,1500})"
            ),
            (
                r"\bqualification\s*[:\-]\s*"
                r"(.{0,1500})"
            ),
        ]

        for pattern in qualification_section_patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE | re.DOTALL,
            )

            if match:

                qualification_text = match.group(1)

                qualification_text = (
                    qualification_text[:1500]
                )

                break

        # ============================================================
        # LOCAL SEARCH FUNCTION
        # ============================================================

        def find_in_qualification(
            patterns: list[str],
        ):
            if not qualification_text:
                return None

            for pattern in patterns:

                match = re.search(
                    pattern,
                    qualification_text,
                    re.IGNORECASE,
                )

                if match:
                    return match

            return None

        # ============================================================
        # PROFESSIONAL QUALIFICATION
        # ============================================================

        professional_patterns = [
            (
                r"A\s+pass\s+in\s+the\s+"
                r"Subordinate\s+Accounts\s+Services"
                r"(?:\s+or\s+equivalent\s+examination)?"
            ),
            (
                r"Successful\s+completion\s+of\s+training"
                r"\s+in\s+the\s+Cash\s+and\s+Accounts\s+Work"
                r"(?:\s+in\s+the\s+ISTM\s+or\s+equivalent)?"
            ),
        ]

        match = find_in_qualification(
            professional_patterns
        )

        if match:

            if re.search(
                r"Subordinate\s+Accounts\s+Services",
                match.group(0),
                re.IGNORECASE,
            ):

                return self._field(
                    "PROFESSIONAL_ACCOUNTING_EXAM",
                    match.group(0),
                    "high",
                )

            return self._field(
                "PROFESSIONAL_ACCOUNTING_TRAINING",
                match.group(0),
                "high",
            )

        # ============================================================
        # POSTGRADUATION
        # ============================================================

        postgraduate_patterns = [
            r"\bpost[- ]graduation\b",
            r"\bpostgraduate\b",
            r"\bpost[- ]graduate\b",
            r"\bmaster'?s?\s+degree\b",
            r"\bmaster\s+degree\b",
        ]

        match = find_in_qualification(
            postgraduate_patterns
        )

        if match:

            return self._field(
                "POST_GRADUATION",
                match.group(0),
                "high",
            )

        # ============================================================
        # PHD
        # ============================================================

        phd_patterns = [
            r"\bph\.?\s*d\.?\b",
            r"\bdoctorate\b",
            r"\bdoctoral\s+degree\b",
        ]

        match = find_in_qualification(
            phd_patterns
        )

        if match:

            return self._field(
                "PHD",
                match.group(0),
                "high",
            )

        # ============================================================
        # GRADUATION
        # ============================================================

        graduation_patterns = [
            r"\bgraduation\b",
            r"\bgraduate\b",
            r"\bgraduated\b",

            r"\bbachelor'?s?\s+degree\b",
            r"\bbachelor\s+degree\b",

            r"\bdegree\s+of\s+a\s+recognised\s+university\b",
            r"\bdegree\s+from\s+a\s+recognised\s+university\b",
            r"\bdegree\s+of\s+any\s+recognised\s+university\b",
            r"\bdegree\s+from\s+any\s+recognised\s+university\b",

            r"\bdegree\s+of\s+a\s+recognized\s+university\b",
            r"\bdegree\s+from\s+a\s+recognized\s+university\b",
            r"\bdegree\s+of\s+any\s+recognized\s+university\b",
            r"\bdegree\s+from\s+any\s+recognized\s+university\b",

            (
                r"\bdegree\s+of\s+a\s+recognised\s+university"
                r"\s+or\s+equivalent\b"
            ),

            (
                r"\bdegree\s+of\s+a\s+recognized\s+university"
                r"\s+or\s+equivalent\b"
            ),

            (
                r"\bdegree\s+from\s+a\s+recognised\s+university"
                r"\s+or\s+equivalent\b"
            ),

            (
                r"\bdegree\s+from\s+a\s+recognized\s+university"
                r"\s+or\s+equivalent\b"
            ),
        ]

        match = find_in_qualification(
            graduation_patterns
        )

        if match:

            return self._field(
                "GRADUATION",
                match.group(0),
                "high",
            )

        # ============================================================
        # 12TH
        # ============================================================

        twelfth_patterns = [
            r"\b12th\b",
            r"\bhigher\s+secondary\b",
            r"\bintermediate\b",
            r"\b10\s*\+\s*2\b",
            r"\bhigher\s+secondary\s+school\b",
        ]

        match = find_in_qualification(
            twelfth_patterns
        )

        if match:

            return self._field(
                "12TH",
                match.group(0),
                "high",
            )

        # ============================================================
        # 10TH
        # ============================================================

        tenth_patterns = [
            r"\b10th\b",
            r"\bmatriculation\b",
            r"\bmatric\b",
            r"\bsecondary\s+school\b",
            r"\bsecondary\s+education\b",
        ]

        match = find_in_qualification(
            tenth_patterns
        )

        if match:

            return self._field(
                "10TH",
                match.group(0),
                "high",
            )

        # ============================================================
        # FALLBACK: WHOLE NOTIFICATION
        # ============================================================

        match = self._first_match(
            text,
            professional_patterns,
        )

        if match:

            if re.search(
                r"Subordinate\s+Accounts\s+Services",
                match.group(0),
                re.IGNORECASE,
            ):

                return self._field(
                    "PROFESSIONAL_ACCOUNTING_EXAM",
                    match.group(0),
                    "high",
                )

            return self._field(
                "PROFESSIONAL_ACCOUNTING_TRAINING",
                match.group(0),