import React, { useState } from "react";
import {
  View,
  Text,
  ScrollView,
  Pressable,
  ActivityIndicator,
  Linking,
  Share,
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/src/api/apiClient";
import { useTheme, makeStyles } from "@/src/theme";
import { MatchScoreBadge } from "@/src/components/MatchScoreBadge";
import { OfficialNotificationModal } from "@/src/components/OfficialNotificationModal";
import {
  ArrowLeft,
  Share2,
  Bookmark,
  ExternalLink,
  Building2,
  Calendar,
  IndianRupee,
  GraduationCap,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  FileText,
  Clock,
  MapPin,
  Users,
  Layers,
  ChevronRight,
  Info,
} from "lucide-react-native";

export default function JobDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { colors } = useTheme();
  const styles = useStyles();
  const queryClient = useQueryClient();

  const [notificationModalVisible, setNotificationModalVisible] = useState(false);

  const {
    data: job,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["job-detail", id],
    queryFn: () => api.getJobDetail(id as string),
    enabled: !!id,
  });

  const { data: trackerData } = useQuery({
    queryKey: ["tracker"],
    queryFn: () => api.getTracker(),
  });

  // Check if job is tracked
  const isBookmarked =
    trackerData?.saved.some((t) => t.job_id === job?.id) ||
    trackerData?.applied.some((t) => t.job_id === job?.id);

  const isApplied = trackerData?.applied.some((t) => t.job_id === job?.id);

  const trackerMutation = useMutation({
    mutationFn: ({ status }: { status: string }) =>
      api.updateTrackerItem({ job_id: job!.id, status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tracker"] });
      queryClient.invalidateQueries({ queryKey: ["job-detail", id] });
    },
  });

  const removeTrackerMutation = useMutation({
    mutationFn: () => api.removeFromTracker(job!.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tracker"] });
      queryClient.invalidateQueries({ queryKey: ["job-detail", id] });
    },
  });

  const handleShare = async () => {
    if (!job) return;
    try {
      await Share.share({
        title: job.title,
        message: `📢 ${job.title}\n\n🏛 Board: ${job.board}\n🎯 Total Vacancies: ${job.total_vacancies}\n💰 Salary: ${job.salary_scale}\n⏳ Last Date to Apply: ${job.last_date}\n\nApply Directly on official portal: ${job.official_apply_url}\n\nView details on SarkariSeva AI App.`,
      });
    } catch (error) {
      console.error("Error sharing job", error);
    }
  };

  const handleDirectApply = () => {
    if (job?.official_apply_url) {
      Linking.openURL(job.official_apply_url).catch((err) =>
        console.error("Failed to open apply link", err)
      );
    }
  };

  const matchInfo = job?.match_info;
  const matchScore = matchInfo?.match_percentage ?? 75;

  if (isLoading) {
    return (
      <View style={[styles.screen, styles.centerContainer, { paddingTop: insets.top }]}>
        <ActivityIndicator size="large" color={colors.brandPrimary} />
        <Text style={styles.loadingText}>Fetching official gazette & syllabus details...</Text>
      </View>
    );
  }

  if (!job) {
    return (
      <View style={[styles.screen, styles.centerContainer, { paddingTop: insets.top }]}>
        <AlertTriangle size={36} color={colors.error} />
        <Text style={styles.errorTitle}>Job Listing Not Found</Text>
        <Text style={styles.errorSub}>The notification may have expired or was removed.</Text>
        <Pressable
          testID="back-to-feed-btn"
          style={styles.backBtn}
          onPress={() => router.back()}
        >
          <Text style={styles.backBtnText}>Back to Feed</Text>
        </Pressable>
      </View>
    );
  }

  return (
    <View style={[styles.screen, { paddingTop: insets.top }]}>
      {/* Sticky Top Header */}
      <View style={styles.topHeader}>
        <Pressable
          testID="job-detail-back-btn"
          style={styles.headerIconBtn}
          onPress={() => router.back()}
          hitSlop={8}
        >
          <ArrowLeft size={18} color={colors.onSurface} />
        </Pressable>

        <Text style={styles.headerTitleText} numberOfLines={1}>
          {job.board_code} Notice
        </Text>

        <View style={styles.headerRightActions}>
          <Pressable
            testID="job-detail-share-btn"
            style={styles.headerIconBtn}
            onPress={handleShare}
            hitSlop={8}
          >
            <Share2 size={17} color={colors.onSurface} />
          </Pressable>

          <Pressable
            testID="job-detail-bookmark-btn"
            style={[
              styles.headerIconBtn,
              isBookmarked && { backgroundColor: colors.brandTertiary },
            ]}
            onPress={() => {
              if (isBookmarked) {
                removeTrackerMutation.mutate();
              } else {
                trackerMutation.mutate({ status: "saved" });
              }
            }}
            hitSlop={8}
          >
            <Bookmark
              size={17}
              color={isBookmarked ? colors.brandPrimary : colors.onSurface}
              fill={isBookmarked ? colors.brandPrimary : "transparent"}
            />
          </Pressable>
        </View>
      </View>

      {/* Main Scroll Content */}
      <ScrollView
        contentContainerStyle={[styles.scrollContent, { paddingBottom: 100 }]}
        showsVerticalScrollIndicator={false}
      >
        {/* Board Seal Hero Card */}
        <View style={styles.heroCard}>
          <View style={styles.boardSealRow}>
            <View style={styles.boardIconBox}>
              <Building2 size={24} color={colors.brandPrimary} />
            </View>
            <View style={{ flex: 1 }}>
              <View style={styles.typeBadgeRow}>
                <View style={styles.typeBadge}>
                  <Text style={styles.typeBadgeText}>{job.job_type} Government</Text>
                </View>
                <View style={styles.categoryBadge}>
                  <Text style={styles.categoryBadgeText}>{job.category}</Text>
                </View>
              </View>
              <Text style={styles.boardNameText}>{job.board}</Text>
            </View>
          </View>

          <Text style={styles.jobTitle}>{job.title}</Text>
          <Text style={styles.postNameText}>🎯 Post: {job.post_name}</Text>

          {/* Quick Metrics Bar */}
          <View style={styles.metricsBar}>
            <View style={styles.metricItem}>
              <Text style={styles.metricLabel}>Total Posts</Text>
              <Text style={styles.metricVal}>
                {job.total_vacancies.toLocaleString("en-IN")}
              </Text>
            </View>
            <View style={styles.metricDivider} />
            <View style={styles.metricItem}>
              <Text style={styles.metricLabel}>In-Hand Salary</Text>
              <Text style={styles.metricVal}>
                {job.in_hand_salary.split("+")[0].trim()}
              </Text>
            </View>
            <View style={styles.metricDivider} />
            <View style={styles.metricItem}>
              <Text style={styles.metricLabel}>Closing Date</Text>
              <Text
                style={[
                  styles.metricVal,
                  job.is_closing_soon && { color: colors.error },
                ]}
              >
                {job.last_date}
              </Text>
            </View>
          </View>
        </View>

        {/* Smart Eligibility Matcher Breakdown Card */}
        {matchInfo && (
          <View testID="match-breakdown-card" style={styles.matchCard}>
            <View style={styles.matchCardHeader}>
              <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
                <Sparkles size={18} color={colors.brandPrimary} />
                <Text style={styles.matchCardTitle}>Your Eligibility Match</Text>
              </View>
              <MatchScoreBadge score={matchScore} size="md" isFullyEligible={matchInfo.is_fully_eligible} />
            </View>

            {/* Breakdown checks */}
            <View style={styles.criteriaList}>
              {/* Age check */}
              <View style={styles.criteriaItem}>
                {matchInfo.age_check.is_eligible ? (
                  <CheckCircle2 size={16} color="#15803D" />
                ) : (
                  <XCircle size={16} color="#B91C1C" />
                )}
                <View style={{ flex: 1 }}>
                  <Text style={styles.criteriaName}>Age Criterion</Text>
                  <Text style={styles.criteriaSub}>
                    Your age: {matchInfo.age_check.candidate_age}y (Allowed: {matchInfo.age_check.allowed_range} with {matchInfo.age_check.category} relaxation of +{matchInfo.age_check.category_relaxation_years}y)
                  </Text>
                </View>
              </View>

              {/* Qualification check */}
              <View style={styles.criteriaItem}>
                {matchInfo.qualification_check.is_eligible ? (
                  <CheckCircle2 size={16} color="#15803D" />
                ) : (
                  <AlertTriangle size={16} color="#B45309" />
                )}
                <View style={{ flex: 1 }}>
                  <Text style={styles.criteriaName}>Educational Qualification</Text>
                  <Text style={styles.criteriaSub}>
                    Required: {job.qualification_required} (Your profile: {matchInfo.qualification_check.candidate_qualification})
                  </Text>
                </View>
              </View>

              {/* Domicile check */}
              <View style={styles.criteriaItem}>
                <CheckCircle2 size={16} color="#15803D" />
                <View style={{ flex: 1 }}>
                  <Text style={styles.criteriaName}>Domicile & Quota</Text>
                  <Text style={styles.criteriaSub}>
                    {job.domicile_rule} ({matchInfo.domicile_check.candidate_domicile})
                  </Text>
                </View>
              </View>
            </View>
          </View>
        )}

        {/* Vacancies Breakdown Table */}
        {job.vacancies_breakdown && (
          <View style={styles.sectionCard}>
            <View style={styles.sectionHeaderRow}>
              <Users size={16} color={colors.brandPrimary} />
              <Text style={styles.sectionTitle}>Category-wise Vacancies</Text>
            </View>
            <View style={styles.vacancyTable}>
              {Object.entries(job.vacancies_breakdown).map(([category, count]) => (
                <View key={category} style={styles.tableCell}>
                  <Text style={styles.tableCatLabel}>{category}</Text>
                  <Text style={styles.tableCatCount}>
                    {Number(count).toLocaleString("en-IN")}
                  </Text>
                </View>
              ))}
            </View>
          </View>
        )}

        {/* Crucial Schedule & Timeline */}
        <View style={styles.sectionCard}>
          <View style={styles.sectionHeaderRow}>
            <Calendar size={16} color={colors.brandPrimary} />
            <Text style={styles.sectionTitle}>Key Examination Dates</Text>
          </View>

          <View style={styles.timelineList}>
            <View style={styles.timelineItem}>
              <View style={styles.timelineDot} />
              <View style={{ flex: 1 }}>
                <Text style={styles.timelineLabel}>Notification Release</Text>
                <Text style={styles.timelineVal}>{job.notification_date}</Text>
              </View>
            </View>

            <View style={styles.timelineItem}>
              <View style={[styles.timelineDot, { backgroundColor: colors.brandPrimary }]} />
              <View style={{ flex: 1 }}>
                <Text style={styles.timelineLabel}>Application Start Date</Text>
                <Text style={styles.timelineVal}>{job.start_date}</Text>
              </View>
            </View>

            <View style={styles.timelineItem}>
              <View style={[styles.timelineDot, { backgroundColor: colors.error }]} />
              <View style={{ flex: 1 }}>
                <Text style={[styles.timelineLabel, { color: colors.error, fontWeight: "700" }]}>
                  Application Last Date (Deadline)
                </Text>
                <Text style={[styles.timelineVal, { color: colors.error, fontWeight: "700" }]}>
                  {job.last_date}
                </Text>
              </View>
            </View>

            <View style={styles.timelineItem}>
              <View style={[styles.timelineDot, { backgroundColor: colors.info }]} />
              <View style={{ flex: 1 }}>
                <Text style={styles.timelineLabel}>Tentative Exam Date</Text>
                <Text style={styles.timelineVal}>{job.exam_date}</Text>
              </View>
            </View>
          </View>
        </View>

        {/* Salary Scale & Allowances */}
        <View style={styles.sectionCard}>
          <View style={styles.sectionHeaderRow}>
            <IndianRupee size={16} color={colors.success} />
            <Text style={styles.sectionTitle}>Salary Structure & Pay Matrix</Text>
          </View>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Pay Scale:</Text>
            <Text style={styles.infoVal}>{job.salary_scale}</Text>
          </View>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Approx In-Hand:</Text>
            <Text style={[styles.infoVal, { color: colors.success, fontWeight: "700" }]}>
              {job.in_hand_salary}
            </Text>
          </View>
        </View>

        {/* Syllabus Overview & Exam Stages */}
        <View style={styles.sectionCard}>
          <View style={styles.sectionHeaderRow}>
            <Layers size={16} color={colors.brandPrimary} />
            <Text style={styles.sectionTitle}>Exam Pattern & Syllabus</Text>
          </View>
          <Text style={styles.syllabusText}>{job.syllabus_overview}</Text>

          {job.exam_pattern && job.exam_pattern.length > 0 && (
            <View style={styles.stagesList}>
              {job.exam_pattern.map((stage) => (
                <View key={stage.stage_num} style={styles.stageCard}>
                  <View style={styles.stageHeader}>
                    <Text style={styles.stageTitle}>
                      Stage {stage.stage_num}: {stage.name}
                    </Text>
                    {stage.marks ? (
                      <Text style={styles.stageMarksBadge}>{stage.marks} Marks</Text>
                    ) : null}
                  </View>
                  <Text style={styles.stageType}>
                    Format: {stage.type} • Duration: {stage.duration}
                  </Text>
                  <Text style={styles.stageDesc}>{stage.description}</Text>
                </View>
              ))}
            </View>
          )}
        </View>

        {/* Official Documents & Links Hub */}
        <View style={styles.sectionCard}>
          <View style={styles.sectionHeaderRow}>
            <FileText size={16} color={colors.brandPrimary} />
            <Text style={styles.sectionTitle}>Official Documents & Notices</Text>
          </View>

          <Pressable
            testID="read-gazette-modal-btn"
            style={styles.docActionCard}
            onPress={() => setNotificationModalVisible(true)}
          >
            <View style={styles.docIconBox}>
              <FileText size={18} color={colors.brandPrimary} />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.docTitle}>Official Gazette Notification</Text>
              <Text style={styles.docSub}>Read full gazette notice and annexures in-app</Text>
            </View>
            <ChevronRight size={18} color={colors.brandPrimary} />
          </Pressable>

          <Pressable
            testID="open-official-website-btn"
            style={styles.docActionCard}
            onPress={() => {
              if (job.official_website_url) {
                Linking.openURL(job.official_website_url);
              }
            }}
          >
            <View style={styles.docIconBox}>
              <Building2 size={18} color={colors.muted} />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.docTitle}>{job.board_code} Official Portal</Text>
              <Text style={styles.docSub}>{job.official_website_url}</Text>
            </View>
            <ExternalLink size={16} color={colors.muted} />
          </Pressable>
        </View>
      </ScrollView>

      {/* Sticky Bottom Apply Action Bar */}
      <View style={[styles.bottomActionBar, { paddingBottom: Math.max(insets.bottom, 12) }]}>
        <Pressable
          testID="track-status-action-btn"
          style={[
            styles.pipelineBtn,
            isApplied && { backgroundColor: "#DCFCE7", borderColor: "#86EFAC" },
          ]}
          onPress={() => {
            if (isApplied) {
              trackerMutation.mutate({ status: "saved" });
            } else {
              trackerMutation.mutate({ status: "applied" });
            }
          }}
        >
          {isApplied ? (
            <>
              <CheckCircle2 size={16} color="#15803D" />
              <Text style={[styles.pipelineBtnText, { color: "#15803D" }]}>Applied</Text>
            </>
          ) : (
            <>
              <Bookmark size={16} color={colors.onSurface} />
              <Text style={styles.pipelineBtnText}>Mark Applied</Text>
            </>
          )}
        </Pressable>

        <Pressable
          testID="direct-apply-now-btn"
          style={styles.directApplyMainBtn}
          onPress={handleDirectApply}
        >
          <Text style={styles.directApplyMainBtnText}>Direct Apply Online</Text>
          <ExternalLink size={16} color={colors.onBrandPrimary} />
        </Pressable>
      </View>

      {/* Official Notification In-App Modal */}
      <OfficialNotificationModal
        visible={notificationModalVisible}
        onClose={() => setNotificationModalVisible(false)}
        job={job}
      />
    </View>
  );
}

