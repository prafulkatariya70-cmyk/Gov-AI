import React from "react";
import {
  View,
  Text,
  ScrollView,
  Pressable,
  ActivityIndicator,
  RefreshControl,
  Linking,
} from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/src/api/apiClient";
import { useTheme, makeStyles } from "@/src/theme";
import {
  ArrowLeft,
  Bell,
  Sparkles,
  CheckCircle2,
  ExternalLink,
  ChevronRight,
  Building,
} from "lucide-react-native";

export default function NotificationsScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { colors } = useTheme();
  const styles = useStyles();

  const { data: jobsData, isLoading, refetch, isRefetching } = useQuery({
    queryKey: ["jobs-latest"],
    queryFn: () => api.getJobs({ sort_by: "latest" }),
  });

  const jobs = jobsData?.jobs || [];

  return (
    <View style={[styles.screen, { paddingTop: insets.top }]}>
      <View style={styles.topHeader}>
        <Pressable
          testID="notif-back-btn"
          style={styles.headerIconBtn}
          onPress={() => router.back()}
          hitSlop={8}
        >
          <ArrowLeft size={18} color={colors.onSurface} />
        </Pressable>

        <Text style={styles.headerTitleText}>Live Government Job Bulletins</Text>
      </View>

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
        <View style={styles.bannerBox}>
          <Sparkles size={18} color={colors.brandPrimary} />
          <View style={{ flex: 1 }}>
            <Text style={styles.bannerTitle}>Real-time Official Synchronizer</Text>
            <Text style={styles.bannerSub}>
              Directly synced with Employment News, Central Ministries & State Gazettes.
            </Text>
          </View>
        </View>

        {isLoading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={colors.brandPrimary} />
          </View>
        ) : (
          jobs.map((j) => (
            <Pressable
              key={j.id}
              testID={`bulletin-item-${j.id}`}
              style={styles.bulletinCard}
              onPress={() => {
                router.push({
                  pathname: "/job/[id]",
                  params: { id: j.id },
                });
              }}
            >
              <View style={styles.cardHeaderRow}>
                <View style={styles.boardBadge}>
                  <Text style={styles.boardText}>{j.board_code}</Text>
                </View>
                <Text style={styles.dateText}>{j.notification_date}</Text>
              </View>

              <Text style={styles.cardTitle}>{j.title}</Text>
              <Text style={styles.cardSub}>
                {j.post_name} • {j.total_vacancies.toLocaleString("en-IN")} Posts
              </Text>

              <View style={styles.cardFooter}>
                <Text style={styles.lastDateText}>Deadline: {j.last_date}</Text>
                <View style={{ flexDirection: "row", alignItems: "center", gap: 4 }}>
                  <Text style={styles.viewText}>View Gazette</Text>
                  <ChevronRight size={14} color={colors.brandPrimary} />
                </View>
              </View>
            </Pressable>
          ))
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
  topHeader: {
    flexDirection: "row",
    alignItems: "center",
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
    fontSize: 16,
    fontWeight: "700",
    color: colors.onSurface,
    marginLeft: 12,
  },
  scrollContent: {
    paddingHorizontal: 16,
    paddingTop: 14,
    paddingBottom: 32,
  },
  bannerBox: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    padding: 12,
    gap: 10,
    marginBottom: 14,
  },
  bannerTitle: {
    fontSize: 13,
    fontWeight: "700",
    color: colors.onSurface,
  },
  bannerSub: {
    fontSize: 11,
    color: colors.muted,
    marginTop: 2,
  },
  bulletinCard: {
    backgroundColor: colors.surfaceSecondary,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 12,
    padding: 14,
    marginBottom: 10,
  },
  cardHeaderRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 6,
  },
  boardBadge: {
    backgroundColor: colors.brandTertiary,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  boardText: {
    fontSize: 11,
    fontWeight: "700",
    color: colors.onBrandTertiary,
  },
  dateText: {
    fontSize: 11,
    color: colors.muted,
  },
  cardTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: colors.onSurface,
    marginBottom: 3,
  },
  cardSub: {
    fontSize: 12,
    color: colors.muted,
    marginBottom: 8,
  },
  cardFooter: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    borderTopWidth: 1,
    borderTopColor: colors.divider,
    paddingTop: 8,
  },
  lastDateText: {
    fontSize: 11,
    color: colors.onSurfaceSecondary,
    fontWeight: "600",
  },
  viewText: {
    fontSize: 11,
    fontWeight: "700",
    color: colors.brandPrimary,
  },
  loadingContainer: {
    paddingVertical: 40,
    alignItems: "center",
  },
}));
