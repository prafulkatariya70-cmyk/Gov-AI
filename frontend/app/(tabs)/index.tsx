import React, { useState, useMemo } from "react";
import {
  View,
  Text,
  TextInput,
  ScrollView,
  FlatList,
  Pressable,
  RefreshControl,
  ActivityIndicator,
  Animated,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/src/api/apiClient";
import { Job } from "@/src/types";
import { useTheme, makeStyles } from "@/src/theme";
import { JobCard } from "@/src/components/JobCard";
import { DailyStreakCard } from "@/src/components/DailyStreakCard";
import { FilterModal, FilterState } from "@/src/components/FilterModal";
import {
  Search,
  SlidersHorizontal,
  RefreshCw,
  Sparkles,
  ShieldAlert,
  User,
  Bell,
  CheckCircle2,
  AlertCircle,
  Building,
} from "lucide-react-native";

const CATEGORY_CHIPS = [
  { label: "All Jobs", category: "All Categories" },
  { label: "UPSC & Civil", category: "Civil Services" },
  { label: "SSC Exams", category: "Staff Selection" },
  { label: "Railways RRB", category: "Railways" },
  { label: "Banking & PSU", category: "Banking & PSU" },
  { label: "Police & Defense", category: "Police & Paramilitary" },
  { label: "State PSC", category: "State PSC" },
  { label: "Teaching", category: "Teaching" },
  { label: "Engineering", category: "Engineering & Tech" },
];

export default function HomeScreen() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { colors } = useTheme();
  const styles = useStyles();
  const queryClient = useQueryClient();

  // Search & Filter State
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All Categories");
  const [filterModalVisible, setFilterModalVisible] = useState(false);
  const [activeSegment, setActiveSegment] = useState<"all" | "central" | "state" | "closing_soon">("all");
  const [syncMessage, setSyncMessage] = useState<string | null>(null);

  const [filterState, setFilterState] = useState<FilterState>({
    category: "All Categories",
    job_type: "All Types",
    state: "All India",
    qualification: "All Qualifications",
    sort_by: "recommended",
  });

  // Queries
  const {
    data: jobsData,
    isLoading: isJobsLoading,
    isRefetching: isJobsRefetching,
    refetch: refetchJobs,
  } = useQuery({
    queryKey: [
      "jobs",
      searchQuery,
      selectedCategory,
      filterState,
      activeSegment,
    ],
    queryFn: () =>
      api.getJobs({
        search: searchQuery || undefined,
        category: selectedCategory !== "All Categories" ? selectedCategory : filterState.category !== "All Categories" ? filterState.category : undefined,
        job_type: activeSegment === "central" ? "Central" : activeSegment === "state" ? "State" : filterState.job_type !== "All Types" ? filterState.job_type : undefined,
        state: filterState.state !== "All India" ? filterState.state : undefined,
        qualification: filterState.qualification !== "All Qualifications" ? filterState.qualification : undefined,
        status: activeSegment === "closing_soon" ? "Closing Soon" : undefined,
        sort_by: activeSegment === "closing_soon" ? "closing_soon" : filterState.sort_by,
      }),
  });

  const { data: profileData } = useQuery({
    queryKey: ["profile"],
    queryFn: () => api.getProfile(),
  });

  const { data: streakData, refetch: refetchCapsule } = useQuery({
    queryKey: ["daily-capsule"],
    queryFn: () => api.getDailyCapsule(),
  });

  const { data: trackerData } = useQuery({
    queryKey: ["tracker"],
    queryFn: () => api.getTracker(),
  });

  // Mutations
  const checkinMutation = useMutation({
    mutationFn: () => api.checkinDaily(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["daily-capsule"] });
      queryClient.invalidateQueries({ queryKey: ["profile"] });
    },
  });

  const syncMutation = useMutation({
    mutationFn: () => api.triggerJobSync(),
    onSuccess: (data) => {
      setSyncMessage(data.message);
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      setTimeout(() => setSyncMessage(null), 4000);
    },
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

  // Bookmarked Set
  const bookmarkedJobIds = useMemo(() => {
    if (!trackerData) return new Set<string>();
    const ids = new Set<string>();
    trackerData.saved.forEach((item) => ids.add(item.job_id));
    trackerData.applied.forEach((item) => ids.add(item.job_id));
    return ids;
  }, [trackerData]);

  const jobsList = jobsData?.jobs || [];
  const candidateSummary = jobsData?.candidate_summary;
  const featuredJob = useMemo(() => jobsList.find((j) => j.is_featured), [jobsList]);

  const activeFiltersCount = useMemo(() => {
    let count = 0;
    if (filterState.category !== "All Categories") count++;
    if (filterState.job_type !== "All Types") count++;
    if (filterState.state !== "All India") count++;
    if (filterState.qualification !== "All Qualifications") count++;
    if (filterState.sort_by !== "recommended") count++;
    return count;
  }, [filterState]);

  const handleToggleBookmark = (job: Job) => {
    const isBookmarked = bookmarkedJobIds.has(job.id);
    bookmarkMutation.mutate({ jobId: job.id, isBookmarked });
  };

  return (
    <View style={[styles.screen, { paddingTop: insets.top }]}>
      {/* Sticky Header Section */}
      <View style={styles.header}>
        {/* Top Branding Row */}
        <View style={styles.topBar}>
          <View>
            <View style={styles.brandRow}>
              <Building size={20} color={colors.brandPrimary} />
              <Text style={styles.appTitle}>SarkariSeva AI</Text>
            </View>
            <Text style={styles.appTagline}>
              Official Central & State Govt Job Gateway
            </Text>
          </View>

          <View style={styles.topRightRow}>
            {/* Live Auto-Sync Button */}
            <Pressable
              testID="sync-jobs-btn"
              style={styles.syncBtn}
              onPress={() => syncMutation.mutate()}
              disabled={syncMutation.isPending}
            >
              {syncMutation.isPending ? (
                <ActivityIndicator size="small" color={colors.brandPrimary} />
              ) : (
                <>
                  <RefreshCw size={13} color={colors.brandPrimary} />
                  <Text style={styles.syncBtnText}>Sync Live</Text>
                </>
              )}
            </Pressable>

            {/* Profile Avatar Trigger */}
            <Pressable
              testID="profile-header-btn"
              style={styles.profileBtn}
              onPress={() => router.push("/profile" as any)}
            >
              <User size={16} color={colors.onSurface} />
            </Pressable>
          </View>
        </View>

        {/* Live Sync Toast Banner */}
        {Boolean(syncMessage) ? (
          <View style={styles.syncToastBanner}>
            <CheckCircle2 size={14} color="#166534" />
            <Text style={styles.syncToastText}>{syncMessage}</Text>
          </View>
        ) : null}

        {/* Candidate Match Pill */}
        {Boolean(candidateSummary) ? (
          <Pressable
            testID="candidate-summary-pill"
            style={styles.candidatePill}
            onPress={() => router.push("/profile" as any)}
          >
            <Sparkles size={13} color={colors.brandPrimary} />
            <Text style={styles.candidatePillText} numberOfLines={1}>
              Matching for <Text style={styles.boldText}>{candidateSummary?.name}</Text> ({candidateSummary?.category} • {candidateSummary?.qualification} • {candidateSummary?.domicile_state})
            </Text>
          </Pressable>
        ) : null}

        {/* Search Bar & Filter Button */}
        <View style={styles.searchBarRow}>
          <View style={styles.searchBox}>
            <Search size={16} color={colors.muted} />
            <TextInput
              testID="job-search-input"
              style={styles.searchInput}
              placeholder="Search UPSC, SSC, Railways, Police, State PSC..."
              placeholderTextColor={colors.muted}
              value={searchQuery}
              onChangeText={setSearchQuery}
              clearButtonMode="while-editing"
            />
          </View>

          <Pressable
            testID="filter-toggle-btn"
            style={[
              styles.filterBtn,
              activeFiltersCount > 0 && styles.filterBtnActive,
            ]}
            onPress={() => setFilterModalVisible(true)}
          >
            <SlidersHorizontal
              size={17}
              color={activeFiltersCount > 0 ? colors.onBrandPrimary : colors.onSurface}
            />
            {activeFiltersCount > 0 && (
              <View style={styles.filterBadge}>
                <Text style={styles.filterBadgeText}>{activeFiltersCount}</Text>
              </View>
            )}
          </Pressable>
        </View>

        {/* Category Chip Row (Chrome: 56pt height, flexShrink: 0, 36pt chip height) */}
        <View style={styles.chipRowWrapper}>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.chipScrollContainer}
          >
            {CATEGORY_CHIPS.map((chip) => {
              const isSelected = selectedCategory === chip.category;
              return (
                <Pressable
                  key={chip.category}
                  testID={`category-chip-${chip.category.replace(/\s+/g, "-")}`}
                  style={[styles.categoryChip, isSelected && styles.categoryChipSelected]}
                  onPress={() => setSelectedCategory(chip.category)}
                >
                  <Text
                    style={[
                      styles.categoryChipText,
                      isSelected && styles.categoryChipTextSelected,
                    ]}
                  >
                    {chip.label}
                  </Text>
                </Pressable>
              );
            })}
          </ScrollView>
        </View>
      </View>

      {/* Main Content List */}
      <FlatList
        data={jobsList}
        keyExtractor={(item) => item.id}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.feedContentContainer}
        refreshControl={
          <RefreshControl
            refreshing={isJobsRefetching}
            onRefresh={() => {
              refetchJobs();
              refetchCapsule();
            }}
            tintColor={colors.brandPrimary}
          />
        }
        ListHeaderComponent={
          <View>
            {/* Daily Habit Streak Card */}
            {streakData && (
              <DailyStreakCard
                streakCount={streakData.user_streak}
                points={streakData.user_points}
                isCheckedInToday={streakData.is_checked_in_today}
                onCheckIn={() => checkinMutation.mutate()}
                isLoading={checkinMutation.isPending}
              />
            )}

            {/* Quick Segment Filter Bar */}
            <View style={styles.segmentBar}>
              <Pressable
                testID="segment-all"
                style={[
                  styles.segmentItem,
                  activeSegment === "all" && styles.segmentItemActive,
                ]}
                onPress={() => setActiveSegment("all")}
              >
                <Text
                  style={[
                    styles.segmentText,
                    activeSegment === "all" && styles.segmentTextActive,
                  ]}
                >
                  All ({jobsList.length})
                </Text>
              </Pressable>

              <Pressable
                testID="segment-central"
                style={[
                  styles.segmentItem,
                  activeSegment === "central" && styles.segmentItemActive,
                ]}
                onPress={() => setActiveSegment("central")}
              >
                <Text
                  style={[
                    styles.segmentText,
                    activeSegment === "central" && styles.segmentTextActive,
                  ]}
                >
                  Central Govt
                </Text>
              </Pressable>

              <Pressable
                testID="segment-state"
                style={[
                  styles.segmentItem,
                  activeSegment === "state" && styles.segmentItemActive,
                ]}
                onPress={() => setActiveSegment("state")}
              >
                <Text
                  style={[
                    styles.segmentText,
                    activeSegment === "state" && styles.segmentTextActive,
                  ]}
                >
                  State PSC/Police
                </Text>
              </Pressable>

              <Pressable
                testID="segment-closing"
                style={[
                  styles.segmentItem,
                  activeSegment === "closing_soon" && styles.segmentItemActive,
                ]}
                onPress={() => setActiveSegment("closing_soon")}
              >
                <Text
                  style={[
                    styles.segmentText,
                    activeSegment === "closing_soon" && styles.segmentTextActive,
                  ]}
                >
                  Closing Soon
                </Text>
              </Pressable>
            </View>

            {/* Feed Section Title */}
            <View style={styles.sectionHeaderRow}>
              <Text style={styles.feedHeading}>
                {activeSegment === "closing_soon"
                  ? "Urgent: Applications Closing Soon"
                  : selectedCategory !== "All Categories"
                  ? `${selectedCategory} Openings`
                  : "Live Government Vacancies"}
              </Text>
              <Text style={styles.feedCountText}>
                {jobsList.length} Opportunities
              </Text>
            </View>
          </View>
        }
        renderItem={({ item }) => (
          <JobCard
            job={item}
            isBookmarked={bookmarkedJobIds.has(item.id)}
            onToggleBookmark={handleToggleBookmark}
            showMatchBreakdown={true}
          />
        )}
        ListEmptyComponent={
          isJobsLoading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color={colors.brandPrimary} />
              <Text style={styles.loadingText}>Fetching official government job gazettes...</Text>
            </View>
          ) : (
            <View style={styles.emptyContainer}>
              <AlertCircle size={36} color={colors.muted} />
              <Text style={styles.emptyTitle}>No matching job notifications</Text>
              <Text style={styles.emptySubtitle}>
                Try adjusting your search criteria, category filters or degree selection.
              </Text>
              <Pressable
                testID="reset-search-empty-btn"
                style={styles.emptyActionBtn}
                onPress={() => {
                  setSearchQuery("");
                  setSelectedCategory("All Categories");
                  setFilterState({
                    category: "All Categories",
                    job_type: "All Types",
                    state: "All India",
                    qualification: "All Qualifications",
                    sort_by: "recommended",
                  });
                  setActiveSegment("all");
                }}
              >
                <Text style={styles.emptyActionText}>Reset All Filters</Text>
              </Pressable>
            </View>
          )
        }
      />

      {/* Filter Modal */}
      <FilterModal
        visible={filterModalVisible}
        onClose={() => setFilterModalVisible(false)}
        filters={filterState}
        onApply={(newFilters) => setFilterState(newFilters)}
        onReset={() => {
          setFilterState({
            category: "All Categories",
            job_type: "All Types",
            state: "All India",
            qualification: "All Qualifications",
            sort_by: "recommended",
          });
        }}
      />
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
  topBar: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  brandRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  appTitle: {
    fontSize: 18,
    fontWeight: "800",
    color: colors.brandPrimary,
    letterSpacing: -0.3,
  },
  appTagline: {
    fontSize: 11,
    color: colors.muted,
    marginTop: 1,
  },
  topRightRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  syncBtn: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: 8,
    paddingVertical: 6,
    borderRadius: 8,
    gap: 4,
  },
  syncBtnText: {
    fontSize: 11,
    fontWeight: "700",
    color: colors.brandPrimary,
  },
  profileBtn: {
    width: 34,
    height: 34,
    borderRadius: 17,
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: "center",
    justifyContent: "center",
  },
  syncToastBanner: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#DCFCE7",
    borderColor: "#86EFAC",
    borderWidth: 1,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
    gap: 6,
    marginBottom: 8,
  },
  syncToastText: {
    fontSize: 12,
    color: "#166534",
    fontWeight: "600",
  },
  candidatePill: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surfaceSecondary,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 5,
    gap: 6,
    marginBottom: 10,
  },
  candidatePillText: {
    fontSize: 11,
    color: colors.onSurfaceSecondary,
    flex: 1,
  },
  boldText: {
    fontWeight: "700",
    color: colors.brandPrimary,
  },
  searchBarRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: 10,
  },
  searchBox: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surfaceSecondary,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 10,
    paddingHorizontal: 12,
    height: 42,
    gap: 8,
  },
  searchInput: {
    flex: 1,
    fontSize: 13,
    color: colors.onSurface,
    paddingVertical: 0,
  },
  filterBtn: {
    width: 42,
    height: 42,
    borderRadius: 10,
    backgroundColor: colors.surfaceSecondary,
    borderColor: colors.border,
    borderWidth: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  filterBtnActive: {
    backgroundColor: colors.brandPrimary,
    borderColor: colors.brandPrimary,
  },
  filterBadge: {
    position: "absolute",
    top: -4,
    right: -4,
    backgroundColor: colors.brandSecondary,
    width: 18,
    height: 18,
    borderRadius: 9,
    alignItems: "center",
    justifyContent: "center",
  },
  filterBadgeText: {
    color: colors.onBrandPrimary,
    fontSize: 10,
    fontWeight: "700",
  },
  chipRowWrapper: {
    height: 56,
    justifyContent: "center",
    marginHorizontal: -16,
  },
  chipScrollContainer: {
    paddingHorizontal: 16,
    alignItems: "center",
    gap: 8,
  },
  categoryChip: {
    flexShrink: 0,
    height: 36,
    paddingHorizontal: 14,
    borderRadius: 18,
    backgroundColor: colors.surfaceSecondary,
    borderColor: colors.border,
    borderWidth: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  categoryChipSelected: {
    backgroundColor: colors.brandPrimary,
    borderColor: colors.brandPrimary,
  },
  categoryChipText: {
    fontSize: 12,
    color: colors.onSurfaceSecondary,
    fontWeight: "600",
  },
  categoryChipTextSelected: {
    color: colors.onBrandPrimary,
    fontWeight: "700",
  },
  feedContentContainer: {
    paddingHorizontal: 16,
    paddingTop: 14,
    paddingBottom: 32,
  },
  segmentBar: {
    flexDirection: "row",
    backgroundColor: colors.surfaceSecondary,
    borderRadius: 10,
    padding: 3,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: colors.border,
  },
  segmentItem: {
    flex: 1,
    paddingVertical: 7,
    alignItems: "center",
    justifyContent: "center",
    borderRadius: 8,
  },
  segmentItemActive: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
  },
  segmentText: {
    fontSize: 11,
    color: colors.muted,
    fontWeight: "600",
  },
  segmentTextActive: {
    color: colors.brandPrimary,
    fontWeight: "700",
  },
  sectionHeaderRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 10,
  },
  feedHeading: {
    fontSize: 15,
    fontWeight: "700",
    color: colors.onSurface,
  },
  feedCountText: {
    fontSize: 12,
    color: colors.muted,
    fontWeight: "500",
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
  emptyActionBtn: {
    marginTop: 12,
    backgroundColor: colors.brandPrimary,
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 8,
  },
  emptyActionText: {
    fontSize: 13,
    fontWeight: "700",
    color: colors.onBrandPrimary,
  },
}));
