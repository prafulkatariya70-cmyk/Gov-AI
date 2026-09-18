import React from "react";
import { View, Text, Pressable, Linking } from "react-native";
import { useRouter } from "expo-router";
import { Job } from "@/src/types";
import { useTheme, makeStyles } from "@/src/theme";
import { MatchScoreBadge } from "./MatchScoreBadge";
import {
  Building2,
  Calendar,
  IndianRupee,
  GraduationCap,
  Bookmark,
  ExternalLink,
  ChevronRight,
  Clock,
  MapPin,
  Sparkles,
} from "lucide-react-native";

interface Props {
  job: Job;
  isBookmarked?: boolean;
  onToggleBookmark?: (job: Job) => void;
  showMatchBreakdown?: boolean;
  testIDPrefix?: string;
}

export const JobCard: React.FC<Props> = ({
  job,
  isBookmarked = false,
  onToggleBookmark,
  showMatchBreakdown = false,
  testIDPrefix = "job-card",
}) => {
  const router = useRouter();
  const { colors } = useTheme();
  const styles = useStyles();

  const matchInfo = job.match_info;
  const matchScore = matchInfo?.match_percentage ?? 75;

  const handlePress = () => {
    router.push({
      pathname: "/job/[id]",
      params: { id: job.id },
    });
  };

  const handleDirectApply = (e: any) => {
    e.stopPropagation();
    if (job.official_apply_url) {
      Linking.openURL(job.official_apply_url).catch((err) =>
        console.error("Failed opening apply URL", err)
      );
    }
  };

  const handleBookmarkPress = (e: any) => {
    e.stopPropagation();
    onToggleBookmark?.(job);
  };

  return (
    <Pressable
      testID={`${testIDPrefix}-${job.id}`}
      style={({ pressed }) => [
        styles.card,
        pressed && styles.cardPressed,
        job.is_featured && styles.featuredCard,
      ]}
      onPress={handlePress}
    >
      {/* Top Meta Bar */}
      <View style={styles.topMetaRow}>
        <View style={styles.boardBadge}>
          <Building2 size={12} color={colors.brandPrimary} />
          <Text style={styles.boardCodeText}>{job.board_code}</Text>
          <View style={styles.badgeDot} />
          <Text style={styles.jobTypeText}>{job.job_type} Govt</Text>
        </View>

        <View style={styles.topRightActions}>
          <MatchScoreBadge
            score={matchScore}
            size="sm"
            isFullyEligible={matchInfo?.is_fully_eligible}
            testID={`match-badge-${job.id}`}
          />
          {onToggleBookmark && (
            <Pressable
              testID={`bookmark-btn-${job.id}`}
              onPress={handleBookmarkPress}
              hitSlop={8}
              style={[
                styles.iconBtn,
                isBookmarked && { backgroundColor: colors.brandTertiary },
              ]}
            >
              <Bookmark
                size={16}
                color={isBookmarked ? colors.brandPrimary : colors.muted}
                fill={isBookmarked ? colors.brandPrimary : "transparent"}
              />
            </Pressable>
          )}
        </View>
      </View>

      {/* Job Title & Post Name */}
      <Text style={styles.jobTitle} numberOfLines={2}>
        {job.title}
      </Text>
      <Text style={styles.postName} numberOfLines={1}>
        {job.post_name}
      </Text>

      {/* Info Grid (Vacancies, Salary, Location, Qualification) */}
      <View style={styles.infoGrid}>
        <View style={styles.infoPill}>
          <Sparkles size={13} color={colors.brandPrimary} />
          <Text style={styles.infoPillText}>
            <Text style={styles.highlightText}>{job.total_vacancies.toLocaleString("en-IN")}</Text> Posts
          </Text>
        </View>

        <View style={styles.infoPill}>
          <IndianRupee size={13} color={colors.success} />
          <Text style={styles.infoPillText} numberOfLines={1}>
            {job.in_hand_salary.split("+")[0].trim()}
          </Text>
        </View>

        <View style={styles.infoPill}>
          <GraduationCap size={13} color={colors.info} />
          <Text style={styles.infoPillText} numberOfLines={1}>
            {job.qualification_required}
          </Text>
        </View>

        <View style={styles.infoPill}>
          <MapPin size={13} color={colors.muted} />
          <Text style={styles.infoPillText} numberOfLines={1}>
            {job.state}
          </Text>
        </View>
      </View>

      {/* Match Breakdown Callout if Enabled */}
      {showMatchBreakdown && matchInfo && (
        <View style={styles.matchBreakdownBox}>
          <View style={styles.matchItemRow}>
            <Text style={styles.matchItemLabel}>Age Criteria:</Text>
            <Text
              style={[
                styles.matchItemValue,
                { color: matchInfo.age_check.is_eligible ? colors.success : colors.error },
              ]}
            >
              {matchInfo.age_check.is_eligible ? "Eligible" : "Exceeds limit"} ({matchInfo.age_check.candidate_age}y vs {matchInfo.age_check.allowed_range})
            </Text>
          </View>
          <View style={styles.matchItemRow}>
            <Text style={styles.matchItemLabel}>Education:</Text>
            <Text
              style={[
                styles.matchItemValue,
                { color: matchInfo.qualification_check.is_eligible ? colors.success : colors.warning },
              ]}
            >
              {matchInfo.qualification_check.is_eligible ? "Matches degree" : "Requires " + job.qualification_required}
            </Text>
          </View>
        </View>
      )}

      {/* Footer (Deadline & Actions) */}
      <View style={styles.footerRow}>
        <View style={styles.deadlineContainer}>
          <Clock size={13} color={job.is_closing_soon ? colors.error : colors.muted} />
          <Text
            style={[
              styles.deadlineText,
              job.is_closing_soon && { color: colors.error, fontWeight: "700" },
            ]}
          >
            Last Date: {job.last_date}
          </Text>
        </View>

        <View style={styles.actionRow}>
          <Pressable
            testID={`direct-apply-btn-${job.id}`}
            style={styles.applyBtn}
            onPress={handleDirectApply}
          >
            <Text style={styles.applyBtnText}>Direct Apply</Text>
            <ExternalLink size={12} color={colors.onBrandPrimary} />
          </Pressable>

          <View style={styles.detailsChevron}>
            <ChevronRight size={16} color={colors.brandPrimary} />
          </View>
        </View>
      </View>
    </Pressable>
  );
};