const useStyles = makeStyles((colors) => ({
  screen: {
    flex: 1,
    backgroundColor: colors.surface,
  },
  centerContainer: {
    alignItems: "center",
    justifyContent: "center",
    padding: 20,
    gap: 12,
  },
  loadingText: {
    fontSize: 13,
    color: colors.muted,
  },
  errorTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: colors.onSurface,
  },
  errorSub: {
    fontSize: 13,
    color: colors.muted,
  },
  backBtn: {
    backgroundColor: colors.brandPrimary,
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 8,
    marginTop: 8,
  },
  backBtnText: {
    color: colors.onBrandPrimary,
    fontWeight: "700",
  },
  topHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    backgroundColor: colors.surface,
  },
  headerIconBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: "center",
    justifyContent: "center",
  },
  headerTitleText: {
    fontSize: 15,
    fontWeight: "700",
    color: colors.onSurface,
    flex: 1,
    textAlign: "center",
    marginHorizontal: 8,
  },
  headerRightActions: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  scrollContent: {
    paddingHorizontal: 16,
    paddingTop: 14,
  },
  heroCard: {
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 14,
    padding: 16,
    marginBottom: 12,
  },
  boardSealRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    marginBottom: 10,
  },
  boardIconBox: {
    width: 44,
    height: 44,
    borderRadius: 10,
    backgroundColor: colors.surfaceTertiary,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: colors.border,
  },
  typeBadgeRow: {
    flexDirection: "row",
    gap: 6,
    marginBottom: 2,
  },
  typeBadge: {
    backgroundColor: colors.brandTertiary,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  typeBadgeText: {
    fontSize: 10,
    fontWeight: "700",
    color: colors.onBrandTertiary,
  },
  categoryBadge: {
    backgroundColor: colors.surfaceTertiary,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  categoryBadgeText: {
    fontSize: 10,
    fontWeight: "600",
    color: colors.onSurfaceSecondary,
  },
  boardNameText: {
    fontSize: 13,
    fontWeight: "700",
    color: colors.onSurface,
  },
  jobTitle: {
    fontSize: 17,
    fontWeight: "800",
    color: colors.onSurface,
    lineHeight: 23,
    marginBottom: 4,
  },
  postNameText: {
    fontSize: 13,
    color: colors.muted,
    fontWeight: "600",
    marginBottom: 14,
  },
  metricsBar: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surface,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: colors.border,
    padding: 10,
    justifyContent: "space-between",
  },
  metricItem: {
    flex: 1,
    alignItems: "center",
  },
  metricDivider: {
    width: 1,
    height: 24,
    backgroundColor: colors.divider,
  },
  metricLabel: {
    fontSize: 10,
    color: colors.muted,
    fontWeight: "600",
    marginBottom: 2,
  },
  metricVal: {
    fontSize: 12,
    fontWeight: "700",
    color: colors.onSurface,
  },
  matchCard: {
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1.5,
    borderColor: colors.brandSecondary,
    borderRadius: 14,
    padding: 14,
    marginBottom: 12,
  },
  matchCardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    paddingBottom: 8,
  },
  matchCardTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: colors.onSurface,
  },
  criteriaList: {
    gap: 8,
  },
  criteriaItem: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 8,
  },
  criteriaName: {
    fontSize: 12,
    fontWeight: "700",
    color: colors.onSurface,
  },
  criteriaSub: {
    fontSize: 11,
    color: colors.muted,
    lineHeight: 15,
  },
  sectionCard: {
    backgroundColor: colors.surfaceSecondary,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
  },
  sectionHeaderRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    marginBottom: 10,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: colors.onSurface,
  },
  vacancyTable: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  tableCell: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 8,
    paddingVertical: 6,
    paddingHorizontal: 10,
    alignItems: "center",
    minWidth: 70,
  },
  tableCatLabel: {
    fontSize: 10,
    color: colors.muted,
    fontWeight: "600",
    marginBottom: 2,
  },
  tableCatCount: {
    fontSize: 13,
    fontWeight: "700",
    color: colors.brandPrimary,
  },
  timelineList: {
    gap: 10,
  },
  timelineItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
  timelineDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: colors.muted,
  },
  timelineLabel: {
    fontSize: 11,
    color: colors.muted,
  },
  timelineVal: {
    fontSize: 12,
    fontWeight: "600",
    color: colors.onSurface,
  },
  infoRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginVertical: 4,
  },
  infoLabel: {
    fontSize: 12,
    color: colors.muted,
  },
  infoVal: {
    fontSize: 12,
    color: colors.onSurface,
    fontWeight: "600",
  },
  syllabusText: {
    fontSize: 12,
    color: colors.onSurfaceSecondary,
    lineHeight: 18,
    marginBottom: 10,
  },
  stagesList: {
    gap: 8,
  },
  stageCard: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 8,
    padding: 10,
  },
  stageHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 2,
  },
  stageTitle: {
    fontSize: 12,
    fontWeight: "700",
    color: colors.onSurface,
  },
  stageMarksBadge: {
    fontSize: 11,
    fontWeight: "700",
    color: colors.brandPrimary,
  },
  stageType: {
    fontSize: 10,
    color: colors.muted,
    marginBottom: 4,
  },
  stageDesc: {
    fontSize: 11,
    color: colors.onSurfaceSecondary,
    lineHeight: 15,
  },
  docActionCard: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 10,
    padding: 10,
    gap: 10,
    marginBottom: 8,
  },
  docIconBox: {
    width: 34,
    height: 34,
    borderRadius: 8,
    backgroundColor: colors.surfaceTertiary,
    alignItems: "center",
    justifyContent: "center",
  },
  docTitle: {
    fontSize: 13,
    fontWeight: "700",
    color: colors.onSurface,
  },
  docSub: {
    fontSize: 11,
    color: colors.muted,
  },
  bottomActionBar: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: colors.surface,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    flexDirection: "row",
    paddingHorizontal: 16,
    paddingTop: 10,
    gap: 10,
  },
  pipelineBtn: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    paddingHorizontal: 14,
    gap: 6,
    minHeight: 46,
  },
  pipelineBtnText: {
    fontSize: 13,
    fontWeight: "700",
    color: colors.onSurface,
  },
  directApplyMainBtn: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.brandPrimary,
    borderRadius: 10,
    paddingHorizontal: 16,
    gap: 6,
    minHeight: 46,
  },
  directApplyMainBtnText: {
    fontSize: 14,
    fontWeight: "700",
    color: colors.onBrandPrimary,
  },
}));
