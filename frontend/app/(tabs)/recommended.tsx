import React, { useState } from "react";
import {
  View,
  Text,
  ScrollView,
  Pressable,
  ActivityIndicator,
  RefreshControl,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/src/api/apiClient";
import { useTheme, makeStyles } from "@/src/theme";
import { JobCard } from "@/src/components/JobCard";
import {
  Sparkles,
  UserCheck,
  Edit3,
  CheckCircle2,
  AlertTriangle,
  GraduationCap,
  MapPin,
  Calendar,
  Shield,
  ArrowRight,
} from "lucide-react-native";

export default function RecommendedScreen() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { colors } = useTheme();
  const styles = useStyles();
  const queryClient = useQueryClient();

  const [activeTab, setActiveTab] = useState<"high_match" | "eligible" | "need_attention">("high_match");

  const {
    data: recData,
    isLoading,
    isRefetching,
    refetch,
  } = useQuery({
    queryKey: ["recommended-jobs"],
    queryFn: () => api.getRecommendedJobs(),
  });

  const { data: trackerData } = useQuery({
    queryKey: ["tracker"],
    queryFn: () => api.getTracker(),
  });

  const bookmarkMutation = useMutation({
    mutationFn: ({ jobId, isBookmarked }: { jobId: string; isBookmarked: boolean }) => {
      if (isBookmarked) {
        return api.removeFromTracker(jobId);
      } else {
        return api.updateTrackerItem({ job_id: jobId, status: "saved" });
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tracker"] });
    },
  });

  const bookmarkedJobIds = new Set<string>();
  if (trackerData) {
    trackerData.saved.forEach((item) => bookmarkedJobIds.add(item.job_id));
    trackerData.applied.forEach((item) => bookmarkedJobIds.add(item.job_id));
  }

  const candidate = recData?.candidate;
  const highMatchJobs = recData?.high_match_jobs || [];
  const eligibleJobs = recData?.eligible_jobs || [];
  const needAttentionJobs = recData?.need_attention_jobs || [];

  const currentList =
    activeTab === "high_match"
      ? highMatchJobs
      : activeTab === "eligible"
      ? eligibleJobs
      : needAttentionJobs;

  return (
    <View style={[styles.screen, { paddingTop: insets.top }]}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerRow}>
          <View>
            <View style={styles.titleRow}>
              <Sparkles size={20} color={colors.brandPrimary} />
              <Text style={styles.headerTitle}>Smart Eligibility Matcher</Text>
            </View>
            <Text style={styles.headerSubtitle}>
              Tailored specifically to your qualifications, age & category
            </Text>
          </View>
        </View>

        {/* Candidate Profile Summary Hero */}
        {candidate && (
          <View style={styles.candidateHeroCard}>
            <View style={styles.candidateHeroTop}>
              <View style={styles.candidateAvatar}>
                <UserCheck size={18} color={colors.brandPrimary} />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={styles.candidateName}>{candidate.full_name}</Text>
                <Text style={styles.candidateBio}>
                  Age: {candidate.age} yrs • {candidate.category} Category
                </Text>
              </View>
              <Pressable
                testID="edit-profile-btn"
                style={styles.editProfileBtn}
                onPress={() => router.push("/profile" as any)}
              >
                <Edit3 size={13} color={colors.brandPrimary} />
                <Text style={styles.editProfileBtnText}>Edit Profile</Text>
              </Pressable>
            </View>

            {/* Profile Meta Pills */}
            <View style={styles.candidateMetaPills}>
              <View style={styles.metaPill}>
                <GraduationCap size={12} color={colors.muted} />
                <Text style={styles.metaPillText} numberOfLines={1}>
                  {candidate.qualification} ({candidate.stream || "All Streams"})
                </Text>
              </View>
              <View style={styles.metaPill}>
                <MapPin size={12} color={colors.muted} />
                <Text style={styles.metaPillText}>
                  {candidate.domicile_state} Domicile
                </Text>
              </View>
            </View>
          </View>
        )}

        {/* Tab Segment Chrome (36pt height, flexShrink:0) */}
        <View style={styles.tabBar}>
          <Pressable
            testID="tab-high-match"
            style={[styles.tabItem, activeTab === "high_match" && styles.tabItemActive]}
            onPress={() => setActiveTab("high_match")}
          >
            <Text
              style={[
                styles.tabText,
                activeTab === "high_match" && styles.tabTextActive,
              ]}
            >
              High Match ({highMatchJobs.length})
            </Text>
          </Pressable>

          <Pressable
            testID="tab-eligible"
            style={[styles.tabItem, activeTab === "eligible" && styles.tabItemActive]}
            onPress={() => setActiveTab("eligible")}
          >
            <Text
              style={[
                styles.tabText,
                activeTab === "eligible" && styles.tabTextActive,
              ]}
            >
              Eligible ({eligibleJobs.length})
            </Text>
          </Pressable>

          <Pressable
            testID="tab-need-attention"
            style={[styles.tabItem, activeTab === "need_attention" && styles.tabItemActive]}
            onPress={() => setActiveTab("need_attention")}
          >
            <Text
              style={[
                styles.tabText,
                activeTab === "need_attention" && styles.tabTextActive,
              ]}
            >
              Check Criteria ({needAttentionJobs.length})
            </Text>
          </Pressable>
        </View>
      </View>

      {/* Main Scroll Content */}
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={isRefetching}
            onRefresh={refetch}
            tintColor={colors.brandPrimary}
          />
        }
      >
        {isLoading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={colors.brandPrimary} />
            <Text style={styles.loadingText}>Calculating dynamic eligibility across all vacancies...</Text>
          </View>
        ) : currentList.length > 0 ? (
          currentList.map((job) => (
            <JobCard
              key={job.id}
              job={job}
              isBookmarked={bookmarkedJobIds.has(job.id)}
              onToggleBookmark={(j) =>
                bookmarkMutation.mutate({
                  jobId: j.id,
                  isBookmarked: bookmarkedJobIds.has(j.id),
                })
              }
              showMatchBreakdown={true}
              testIDPrefix={`rec-job-${activeTab}`}
            />
          ))
        ) : (
          <View style={styles.emptyContainer}>
            <CheckCircle2 size={36} color={colors.success} />
            <Text style={styles.emptyTitle}>No jobs in this filter</Text>
            <Text style={styles.emptySubtitle}>
              Update your candidate profile with additional qualifications or preferred sectors to unlock more matches.
            </Text>
          </View>
        )}
      </ScrollView>
    </View>
  );
}