const useStyles = makeStyles((colors) => ({
  card: {
    backgroundColor: colors.surfaceSecondary,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 14,
    padding: 14,
    marginBottom: 12,
  },
  cardPressed: {
    opacity: 0.92,
    borderColor: colors.brandPrimary,
  },
  featuredCard: {
    borderColor: colors.brandSecondary,
    borderWidth: 1.5,
  },
  topMetaRow: {
    flexDirection: "row",
    justifyContent: "space-in-between",
    alignItems: "center",
    marginBottom: 8,
  },
  boardBadge: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surfaceTertiary,
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
    gap: 5,
  },
  boardCodeText: {
    fontSize: 11,
    fontWeight: "700",
    color: colors.brandPrimary,
    letterSpacing: 0.3,
  },
  badgeDot: {
    width: 3,
    height: 3,
    borderRadius: 2,
    backgroundColor: colors.muted,
  },
  jobTypeText: {
    fontSize: 11,
    color: colors.onSurfaceSecondary,
    fontWeight: "500",
  },
  topRightActions: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    marginLeft: "auto",
  },
  iconBtn: {
    width: 32,
    height: 32,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  jobTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: colors.onSurface,
    lineHeight: 20,
    marginBottom: 2,
  },
  postName: {
    fontSize: 12,
    color: colors.muted,
    marginBottom: 10,
    fontWeight: "500",
  },
  infoGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
    marginBottom: 10,
  },
  infoPill: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    gap: 4,
    maxWidth: "48%",
  },
  infoPillText: {
    fontSize: 11,
    color: colors.onSurfaceSecondary,
    fontWeight: "500",
  },
  highlightText: {
    fontWeight: "700",
    color: colors.brandPrimary,
  },
  matchBreakdownBox: {
    backgroundColor: colors.surfaceTertiary,
    borderRadius: 8,
    padding: 8,
    marginBottom: 10,
    gap: 4,
  },
  matchItemRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  matchItemLabel: {
    fontSize: 11,
    color: colors.muted,
    fontWeight: "600",
  },
  matchItemValue: {
    fontSize: 11,
    fontWeight: "700",
  },
  footerRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: colors.divider,
  },
  deadlineContainer: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    flex: 1,
  },
  deadlineText: {
    fontSize: 11,
    color: colors.muted,
    fontWeight: "500",
  },
  actionRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  applyBtn: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.brandPrimary,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 6,
    gap: 4,
  },
  applyBtnText: {
    fontSize: 11,
    fontWeight: "700",
    color: colors.onBrandPrimary,
  },
  detailsChevron: {
    width: 24,
    height: 24,
    alignItems: "center",
    justifyContent: "center",
  },
}));
