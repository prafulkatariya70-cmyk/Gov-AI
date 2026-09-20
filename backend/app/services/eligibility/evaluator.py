from __future__ import annotations

from typing import Iterable

from app.services.documents.parsing.rules.models import (
    EligibilityRule,
    EligibilityRuleGroup,
)

from app.services.eligibility.models import (
    CandidateProfile,
    EligibilityResult,
    RequirementResult,
)


class EligibilityEvaluator:
    """
    Evaluates a CandidateProfile against the normalized
    eligibility rule tree.

    PASS    = requirement is satisfied.
    FAIL    = requirement is definitely not satisfied.
    UNKNOWN = required candidate information is missing.

    Important:

    A child requirement inside a satisfied OR group does
    not independently make the candidate ineligible.

    Example:

        EXAMINATION OR TRAINING

    If examination = PASS and training = FAIL,

    the OR group = PASS.

    The failed training branch is therefore not treated
    as a final eligibility failure.
    """

    def evaluate(
        self,
        candidate: CandidateProfile,
        rules,
    ) -> EligibilityResult:

        results: list[RequirementResult] = []

        # ---------------------------------------------
        # AGE
        # ---------------------------------------------

        results.extend(
            self._evaluate_rules(
                candidate,
                rules.age_rules,
            )
        )

        # ---------------------------------------------
        # SERVICE
        # ---------------------------------------------

        results.extend(
            self._evaluate_rules(
                candidate,
                rules.service_rules,
            )
        )

        # ---------------------------------------------
        # QUALIFICATION
        # ---------------------------------------------

        results.extend(
            self._evaluate_rules(
                candidate,
                rules.qualification_rules,
            )
        )

        # ---------------------------------------------
        # EXPERIENCE
        # ---------------------------------------------

        results.extend(
            self._evaluate_rules(
                candidate,
                rules.experience_rules,
            )
        )

        # ---------------------------------------------
        # DEPARTMENT
        # ---------------------------------------------

        results.extend(
            self._evaluate_rules(
                candidate,
                rules.department_rules,
            )
        )

        # ---------------------------------------------
        # SPECIAL
        # ---------------------------------------------

        results.extend(
            self._evaluate_rules(
                candidate,
                rules.special_rules,
            )
        )

        # ---------------------------------------------
        # PAY
        # ---------------------------------------------

        results.extend(
            self._evaluate_rules(
                candidate,
                rules.pay_rules,
            )
        )

        # ---------------------------------------------
        # EFFECTIVE RESULTS
        # ---------------------------------------------

        failed = self._collect_effective_results(
            results,
            "FAIL",
        )

        unknown = self._collect_effective_results(
            results,
            "UNKNOWN",
        )

        passed = self._collect_effective_results(
            results,
            "PASS",
        )

        # ---------------------------------------------
        # FINAL STATUS
        # ---------------------------------------------

        # No evaluable requirements must never be
        # interpreted as eligibility.
        #
        # Missing/empty eligibility rules require
        # manual review instead.
        if not results:

            status = "NEEDS_REVIEW"

        elif failed:

            status = "NOT_ELIGIBLE"

        elif unknown:

            status = "NEEDS_REVIEW"

        else:

            status = "ELIGIBLE"

        # Empty rules cannot provide high-confidence
        # eligibility information.
        if not results:

            confidence = "medium"

        else:

            confidence = self._calculate_confidence(
                failed,
                unknown,
            )

        reasons = self._build_reasons(
            failed,
            unknown,
        )

        return EligibilityResult(
            status=status,
            confidence=confidence,
            requirements=results,
            passed=passed,
            failed=failed,
            unknown=unknown,
            reasons=reasons,
        )

    # =================================================
    # RULE DISPATCH
    # =================================================

    def _evaluate_rules(
        self,
        candidate: CandidateProfile,
        rules: Iterable,
    ) -> list[RequirementResult]:

        results = []

        for rule in rules:

            results.append(
                self._evaluate_node(
                    candidate,
                    rule,
                )
            )

        return results

    def _evaluate_node(
        self,
        candidate: CandidateProfile,
        node,
    ) -> RequirementResult:

        if isinstance(
            node,
            EligibilityRuleGroup,
        ):

            return self._evaluate_group(
                candidate,
                node,
            )

        if isinstance(
            node,
            EligibilityRule,
        ):

            return self._evaluate_rule(
                candidate,
                node,
            )

        return RequirementResult(
            rule_type="UNKNOWN_RULE",
            status="UNKNOWN",
            reason="Unsupported eligibility rule.",
        )

    # =================================================
    # GROUP EVALUATION
    # =================================================

    def _evaluate_group(
        self,
        candidate: CandidateProfile,
        group: EligibilityRuleGroup,
    ) -> RequirementResult:

        children = [
            self._evaluate_node(
                candidate,
                rule,
            )
            for rule in group.rules
        ]

        statuses = [
            child.status
            for child in children
        ]

        # ---------------------------------------------
        # AND
        # ---------------------------------------------

        if group.operator == "AND":

            if "FAIL" in statuses:

                status = "FAIL"

            elif "UNKNOWN" in statuses:

                status = "UNKNOWN"

            else:

                status = "PASS"

        # ---------------------------------------------
        # OR
        # ---------------------------------------------

        elif group.operator == "OR":

            if "PASS" in statuses:

                status = "PASS"

            elif all(
                item == "FAIL"
                for item in statuses
            ):

                status = "FAIL"

            else:

                status = "UNKNOWN"

        else:

            status = "UNKNOWN"

        return RequirementResult(
            rule_type=f"{group.operator}_GROUP",
            status=status,
            reason=(
                f"{group.operator} eligibility group "
                f"evaluated as {status}."
            ),
            children=children,
        )

    # =================================================
    # EFFECTIVE RESULT COLLECTION
    # =================================================

    def _collect_effective_results(
        self,
        results: Iterable[RequirementResult],
        status: str,
    ) -> list[RequirementResult]:
        """
        Collect only requirements that actually affect
        the final logical result.

        This is different from simply flattening every
        child.

        Example:

            OR
              EXAMINATION = PASS
              TRAINING    = FAIL

        The OR group passes.

        The failed TRAINING branch is therefore ignored
        for final eligibility because it was an optional
        alternative.
        """

        collected: list[RequirementResult] = []

        for result in results:

            if result.rule_type.endswith("_GROUP"):

                self._collect_effective_from_group(
                    result,
                    status,
                    collected,
                )

            else:

                if result.status == status:

                    collected.append(result)

        return collected

    def _collect_effective_from_group(
        self,
        group: RequirementResult,
        status: str,
        collected: list[RequirementResult],
    ) -> None:
        """
        Recursively collect effective failures,
        unknowns, or passes from a logical group.

        For OR groups:

        - PASS means the group is satisfied.
        - Child failures/unknowns are not effective
          eligibility failures.

        For AND groups:

        - Child failures/unknowns remain effective.
        """

        if group.rule_type == "OR_GROUP":

            if group.status == "PASS":

                if status == "PASS":

                    collected.append(group)

                return

            if group.status == "FAIL":

                if status == "FAIL":

                    collected.append(group)

                return

            if group.status == "UNKNOWN":

                if status == "UNKNOWN":

                    collected.append(group)

                return

        # ---------------------------------------------
        # AND GROUP
        # ---------------------------------------------

        if group.rule_type == "AND_GROUP":

            if group.status == status:

                collected.append(group)

            for child in group.children:

                if child.rule_type.endswith("_GROUP"):

                    self._collect_effective_from_group(
                        child,
                        status,
                        collected,
                    )

                elif child.status == status:

                    collected.append(child)

            return

        # ---------------------------------------------
        # UNKNOWN GROUP TYPE
        # ---------------------------------------------

        if group.status == status:

            collected.append(group)

    # =================================================
    # ATOMIC RULE EVALUATION
    # =================================================

    def _evaluate_rule(
        self,
        candidate: CandidateProfile,
        rule: EligibilityRule,
    ) -> RequirementResult:

        rule_type = rule.rule_type
        required = rule.value

        # ---------------------------------------------
        # AGE
        # ---------------------------------------------

        if rule_type == "MINIMUM_AGE":

            return self._compare_numeric(
                rule,
                candidate.age,
                minimum=float(required),
                requirement_label=(
                    f"Age must be at least {required}"
                ),
            )

        if rule_type == "MAXIMUM_AGE":

            return self._compare_numeric(
                rule,
                candidate.age,
                maximum=float(required),
                requirement_label=(
                    f"Age must not exceed {required}"
                ),
            )

        # ---------------------------------------------
        # GOVERNMENT SERVICE
        # ---------------------------------------------

        if rule_type == "GOVERNMENT_SERVICE_REQUIRED":

            return self._compare_boolean(
                rule,
                candidate.government_employee,
                expected=True,
                requirement_label=(
                    "Government service is required"
                ),
            )

        # ---------------------------------------------
        # ANALOGOUS POST
        # ---------------------------------------------

        if rule_type == "ANALOGOUS_POST_REQUIRED":

            return self._compare_boolean(
                rule,
                candidate.analogous_post,
                expected=True,
                requirement_label=(
                    "An analogous post is required"
                ),
            )

        # ---------------------------------------------
        # MINIMUM SERVICE YEARS
        # ---------------------------------------------

        if rule_type == "MINIMUM_SERVICE_YEARS":

            return self._compare_numeric(
                rule,
                candidate.regular_service_years,
                minimum=float(required),
                requirement_label=(
                    f"At least {required} years "
                    f"of qualifying service required"
                ),
            )

        # ---------------------------------------------
        # MINIMUM SERVICE PAY LEVEL
        # ---------------------------------------------

        if rule_type == "MINIMUM_SERVICE_PAY_LEVEL":

            return self._compare_numeric(
                rule,
                candidate.current_pay_level,
                minimum=float(required),
                requirement_label=(
                    f"Pay Level {required} or equivalent "
                    f"is required"
                ),
            )

        # ---------------------------------------------
        # PARENT CADRE
        # ---------------------------------------------

        if rule_type == "PARENT_CADRE_REQUIRED":

            return self._compare_boolean(
                rule,
                candidate.parent_cadre,
                expected=True,
                requirement_label=(
                    "Parent cadre requirement must "
                    "be satisfied"
                ),
            )

        # ---------------------------------------------
        # QUALIFYING EXAMINATION
        # ---------------------------------------------

        if rule_type == "QUALIFYING_EXAMINATION":

            return self._compare_boolean(
                rule,
                candidate.qualifying_examination,
                expected=True,
                requirement_label=(
                    "Required qualifying examination "
                    "must be satisfied"
                ),
            )

        # ---------------------------------------------
        # REQUIRED TRAINING
        # ---------------------------------------------

        if rule_type == "REQUIRED_TRAINING":

            return self._compare_boolean(
                rule,
                candidate.required_training,
                expected=True,
                requirement_label=(
                    "Required training must be completed"
                ),
            )

        # ---------------------------------------------
        # RELEVANT EXPERIENCE
        # ---------------------------------------------

        if rule_type == "MINIMUM_RELEVANT_EXPERIENCE":

            return self._evaluate_relevant_experience(
                candidate,
                rule,
            )

        # ---------------------------------------------
        # STANDALONE EXPERIENCE
        # ---------------------------------------------

        if rule_type == "MINIMUM_EXPERIENCE_YEARS":

            return self._compare_numeric(
                rule,
                candidate.relevant_experience_years,
                minimum=float(required),
                requirement_label=(
                    f"At least {required} years "
                    f"of experience required"
                ),
            )

        # ---------------------------------------------
        # PAY LEVEL
        # ---------------------------------------------

        if rule_type == "PAY_LEVEL":

            return self._compare_numeric(
                rule,
                candidate.current_pay_level,
                minimum=float(required),
                requirement_label=(
                    f"Pay Level {required} or higher required"
                ),
            )

        # ---------------------------------------------
        # DOCUMENT / SPECIAL REQUIREMENTS
        # ---------------------------------------------

        if rule_type in {
            "CADRE_CLEARANCE",
            "VIGILANCE_CLEARANCE",
            "APAR_DOCUMENTS",
            "EMPLOYER_CERTIFICATE",
        }:

            return RequirementResult(
                rule_type=rule_type,
                status="UNKNOWN",
                required=True,
                actual=None,
                reason=(
                    "This document requirement must "
                    "be verified during application."
                ),
                evidence=rule.evidence,
                confidence="medium",
            )

        # ---------------------------------------------
        # UNKNOWN RULE
        # ---------------------------------------------

        return RequirementResult(
            rule_type=rule_type,
            status="UNKNOWN",
            required=required,
            actual=None,
            reason=(
                "No evaluator is currently implemented "
                f"for rule type: {rule_type}"
            ),
            evidence=rule.evidence,
            confidence="low",
        )

    # =================================================
    # RELEVANT EXPERIENCE
    # =================================================

    def _evaluate_relevant_experience(
        self,
        candidate: CandidateProfile,
        rule: EligibilityRule,
    ) -> RequirementResult:

        required = rule.value or {}

        required_years = float(
            required.get(
                "years",
                0,
            )
        )

        required_areas = {
            str(area).lower()
            for area in required.get(
                "areas",
                [],
            )
        }

        if candidate.relevant_experience_years is None:

            return RequirementResult(
                rule_type=rule.rule_type,
                status="UNKNOWN",
                required=required,
                actual=None,
                reason=(
                    "Relevant experience duration "
                    "is unknown."
                ),
                evidence=rule.evidence,
                confidence=rule.confidence,
            )

        actual_areas = {
            str(area).lower()
            for area in candidate.experience_areas
        }

        missing_areas = (
            required_areas
            - actual_areas
        )

        enough_years = (
            candidate.relevant_experience_years
            >= required_years
        )

        if not enough_years:

            return RequirementResult(
                rule_type=rule.rule_type,
                status="FAIL",
                required=required,
                actual={
                    "years": (
                        candidate.relevant_experience_years
                    ),
                    "areas": (
                        candidate.experience_areas
                    ),
                },
                reason=(
                    f"At least {required_years:g} "
                    f"years of relevant experience "
                    f"is required."
                ),
                evidence=rule.evidence,
                confidence=rule.confidence,
            )

        if missing_areas:

            return RequirementResult(
                rule_type=rule.rule_type,
                status="FAIL",
                required=required,
                actual={
                    "years": (
                        candidate.relevant_experience_years
                    ),
                    "areas": (
                        candidate.experience_areas
                    ),
                },
                reason=(
                    "Required experience areas are "
                    f"missing: "
                    f"{', '.join(sorted(missing_areas))}."
                ),
                evidence=rule.evidence,
                confidence=rule.confidence,
            )

        return RequirementResult(
            rule_type=rule.rule_type,
            status="PASS",
            required=required,
            actual={
                "years": (
                    candidate.relevant_experience_years
                ),
                "areas": (
                    candidate.experience_areas
                ),
            },
            reason=(
                "Required relevant experience "
                "is satisfied."
            ),
            evidence=rule.evidence,
            confidence=rule.confidence,
        )

    # =================================================
    # BOOLEAN COMPARISON
    # =================================================

    @staticmethod
    def _compare_boolean(
        rule: EligibilityRule,
        actual: bool | None,
        expected: bool,
        requirement_label: str,
    ) -> RequirementResult:

        if actual is None:

            return RequirementResult(
                rule_type=rule.rule_type,
                status="UNKNOWN",
                required=expected,
                actual=None,
                reason=(
                    f"{requirement_label}, but the "
                    "candidate information is unknown."
                ),
                evidence=rule.evidence,
                confidence=rule.confidence,
            )

        if actual == expected:

            return RequirementResult(
                rule_type=rule.rule_type,
                status="PASS",
                required=expected,
                actual=actual,
                reason=(
                    f"{requirement_label} and the "
                    "candidate satisfies it."
                ),
                evidence=rule.evidence,
                confidence=rule.confidence,
            )

        return RequirementResult(
            rule_type=rule.rule_type,
            status="FAIL",
            required=expected,
            actual=actual,
            reason=(
                f"{requirement_label}, but the "
                "candidate does not satisfy it."
            ),
            evidence=rule.evidence,
            confidence=rule.confidence,
        )

    # =================================================
    # NUMERIC COMPARISON
    # =================================================

    @staticmethod
    def _compare_numeric(
        rule: EligibilityRule,
        actual,
        minimum: float | None = None,
        maximum: float | None = None,
        requirement_label: str = "",
    ) -> RequirementResult:

        if actual is None:

            return RequirementResult(
                rule_type=rule.rule_type,
                status="UNKNOWN",
                required=rule.value,
                actual=None,
                reason=(
                    f"{requirement_label}; candidate "
                    "value is unknown."
                ),
                evidence=rule.evidence,
                confidence=rule.confidence,
            )

        try:

            numeric_actual = float(actual)

        except (
            TypeError,
            ValueError,
        ):

            return RequirementResult(
                rule_type=rule.rule_type,
                status="UNKNOWN",
                required=rule.value,
                actual=actual,
                reason=(
                    "Candidate value could not be "
                    "interpreted as a number."
                ),
                evidence=rule.evidence,
                confidence=rule.confidence,
            )

        if (
            minimum is not None
            and numeric_actual < minimum
        ):

            return RequirementResult(
                rule_type=rule.rule_type,
                status="FAIL",
                required=rule.value,
                actual=actual,
                reason=(
                    f"{requirement_label}; candidate "
                    f"value is {actual}."
                ),
                evidence=rule.evidence,
                confidence=rule.confidence,
            )

        if (
            maximum is not None
            and numeric_actual > maximum
        ):

            return RequirementResult(
                rule_type=rule.rule_type,
                status="FAIL",
                required=rule.value,
                actual=actual,
                reason=(
                    f"{requirement_label}; candidate "
                    f"value is {actual}."
                ),
                evidence=rule.evidence,
                confidence=rule.confidence,
            )

        return RequirementResult(
            rule_type=rule.rule_type,
            status="PASS",
            required=rule.value,
            actual=actual,
            reason=(
                f"{requirement_label}; candidate "
                "value satisfies the requirement."
            ),
            evidence=rule.evidence,
            confidence=rule.confidence,
        )

    # =================================================
    # RESULT HELPERS
    # =================================================

    @staticmethod
    def _calculate_confidence(
        failed: list[RequirementResult],
        unknown: list[RequirementResult],
    ) -> str:

        if failed:

            return "high"

        if unknown:

            return "medium"

        return "high"

    @staticmethod
    def _build_reasons(
        failed: list[RequirementResult],
        unknown: list[RequirementResult],
    ) -> list[str]:

        reasons = []

        for result in failed:

            if result.reason:

                reasons.append(
                    result.reason
                )

        for result in unknown:

            if result.reason:

                reasons.append(
                    result.reason
                )

        return reasons