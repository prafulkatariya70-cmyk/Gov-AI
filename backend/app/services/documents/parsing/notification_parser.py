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

        text = re.sub(r"\r\n?", "\n", text)

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

            parsed = self._parse_date(group)

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
                r"applications?\s+(?:are\s+)?invited\s+from\s+"
                r"(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})"
            ),
            (
                r"(?:online\s+)?applications?\s+"
                r"(?:will\s+)?(?:be\s+)?"
                r"(?:received|accepted)"
                r".{0,100}?"
                r"(?:from|starting\s+from|start(?:s|ing)?\s+on)"
                r"\s*"
                r"(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})"
            ),
            (
                r"opening\s+date\s*[:\-]?\s*"
                r"(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})"
            ),
            (
                r"application\s+start(?:s|ing)?\s+date"
                r"\s*[:\-]?\s*"
                r"(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})"
            ),
            (
                r"start\s+date\s*[:\-]?\s*"
                r"(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})"
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

            parsed = self._extract_date_from_match(match)

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
                r"applications?\s+(?:are\s+)?invited\s+from\s+"
                r"\d{1,2}[./-]\d{1,2}[./-]\d{2,4}"
                r".{0,30}?(?:to|till|until)\s*"
                r"(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})"
            ),
            (
                r"(?:online\s+)?applications?\s+"
                r"(?:will\s+)?(?:be\s+)?"
                r"(?:received|accepted)"
                r".{0,100}?"
                r"(?:from|starting\s+from|start(?:s|ing)?\s+on)"
                r"\s*\d{1,2}[./-]\d{1,2}[./-]\d{2,4}"
                r".{0,30}?"
                r"(?:to|till|until)"
                r"\s*"
                r"(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})"
            ),
            (
                r"last\s+date\s+for\s+"
                r"(?:receipt\s+of\s+)?"
                r"(?:applications?|application)"
                r".{0,100}?"
                r"(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})"
            ),
            (
                r"last\s+date\s*[:\-]?\s*"
                r"(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})"
            ),
            (
                r"closing\s+date\s*[:\-]?\s*"
                r"(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})"
            ),
            (
                r"application\s+end(?:s|ing)?\s+date"
                r"\s*[:\-]?\s*"
                r"(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})"
            ),
            (
                r"end\s+date\s*[:\-]?\s*"
                r"(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})"
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

            parsed = self._extract_date_from_match(match)

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
            r"Staff Selection Commission",
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
            (
                r"(?:recruitment\s+to\s+the\s+)?post\s+of\s+"
                r"([^\n.]+)"
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
            (
                r"applications?\s+are\s+invited\s+for\s+"
                r"0*(\d+)\s+posts?"
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
            r"(?:total\s+vacancies?|total\s+number\s+of\s+vacancies?)\s*[:\-]?\s*0*(\d+)\b",
            text,
            re.IGNORECASE,
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
                r"age\s+limit\s*[:\-]?\s*"
                r"(\d{1,2})\s+to\s+\d{1,2}\s*years?"
            ),
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
                r"age\s+limit\s*[:\-]?\s*"
                r"\d{1,2}\s+to\s+(\d{1,2})\s*years?"
            ),
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

                # Prevent unrelated parts of the notification
                # from influencing the education classification.
                qualification_text = qualification_text[:1500]

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
        #
        # IMPORTANT:
        #
        # "Degree of a recognised University"
        # "Degree from a recognised University"
        #
        # means graduation-level qualification.
        #
        # But we DO NOT return:
        #
        #     degree = "Degree"
        #
        # That is handled separately by _parse_degree().
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

            r"\bdegree\s+of\s+a\s+recognised\s+university"
            r"\s+or\s+equivalent\b",

            r"\bdegree\s+of\s+a\s+recognized\s+university"
            r"\s+or\s+equivalent\b",

            r"\bdegree\s+from\s+a\s+recognised\s+university"
            r"\s+or\s+equivalent\b",

            r"\bdegree\s+from\s+a\s+recognized\s+university"
            r"\s+or\s+equivalent\b",
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
        #
        # Only used if no useful qualification section was found.
        # Higher education is checked first.
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
                "high",
            )

        match = self._first_match(
            text,
            postgraduate_patterns,
        )

        if match:

            return self._field(
                "POST_GRADUATION",
                match.group(0),
                "high",
            )

        match = self._first_match(
            text,
            phd_patterns,
        )

        if match:

            return self._field(
                "PHD",
                match.group(0),
                "high",
            )

        match = self._first_match(
            text,
            graduation_patterns,
        )

        if match:

            return self._field(
                "GRADUATION",
                match.group(0),
                "high",
            )

        match = self._first_match(
            text,
            twelfth_patterns,
        )

        if match:

            return self._field(
                "12TH",
                match.group(0),
                "high",
            )

        match = self._first_match(
            text,
            tenth_patterns,
        )

        if match:

            return self._field(
                "10TH",
                match.group(0),
                "high",
            )

        return self._field()

    # ================================================================
    # DEGREE
    # ================================================================

    def _parse_degree(
        self,
        text: str,
    ) -> ParsedField:

        """
        Extract an actual named degree.

        IMPORTANT:

        These must NOT return degree="Degree":

            Degree of a recognised University
            Degree from a recognised University
            Educational Degree

        Generic "Degree" is not a specific degree.
        """

        # ============================================================
        # SPECIFIC ABBREVIATIONS
        # ============================================================

        abbreviation_patterns = [
            r"\bB\.E\.?\b",
            r"\bB\.Tech\.?\b",
            r"\bB\.Sc\.?\b",
            r"\bB\.Com\.?\b",
            r"\bB\.A\.?\b",
            r"\bB\.CA\.?\b",
            r"\bB\.BA\.?\b",
            r"\bB\.Pharm\.?\b",
            r"\bLL\.B\.?\b",
            r"\bB\.Ed\.?\b",
            r"\bB\.Lib\.?\b",

            r"\bM\.E\.?\b",
            r"\bM\.Tech\.?\b",
            r"\bM\.Sc\.?\b",
            r"\bM\.Com\.?\b",
            r"\bM\.A\.?\b",
            r"\bM\.CA\.?\b",
            r"\bMBA\b",
            r"\bMCA\b",
            r"\bLL\.M\.?\b",
            r"\bM\.Ed\.?\b",
            r"\bM\.Lib\.?\b",

            r"\bBDS\b",
            r"\bMBBS\b",
            r"\bMD\b",
            r"\bMDS\b",
            r"\bPh\.D\.?\b",
        ]

        for pattern in abbreviation_patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if not match:
                continue

            value = self._clean(
                match.group(0)
            )

            if not value:
                continue

            return self._field(
                value,
                match.group(0),
                "high",
            )

        # ============================================================
        # M.S. / MS SPECIAL HANDLING
        #
        # Plain "Ms" is commonly an honorific (Ms. Name), so it must
        # never be accepted from the entire notification as a degree.
        # A genuine academic MS is accepted only from qualification
        # text and only when academic context is present nearby.
        # ============================================================

        qualification_field = self._parse_qualification_text(text)
        qualification_text = (
            str(qualification_field.value)
            if qualification_field.value
            else ""
        )

        if qualification_text:

            ms_patterns = [
                r"\bM\.S\.?\b",
                r"\bMS\b",
            ]

            for pattern in ms_patterns:

                for match in re.finditer(
                    pattern,
                    qualification_text,
                    re.IGNORECASE,
                ):

                    start = match.start()
                    end = match.end()

                    nearby = qualification_text[
                        max(0, start - 100):
                        min(len(qualification_text), end + 100)
                    ]

                    if not re.search(
                        r"\b(?:degree|master|science|engineering|"
                        r"technology|qualification|university|college)\b",
                        nearby,
                        re.IGNORECASE,
                    ):
                        continue

                    value = self._clean(match.group(0))

                    if value.lower() == "ms":
                        value = "MS"

                    if value:
                        return self._field(
                            value,
                            match.group(0),
                            "high",
                        )

        # ============================================================
        # FULL DEGREE NAMES
        # ============================================================

        full_name_patterns = [
            (
                r"\bBachelor(?:'s)?\s+of\s+"
                r"(?:Engineering|Technology|Science|Commerce|"
                r"Arts|Computer\s+Applications|Business\s+Administration|"
                r"Pharmacy|Education|Law|Library\s+Science)"
            ),
            (
                r"\bMaster(?:'s)?\s+of\s+"
                r"(?:Engineering|Technology|Science|Commerce|"
                r"Arts|Computer\s+Applications|Business\s+Administration|"
                r"Education|Law|Library\s+Science)"
            ),
        ]

        for pattern in full_name_patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:

                value = self._clean(
                    match.group(0)
                )

                if value:

                    return self._field(
                        value,
                        match.group(0),
                        "high",
                    )

        # ============================================================
        # DEGREE IN SUBJECT
        #
        # Example:
        #
        # Degree in Civil Engineering
        #
        # Return:
        #
        # Civil Engineering
        #
        # NOT:
        #
        # Degree
        # ============================================================

        degree_in_patterns = [
            (
                r"\bdegree\s+in\s+"
                r"([A-Za-z][A-Za-z &/,().\-]{2,100}?)"
                r"(?=\s+(?:from|of|with|and|or|recognized|recognised|"
                r"equivalent|having|possessing)\b|[.;:\n]|$)"
            ),
            (
                r"\bdegree\s+in\s+"
                r"([A-Za-z][A-Za-z &/,().\-]{2,100})"
            ),
        ]

        for pattern in degree_in_patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if not match:
                continue

            subject = self._clean(
                match.group(1)
            )

            if not subject:
                continue

            subject = re.sub(
                r"\s+",
                " ",
                subject,
            )

            return self._field(
                subject,
                match.group(0),
                "medium",
            )

        # ============================================================
        # NO GENERIC DEGREE FALLBACK
        # ============================================================

        return self._field()

    # ================================================================
    # BRANCH
    # ================================================================

    def _parse_branch(
        self,
        text: str,
    ) -> ParsedField:

        patterns = [
            (
                r"\bbranch\s*[:\-]\s*"
                r"([A-Za-z][A-Za-z &/,.\-]{2,80})"
            ),
            (
                r"\bdiscipline\s*[:\-]\s*"
                r"([A-Za-z][A-Za-z &/,.\-]{2,80})"
            ),
            (
                r"\bspecialization\s*[:\-]\s*"
                r"([A-Za-z][A-Za-z &/,.\-]{2,80})"
            ),
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:

                value = self._clean(
                    match.group(1)
                )

                if value:

                    return self._field(
                        value,
                        match.group(0),
                        "medium",
                    )

        return self._field()

    # ================================================================
    # MINIMUM EXPERIENCE
    # ================================================================

    def _parse_minimum_experience(
        self,
        text: str,
    ) -> ParsedField:

        number_words = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10,
            "eleven": 11,
            "twelve": 12,
            "thirteen": 13,
            "fourteen": 14,
            "fifteen": 15,
            "sixteen": 16,
            "seventeen": 17,
            "eighteen": 18,
            "nineteen": 19,
            "twenty": 20,
        }

        numeric_patterns = [
            (
                r"\b(\d+)\s+years?'?\s+"
                r"of\s+experience\b"
            ),
            (
                r"\b(\d+)\s+years?'?\s+"
                r"experience\b"
            ),
        ]

        for pattern in numeric_patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if not match:
                continue

            value = int(
                match.group(1)
            )

            return self._field(
                value,
                match.group(0),
                "high",
            )

        word_pattern = (
            r"\b("
            + "|".join(number_words.keys())
            + r")\s+years?'?\s+"
            r"(?:of\s+)?experience\b"
        )

        match = re.search(
            word_pattern,
            text,
            re.IGNORECASE,
        )

        if match:

            word = match.group(1).lower()
            value = number_words[word]

            return self._field(
                value,
                match.group(0),
                "high",
            )

        return self._field()

    # ================================================================
    # GOVERNMENT SERVICE
    # ================================================================

    def _parse_requires_government_service(
        self,
        text: str,
    ) -> ParsedField:

        patterns = [
            r"Officers under the Central Government",
            r"Officers under the State Government",
            r"Central Government",
            r"State Government",
            r"Government servants",
            r"Government employees",
            r"Govt\.?\s+employees",
            r"Central/State Governments",
            r"experience\s+in\s+government\s+service",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:

                return self._field(
                    True,
                    match.group(0),
                    "high",
                )

        return self._field(
            False,
            None,
            "medium",
        )

    # ================================================================
    # SERVICE REQUIREMENT
    # ================================================================

    def _parse_service_requirement(
        self,
        text: str,
    ) -> ParsedField:

        requirements: list[str] = []

        patterns_a = [
            (
                r"holding\s+analogous\s+posts\s+"
                r"on\s+regular\s+basis\s+"
                r"in\s+the\s+parent\s+cadre\s+or\s+Department"
            ),
            (
                r"holding\s+analogous\s+posts\s+"
                r"on\s+regular\s+basis\s+"
                r"in\s+the\s+parent\s+cadre/department"
            ),
        ]

        for pattern in patterns_a:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:

                value = self._clean(
                    match.group(0)
                )

                if (
                    value
                    and value not in requirements
                ):
                    requirements.append(value)

                break

        patterns_b = [
            (
                r"With\s+\d+\s+years?'?\s+"
                r"service\s+in\s+the\s+grade"
                r".{0,350}?"
                r"parent\s+cadre/department"
            ),
            (
                r"With\s+\d+\s+years?'?\s+"
                r"service\s+in\s+the\s+grade"
                r".{0,350}?"
                r"parent\s+cadre\s+or\s+Department"
            ),
        ]

        for pattern in patterns_b:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE | re.DOTALL,
            )

            if match:

                value = self._clean(
                    match.group(0)
                )

                if (
                    value
                    and value not in requirements
                ):
                    requirements.append(value)

                break

        if not requirements:
            return self._field()

        value = " OR ".join(
            requirements
        )

        return self._field(
            value,
            value,
            "high",
        )

    # ================================================================
    # QUALIFICATION TEXT
    # ================================================================

    def _parse_qualification_text(
        self,
        text: str,
    ) -> ParsedField:

        start_patterns = [
            (
                r"\bb\)\s*"
                r"Possessing\s+the\s+following\s+"
                r"qualifications\s+and\s+experience\s*"
                r":?\s*-?"
            ),
            (
                r"\bPossessing\s+the\s+following\s+"
                r"qualifications\s+and\s+experience\s*"
                r":?\s*-?"
            ),
            (
                r"\bEssential\s+Qualifications?\s*[:\-]?"
            ),
            (
                r"\bESSENTIAL\s+QUALIFICATIONS?\s*[:\-]?"
            ),
        ]

        start_match = None

        for pattern in start_patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:
                start_match = match
                break

        if not start_match:
            return self._field()

        start = start_match.start()

        remaining = text[start:]

        end_patterns = [
            r"\n\s*Note-?\s*1\b",
            r"\n\s*Note\s*1\b",
            r"\n\s*Note-?\s*2\b",
            r"\n\s*Note\s*2\b",
            r"\n\s*DESIRABLE\s+QUALIFICATIONS?\b",
            r"\n\s*ii\s+Last date for receipt",
            r"\n\s*Last date for receipt",
            r"\n\s*ANNEXURE-II\b",
            r"\n\s*AGE\s+LIMIT\b",
            r"\n\s*PAY\s+LEVEL\b",
        ]

        end_positions: list[int] = []

        for pattern in end_patterns:

            match = re.search(
                pattern,
                remaining,
                re.IGNORECASE,
            )

            if match:
                end_positions.append(
                    match.start()
                )

        if end_positions:

            end = min(end_positions)
            block = remaining[:end]

        else:

            block = remaining[:2500]

        block = self._clean(block)

        if not block:
            return self._field()

        block = re.sub(
            r"^b\)\s*",
            "",
            block,
            flags=re.IGNORECASE,
        )

        block = re.sub(
            r"^ESSENTIAL\s+QUALIFICATIONS?\s*[:\-]?\s*",
            "",
            block,
            flags=re.IGNORECASE,
        )

        block = self._clean(block)

        if not block:
            return self._field()

        return self._field(
            block,
            block,
            "high",
        )

    # ================================================================
    # EXPERIENCE REQUIREMENT
    # ================================================================

    def _parse_experience_requirement(
        self,
        text: str,
    ) -> ParsedField:

        patterns = [
            (
                r"\b(\d+)\s+years?'?\s+"
                r"experience\s+in\s+"
                r"Cash,\s*Accounts\s+and\s+Budget\s+work"
            ),
            (
                r"\b(\d+)\s+years?'?\s+"
                r"of\s+experience\s+in\s+"
                r"Cash,\s*Accounts\s+and\s+Budget\s+work"
            ),
            (
                r"\bFive\s+years?'?\s+"
                r"experience\s+in\s+"
                r"Cash,\s*Accounts\s+and\s+Budget\s+work"
            ),
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if not match:
                continue

            value = self._clean(
                match.group(0)
            )

            if value:

                value = re.sub(
                    r"[.;,:]+$",
                    "",
                    value,
                )

                return self._field(
                    value,
                    match.group(0),
                    "high",
                )

        return self._field()

    # ================================================================
    # DEPARTMENT REQUIREMENT
    # ================================================================

    def _parse_department_requirement(
        self,
        text: str,
    ) -> ParsedField:

        patterns = [
            (
                r"holding\s+analogous\s+posts\s+"
                r"on\s+regular\s+basis\s+"
                r"in\s+the\s+parent\s+cadre\s+or\s+Department"
            ),
            (
                r"holding\s+analogous\s+posts\s+"
                r"on\s+regular\s+basis\s+"
                r"in\s+the\s+parent\s+cadre/department"
            ),
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:

                value = self._clean(
                    match.group(0)
                )

                if value:

                    return self._field(
                        value,
                        match.group(0),
                        "high",
                    )

        return self._field()

    # ================================================================
    # SPECIAL REQUIREMENTS
    # ================================================================

    def _parse_special_requirements(
        self,
        text: str,
    ) -> ParsedField:

        requirements: list[str] = []

        checks = [
            (
                r"\bcadre\s+clearance\b",
                "Cadre clearance required",
            ),
            (
                r"\bvigilance\s+clearance\b",
                "Vigilance clearance required",
            ),
            (
                r"\bcopies\s+of\s+APARs\b",
                "Copies of APARs required",
            ),
            (
                r"\bCR\s+Dossier\b"
                r"|\bCR\s+dossier\b"
                r"|\bACRs?\s+for\s+the\s+last\s+5\s+years\b",
                "ACRs/CR dossier documentation required",
            ),
            (
                r"Certificate\s+from\s+the\s+Employer"
                r"|Certificate\s+of\s+Employer",
                "Certificate from Employer required",
            ),
            (
                r"\bthrough\s+proper\s+channel\b",
                "Application must be forwarded through proper channel",
            ),
            (
                r"\bconditional\s+forwarding\b",
                "Conditional forwarding from employer may lead to rejection",
            ),
        ]

        for pattern, label in checks:

            if re.search(
                pattern,
                text,
                re.IGNORECASE,
            ):

                if label not in requirements:
                    requirements.append(label)

        duration_patterns = [
            (
                r"appointment\s+will\s+be\s+made\s+"
                r"on\s+deputation\s+basis\s+initially\s+"
                r"for\s+a\s+period\s+of\s+(\d+)\s+years?"
            ),
            (
                r"deputation\s+basis\s+initially\s+"
                r"for\s+a\s+period\s+of\s+(\d+)\s+years?"
            ),
        ]

        for pattern in duration_patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:

                label = (
                    f"Initial deputation period: "
                    f"{match.group(1)} years"
                )

                if label not in requirements:
                    requirements.append(label)

                break

        if re.search(
            r"within\s+2\s+months\s+from\s+the\s+date\s+"
            r"of\s+publication\s+of\s+the\s+advertisement",
            text,
            re.IGNORECASE,
        ):

            label = (
                "Application deadline: within 2 months "
                "from publication in Employment News"
            )

            if label not in requirements:
                requirements.append(label)

        maximum_age_match = re.search(
            r"maximum\s+age\s+limit.*?"
            r"not\s+exceed.*?(\d{1,3})\s+years",
            text,
            re.IGNORECASE | re.DOTALL,
        )

        if maximum_age_match:

            label = (
                f"Maximum age: "
                f"{maximum_age_match.group(1)} years"
            )

            if label not in requirements:
                requirements.append(label)

        if not requirements:
            return self._field()

        value = "; ".join(
            requirements
        )

        return self._field(
            value,
            value,
            "high",
        )

    # ================================================================
    # PAY LEVEL
    # ================================================================

    def _parse_pay_level(
        self,
        text: str,
    ) -> ParsedField:

        patterns = [
            r"\bPay\s+Level[- ]?(\d+)\b",
            r"\bLevel[- ]?(\d+)\s*\(",
        ]

        matches = []
        for pattern in patterns:
            matches.extend(
                re.finditer(
                    pattern,
                    text,
                    re.IGNORECASE,
                )
            )

        if not matches:
            return self._field()

        # If a salary/pay-scale is present, prefer the pay-level mention
        # nearest to it. This avoids confusing a prerequisite such as
        # "Pay Level-6" with the actual post level "Pay Level-7".
        salary_match = re.search(
            r"(?:pay\s*(?:scale|matrix)|rs\.?\s*\d)[^\n]{0,120}",
            text,
            re.IGNORECASE,
        )
        if salary_match:
            before_salary = [m for m in matches if m.start() <= salary_match.start()]
            if before_salary:
                match = min(
                    before_salary,
                    key=lambda m: salary_match.start() - m.end(),
                )
            else:
                match = matches[0]
        else:
            # With no salary anchor, retain the final explicit pay-level
            # mention, which is usually the post's own level after any
            # service/prerequisite wording.
            match = max(matches, key=lambda m: m.start())

        return self._field(
            f"Level-{match.group(1)}",
            match.group(0),
            "high",
        )

    # ================================================================
    # SALARY
    # ================================================================

    def _parse_salary(
        self,
        text: str,
    ) -> ParsedField:

        patterns = [
            (
                r"Rs\.?\s*"
                r"([\d,]+\s*-\s*[\d,]+)"
            ),
            (
                r"Rs\.?\s*"
                r"([\d,]+\s*[â€”â€“-]\s*[\d,]+)"
            ),
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if not match:
                continue

            value = self._clean(
                match.group(1)
            )

            if not value:
                continue

            value = re.sub(
                r"\s*[â€”â€“-]\s*",
                " - ",
                value,
            )

            return self._field(
                f"Rs.{value}",
                match.group(0),
                "high",
            )

        return self._field()