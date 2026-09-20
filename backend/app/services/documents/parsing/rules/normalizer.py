import re

from app.services.documents.parsing.notification_parser import (
    ParsedNotification,
)

from app.services.documents.parsing.rules.models import (
    EligibilityRule,
    EligibilityRuleGroup,
    NormalizedEligibility,
)


class EligibilityNormalizer:
    """
    Converts parsed notification fields into a
    machine-readable eligibility rule tree.

    This class extracts requirements only.
    It does NOT decide candidate eligibility.
    """

    def normalize(
        self,
        parsed: ParsedNotification,
    ) -> NormalizedEligibility:

        result = NormalizedEligibility()

        self._normalize_age(parsed, result)
        self._normalize_service(parsed, result)
        self._normalize_qualification(parsed, result)
        self._normalize_experience(parsed, result)
        self._normalize_department(parsed, result)
        self._normalize_special(parsed, result)
        self._normalize_pay(parsed, result)

        return result

    # =================================================
    # AGE
    # =================================================

    def _normalize_age(
        self,
        parsed: ParsedNotification,
        result: NormalizedEligibility,
    ) -> None:

        if parsed.minimum_age.value is not None:
            result.age_rules.append(
                EligibilityRule(
                    rule_type="MINIMUM_AGE",
                    value=parsed.minimum_age.value,
                    confidence=parsed.minimum_age.confidence,
                    evidence=self._short_evidence(
                        parsed.minimum_age.evidence
                    ),
                )
            )

        if parsed.maximum_age.value is not None:
            result.age_rules.append(
                EligibilityRule(
                    rule_type="MAXIMUM_AGE",
                    value=parsed.maximum_age.value,
                    confidence=parsed.maximum_age.confidence,
                    evidence=self._short_evidence(
                        parsed.maximum_age.evidence
                    ),
                )
            )

    # =================================================
    # SERVICE
    # =================================================

    def _normalize_service(
        self,
        parsed: ParsedNotification,
        result: NormalizedEligibility,
    ) -> None:

        rules = []

        if (
            parsed.requires_government_service.value
            is True
        ):
            rules.append(
                EligibilityRule(
                    rule_type="GOVERNMENT_SERVICE_REQUIRED",
                    value=True,
                    confidence=(
                        parsed.requires_government_service.confidence
                    ),
                    evidence=self._short_evidence(
                        parsed.requires_government_service.evidence
                    ),
                )
            )

        service_text = parsed.service_requirement.value

        if not service_text:
            result.service_rules.extend(rules)
            return

        text = str(service_text)
        lower_text = text.lower()

        analogous_rule = None

        if "holding analogous posts" in lower_text:
            analogous_rule = EligibilityRule(
                rule_type="ANALOGOUS_POST_REQUIRED",
                value=True,
                confidence="high",
                evidence=self._short_evidence(
                    self._extract_context(
                        text,
                        "holding analogous posts",
                    )
                ),
            )

        service_years_rule = None

        years_match = re.search(
            r"(\d+)\s+years[’']?\s+service",
            text,
            flags=re.IGNORECASE,
        )

        if years_match:
            service_years_rule = EligibilityRule(
                rule_type="MINIMUM_SERVICE_YEARS",
                value=int(years_match.group(1)),
                confidence="high",
                evidence=self._short_evidence(
                    self._extract_context(
                        text,
                        years_match.group(0),
                    )
                ),
            )

        pay_level_rule = None

        pay_match = re.search(
            r"Pay Level[-\s]*(\d+)",
            text,
            flags=re.IGNORECASE,
        )

        if pay_match:
            pay_level_rule = EligibilityRule(
                rule_type="MINIMUM_SERVICE_PAY_LEVEL",
                value=int(pay_match.group(1)),
                confidence="high",
                evidence=self._short_evidence(
                    self._extract_context(
                        text,
                        pay_match.group(0),
                    )
                ),
            )

        alternatives = []

        if analogous_rule is not None:
            alternatives.append(
                analogous_rule
            )

        service_path = []

        if service_years_rule is not None:
            service_path.append(
                service_years_rule
            )

        if pay_level_rule is not None:
            service_path.append(
                pay_level_rule
            )

        if len(service_path) == 1:
            alternatives.append(
                service_path[0]
            )

        elif len(service_path) > 1:
            alternatives.append(
                EligibilityRuleGroup(
                    operator="AND",
                    rules=service_path,
                )
            )

        if len(alternatives) >= 2:
            rules.append(
                EligibilityRuleGroup(
                    operator="OR",
                    rules=alternatives,
                )
            )

        else:
            rules.extend(alternatives)

        result.service_rules.extend(rules)

    # =================================================
    # QUALIFICATION
    # =================================================

    def _normalize_qualification(
        self,
        parsed: ParsedNotification,
        result: NormalizedEligibility,
    ) -> None:

        qualification = parsed.qualification_text.value

        if not qualification:
            return

        text = str(qualification)

        # Normalize OCR whitespace.
        normalized_text = re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

        lower_text = normalized_text.lower()

        alternatives = []

        # ---------------------------------------------
        # QUALIFYING EXAMINATION
        # ---------------------------------------------

        if (
            "subordinate accounts services"
            in lower_text
        ):
            alternatives.append(
                EligibilityRule(
                    rule_type="QUALIFYING_EXAMINATION",
                    value=(
                        "Subordinate Accounts Services "
                        "or equivalent examination"
                    ),
                    confidence="high",
                    evidence=self._short_evidence(
                        self._extract_context(
                            normalized_text,
                            "Subordinate Accounts Services",
                        )
                    ),
                )
            )

        # ---------------------------------------------
        # REQUIRED TRAINING
        # ---------------------------------------------

        if (
            "successful completion of training"
            in lower_text
        ):
            training_value = (
                "Cash and Accounts Work training"
            )

            if "istm" in lower_text:
                training_value += (
                    " at ISTM or equivalent"
                )

            alternatives.append(
                EligibilityRule(
                    rule_type="REQUIRED_TRAINING",
                    value=training_value,
                    confidence="high",
                    evidence=self._short_evidence(
                        self._extract_context(
                            normalized_text,
                            "Successful completion of training",
                        )
                    ),
                )
            )

        # ---------------------------------------------
        # EXPERIENCE
        #
        # Handles:
        #
        # 5 years' experience in Cash, Accounts
        # and Budget work.
        #
        # Also handles OCR variants such as:
        #
        # 5 years experience in...
        # Five years' experience in...
        # ---------------------------------------------

        experience_years = None
        experience_evidence = None

        numeric_match = re.search(
            r"(\d+)\s*years?"
            r"\s*['’]?\s*"
            r"experience"
            r"(?:\s+(?:in|of))?"
            r"\s*"
            r"(.{0,300})",
            normalized_text,
            flags=re.IGNORECASE,
        )

        if numeric_match:
            experience_years = int(
                numeric_match.group(1)
            )

            experience_evidence = (
                numeric_match.group(0)
            )

        else:
            word_numbers = {
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
            }

            word_pattern = (
                r"\b("
                + "|".join(word_numbers.keys())
                + r")\s*years?"
                r"\s*['’]?\s*"
                r"experience"
                r"(?:\s+(?:in|of))?"
                r"\s*"
                r"(.{0,300})"
            )

            word_match = re.search(
                word_pattern,
                normalized_text,
                flags=re.IGNORECASE,
            )

            if word_match:
                experience_years = word_numbers[
                    word_match.group(1).lower()
                ]

                experience_evidence = (
                    word_match.group(0)
                )

        experience_rule = None

        if experience_years is not None:

            evidence_text = (
                experience_evidence
                or ""
            )

            areas = self._parse_areas(
                evidence_text
            )

            experience_rule = EligibilityRule(
                rule_type=(
                    "MINIMUM_RELEVANT_EXPERIENCE"
                ),
                value={
                    "years": experience_years,
                    "areas": areas,
                },
                confidence="high",
                evidence=self._short_evidence(
                    evidence_text
                ),
            )

        # ---------------------------------------------
        # BUILD QUALIFICATION TREE
        #
        # (EXAM OR TRAINING)
        #
        # AND
        #
        # RELEVANT EXPERIENCE
        # ---------------------------------------------

        qualification_path = None

        if len(alternatives) >= 2:
            qualification_path = (
                EligibilityRuleGroup(
                    operator="OR",
                    rules=alternatives,
                )
            )

        elif len(alternatives) == 1:
            qualification_path = alternatives[0]

        if (
            qualification_path is not None
            and experience_rule is not None
        ):
            result.qualification_rules.append(
                EligibilityRuleGroup(
                    operator="AND",
                    rules=[
                        qualification_path,
                        experience_rule,
                    ],
                )
            )

        elif qualification_path is not None:
            result.qualification_rules.append(
                qualification_path
            )

        elif experience_rule is not None:
            result.qualification_rules.append(
                experience_rule
            )

    # =================================================
    # STANDALONE EXPERIENCE
    # =================================================

    def _normalize_experience(
        self,
        parsed: ParsedNotification,
        result: NormalizedEligibility,
    ) -> None:

        experience = (
            parsed.experience_requirement.value
        )

        if not experience:
            return

        text = str(experience)
        lower_text = text.lower()

        # Detailed Cash/Accounts/Budget experience
        # is already represented in qualification_rules.
        if (
            "cash" in lower_text
            and "accounts" in lower_text
            and "budget" in lower_text
        ):
            return

        match = re.search(
            r"(\d+)\s+years?",
            text,
            flags=re.IGNORECASE,
        )

        if not match:
            return

        result.experience_rules.append(
            EligibilityRule(
                rule_type="MINIMUM_EXPERIENCE_YEARS",
                value=int(
                    match.group(1)
                ),
                confidence="medium",
                evidence=self._short_evidence(
                    text
                ),
            )
        )

    # =================================================
    # DEPARTMENT
    # =================================================

    def _normalize_department(
        self,
        parsed: ParsedNotification,
        result: NormalizedEligibility,
    ) -> None:

        requirement = (
            parsed.department_requirement.value
        )

        if not requirement:
            return

        text = str(requirement)

        if "parent cadre" in text.lower():
            result.department_rules.append(
                EligibilityRule(
                    rule_type="PARENT_CADRE_REQUIRED",
                    value=True,
                    confidence="high",
                    evidence=self._short_evidence(
                        self._extract_context(
                            text,
                            "parent cadre",
                        )
                    ),
                )
            )

    # =================================================
    # SPECIAL REQUIREMENTS
    # =================================================

    def _normalize_special(
        self,
        parsed: ParsedNotification,
        result: NormalizedEligibility,
    ) -> None:

        special = (
            parsed.special_requirements.value
        )

        if not special:
            return

        text = str(special)
        lower_text = text.lower()

        checks = [
            (
                "cadre clearance",
                "CADRE_CLEARANCE",
            ),
            (
                "vigilance clearance",
                "VIGILANCE_CLEARANCE",
            ),
            (
                "apar",
                "APAR_DOCUMENTS",
            ),
            (
                "certificate from the employer",
                "EMPLOYER_CERTIFICATE",
            ),
        ]

        for keyword, rule_type in checks:

            if keyword not in lower_text:
                continue

            result.special_rules.append(
                EligibilityRule(
                    rule_type=rule_type,
                    value=True,
                    confidence="high",
                    evidence=self._short_evidence(
                        self._extract_context(
                            text,
                            keyword,
                        )
                    ),
                )
            )

    # =================================================
    # PAY
    # =================================================

    def _normalize_pay(
        self,
        parsed: ParsedNotification,
        result: NormalizedEligibility,
    ) -> None:

        if not parsed.pay_level.value:
            return

        match = re.search(
            r"(\d+)",
            str(
                parsed.pay_level.value
            ),
        )

        if not match:
            return

        result.pay_rules.append(
            EligibilityRule(
                rule_type="PAY_LEVEL",
                value=int(
                    match.group(1)
                ),
                confidence=(
                    parsed.pay_level.confidence
                ),
                evidence=self._short_evidence(
                    parsed.pay_level.evidence
                ),
            )
        )

    # =================================================
    # UTILITIES
    # =================================================

    @staticmethod
    def _extract_context(
        text: str,
        keyword: str,
        before: int = 60,
        after: int = 220,
    ) -> str:

        lower_text = text.lower()

        index = lower_text.find(
            keyword.lower()
        )

        if index == -1:
            return text[:300]

        start = max(
            0,
            index - before,
        )

        end = min(
            len(text),
            index + len(keyword) + after,
        )

        return text[start:end]

    @staticmethod
    def _short_evidence(
        evidence: str | None,
        max_length: int = 320,
    ) -> str | None:

        if not evidence:
            return None

        cleaned = re.sub(
            r"\s+",
            " ",
            evidence,
        ).strip()

        if len(cleaned) <= max_length:
            return cleaned

        return (
            cleaned[: max_length - 3]
            + "..."
        )

    @staticmethod
    def _parse_areas(
        text: str,
    ) -> list[str]:

        lower = text.lower()

        areas = []

        if "cash" in lower:
            areas.append("Cash")

        if "accounts" in lower:
            areas.append("Accounts")

        if "budget" in lower:
            areas.append("Budget")

        return areas