const useStyles = makeStyles((colors) => ({
  screen: {
    flex: 1,
    backgroundColor: colors.surface,
  },
  header: {
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    paddingHorizontal: 16,
    paddingTop: 8,
  },
  headerRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  titleRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: "800",
    color: colors.onSurface,
    letterSpacing: -0.3,
  },
  headerSubtitle: {
    fontSize: 11,
    color: colors.muted,
    marginTop: 1,
  },
  candidateHeroCard: {
    backgroundColor: colors.surfaceSecondary,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 12,
    padding: 12,
    marginBottom: 10,
  },
  candidateHeroTop: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    marginBottom: 8,
  },
  candidateAvatar: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.brandTertiary,
    alignItems: "center",
    justifyContent: "center",
  },
  candidateName: {
    fontSize: 14,
    fontWeight: "700",
    color: colors.onSurface,
  },
  candidateBio: {
    fontSize: 11,
    color: colors.muted,
  },
  editProfileBtn: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
    paddingHorizontal: 8,
    paddingVertical: 5,
    borderRadius: 6,
    gap: 4,
  },
  editProfileBtnText: {
    fontSize: 11,
    fontWeight: "600",
    color: colors.brandPrimary,
  },
  candidateMetaPills: {
    flexDirection: "row",
    gap: 6,
    flexWrap: "wrap",
  },
  metaPill: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
    gap: 4,
  },
  metaPillText: {
    fontSize: 11,
    color: colors.onSurfaceSecondary,
    fontWeight: "500",
  },
  tabBar: {
    flexDirection: "row",
    backgroundColor: colors.surfaceSecondary,
    borderRadius: 10,
    padding: 3,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: colors.border,
  },
  tabItem: {
    flex: 1,
    paddingVertical: 8,
    alignItems: "center",
    justifyContent: "center",
    borderRadius: 8,
  },
  tabItemActive: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
  },
  tabText: {
    fontSize: 11,
    color: colors.muted,
    fontWeight: "600",
  },
  tabTextActive: {
    color: colors.brandPrimary,
    fontWeight: "700",
  },
  scrollContent: {
    paddingHorizontal: 16,
    paddingTop: 14,
    paddingBottom: 32,
  },
  loadingContainer: {
    paddingVertical: 40,
    alignItems: "center",
    gap: 12,
  },
  loadingText: {
    fontSize: 13,
    color: colors.muted,
  },
  emptyContainer: {
    paddingVertical: 40,
    alignItems: "center",
    paddingHorizontal: 20,
    gap: 8,
  },
  emptyTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: colors.onSurface,
    marginTop: 6,
  },
  emptySubtitle: {
    fontSize: 12,
    color: colors.muted,
    textAlign: "center",
    lineHeight: 18,
  },
}));
