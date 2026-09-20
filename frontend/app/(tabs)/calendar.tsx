import React, { useState } from "react";
import {
  View,
  Text,
  ScrollView,
  Pressable,
  ActivityIndicator,
  RefreshControl,
  Linking,
  Modal,
  TextInput,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/src/api/apiClient";
import { CalendarEvent, ApplicationTrackerItem } from "@/src/types";
import { useTheme, makeStyles } from "@/src/theme";
import {
  Calendar,
  Clock,
  ExternalLink,
  ChevronRight,
  Bookmark,
  CheckCircle2,
  FileCheck,
  Award,
  AlertCircle,
  Plus,
  Trash2,
  Edit2,
  X,
  Building2,
  Sparkles,
} from "lucide-react-native";

export default function CalendarScreen() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { colors } = useTheme();
  const styles = useStyles();
  const queryClient = useQueryClient();

  const [viewMode, setViewMode] = useState<"calendar" | "pipeline">("calendar");
  const [calendarFilter, setCalendarFilter] = useState<"all" | "deadline" | "exam" | "admit">("all");
  const [pipelineStage, setPipelineStage] = useState<"all" | "saved" | "applied" | "admit_card_ready" | "exam_taken" | "selected">("all");

  // Edit Tracker Modal State
  const [editingItem, setEditingItem] = useState<ApplicationTrackerItem | null>(null);
  const [editStatus, setEditStatus] = useState("applied");
  const [editAppNo, setEditAppNo] = useState("");
  const [editRollNo, setEditRollNo] = useState("");
  const [editExamCenter, setEditExamCenter] = useState("");
  const [editNotes, setEditNotes] = useState("");

  const {
    data: calendarData,
    isLoading: isCalLoading,
    isRefetching: isCalRefetching,
    refetch: refetchCalendar,
  } = useQuery({
    queryKey: ["calendar"],
    queryFn: () => api.getCalendar(),
  });

  const {
    data: trackerData,
    isLoading: isTrackerLoading,
    isRefetching: isTrackerRefetching,
    refetch: refetchTracker,
  } = useQuery({
    queryKey: ["tracker"],
    queryFn: () => api.getTracker(),
  });

  // Mutations
  const updateTrackerMutation = useMutation({
    mutationFn: (data: any) => api.updateTrackerItem(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tracker"] });
      setEditingItem(null);
    },
  });

  const removeTrackerMutation = useMutation({
    mutationFn: (jobId: string) => api.removeFromTracker(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tracker"] });
    },
  });

  const openEditModal = (item: ApplicationTrackerItem) => {
    setEditingItem(item);
    setEditStatus(item.status);
    setEditAppNo(item.application_number || "");
    setEditRollNo(item.roll_number || "");
    setEditExamCenter(item.exam_center || "");
    setEditNotes(item.notes || "");
  };

  const handleSaveEdit = () => {
    if (!editingItem) return;
    updateTrackerMutation.mutate({
      job_id: editingItem.job_id,
      status: editStatus,
      application_number: editAppNo,
      roll_number: editRollNo,
      exam_center: editExamCenter,
      notes: editNotes,
    });
  };

  // Filtered Calendar Events
  const allEvents = calendarData?.events || [];
  const filteredEvents = allEvents.filter((ev) => {
    if (calendarFilter === "deadline") return ev.event_type.includes("Deadline");
    if (calendarFilter === "exam") return ev.event_type.includes("Exam");
    if (calendarFilter === "admit") return ev.event_type.includes("Admit");
    return true;
  });

  // Flattened Pipeline Items
  const pipelineAll: ApplicationTrackerItem[] = [
    ...(trackerData?.saved || []),
    ...(trackerData?.applied || []),
    ...(trackerData?.admit_card || []),
    ...(trackerData?.exam_taken || []),
    ...(trackerData?.selected || []),
  ];

  const filteredPipeline = pipelineAll.filter((item) => {
    if (pipelineStage === "all") return true;
    return item.status === pipelineStage;
  });

  return (
    <View style={[styles.screen, { paddingTop: insets.top }]}>
      {/* Sticky Header */}
      <View style={styles.header}>
        <View style={styles.headerTop}>
          <View>
            <View style={styles.titleRow}>
              <Calendar size={20} color={colors.brandPrimary} />
              <Text style={styles.headerTitle}>Deadlines & Application Tracker</Text>
            </View>
            <Text style={styles.headerSubtitle}>
              Never miss exam dates, admit cards or application cut-offs
            </Text>
          </View>
        </View>

        {/* Primary View Toggle (Calendar vs Pipeline) */}
        <View style={styles.viewModeToggle}>
          <Pressable
            testID="view-mode-calendar-btn"
            style={[styles.toggleBtn, viewMode === "calendar" && styles.toggleBtnActive]}
            onPress={() => setViewMode("calendar")}
          >
            <Clock size={14} color={viewMode === "calendar" ? colors.brandPrimary : colors.muted} />
            <Text
              style={[
                styles.toggleBtnText,
                viewMode === "calendar" && styles.toggleBtnTextActive,
              ]}
            >
              Exam Calendar & Deadlines
            </Text>
          </Pressable>

          <Pressable
            testID="view-mode-pipeline-btn"
            style={[styles.toggleBtn, viewMode === "pipeline" && styles.toggleBtnActive]}
            onPress={() => setViewMode("pipeline")}
          >
            <Bookmark size={14} color={viewMode === "pipeline" ? colors.brandPrimary : colors.muted} />
            <Text
              style={[
                styles.toggleBtnText,
                viewMode === "pipeline" && styles.toggleBtnTextActive,
              ]}
            >
              My Pipeline ({pipelineAll.length})
            </Text>
          </Pressable>
        </View>

        {/* Sub Filters Chrome */}
        {viewMode === "calendar" ? (
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.filterChipRow}
          >
            <Pressable
              testID="filter-cal-all"
              style={[styles.filterChip, calendarFilter === "all" && styles.filterChipActive]}
              onPress={() => setCalendarFilter("all")}
            >
              <Text style={[styles.filterChipText, calendarFilter === "all" && styles.filterChipTextActive]}>
                All Events ({allEvents.length})
              </Text>
            </Pressable>
            <Pressable
              testID="filter-cal-deadline"
              style={[styles.filterChip, calendarFilter === "deadline" && styles.filterChipActive]}
              onPress={() => setCalendarFilter("deadline")}
            >
              <Text style={[styles.filterChipText, calendarFilter === "deadline" && styles.filterChipTextActive]}>
                Application Deadlines
              </Text>
            </Pressable>
            <Pressable
              testID="filter-cal-exam"
              style={[styles.filterChip, calendarFilter === "exam" && styles.filterChipActive]}
              onPress={() => setCalendarFilter("exam")}
            >
              <Text style={[styles.filterChipText, calendarFilter === "exam" && styles.filterChipTextActive]}>
                Exam Dates
              </Text>
            </Pressable>
            <Pressable
              testID="filter-cal-admit"
              style={[styles.filterChip, calendarFilter === "admit" && styles.filterChipActive]}
              onPress={() => setCalendarFilter("admit")}
            >
              <Text style={[styles.filterChipText, calendarFilter === "admit" && styles.filterChipTextActive]}>
                Admit Cards
              </Text>
            </Pressable>
          </ScrollView>
        ) : (
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.filterChipRow}
          >
            <Pressable
              testID="pipeline-tab-all"
              style={[styles.filterChip, pipelineStage === "all" && styles.filterChipActive]}
              onPress={() => setPipelineStage("all")}
            >
              <Text style={[styles.filterChipText, pipelineStage === "all" && styles.filterChipTextActive]}>
                All ({pipelineAll.length})
              </Text>
            </Pressable>
            <Pressable
              testID="pipeline-tab-saved"
              style={[styles.filterChip, pipelineStage === "saved" && styles.filterChipActive]}
              onPress={() => setPipelineStage("saved")}
            >
              <Text style={[styles.filterChipText, pipelineStage === "saved" && styles.filterChipTextActive]}>
                Saved ({trackerData?.saved?.length || 0})
              </Text>
            </Pressable>
            <Pressable
              testID="pipeline-tab-applied"
              style={[styles.filterChip, pipelineStage === "applied" && styles.filterChipActive]}
              onPress={() => setPipelineStage("applied")}
            >
              <Text style={[styles.filterChipText, pipelineStage === "applied" && styles.filterChipTextActive]}>
                Applied ({trackerData?.applied?.length || 0})
              </Text>
            </Pressable>
            <Pressable
              testID="pipeline-tab-admit"
              style={[styles.filterChip, pipelineStage === "admit_card_ready" && styles.filterChipActive]}
              onPress={() => setPipelineStage("admit_card_ready")}
            >
              <Text style={[styles.filterChipText, pipelineStage === "admit_card_ready" && styles.filterChipTextActive]}>
                Admit Card ({trackerData?.admit_card?.length || 0})
              </Text>
            </Pressable>
            <Pressable
              testID="pipeline-tab-selected"
              style={[styles.filterChip, pipelineStage === "selected" && styles.filterChipActive]}
              onPress={() => setPipelineStage("selected")}
            >
              <Text style={[styles.filterChipText, pipelineStage === "selected" && styles.filterChipTextActive]}>
                Selected / Results ({trackerData?.selected?.length || 0})
              </Text>
            </Pressable>
          </ScrollView>
        )}
      </View>

      {/* Main List */}
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={viewMode === "calendar" ? isCalRefetching : isTrackerRefetching}
            onRefresh={() => {
              refetchCalendar();
              refetchTracker();
            }}
            tintColor={colors.brandPrimary}
          />
        }
      >
        {viewMode === "calendar" ? (
          /* Calendar Events Timeline */
          isCalLoading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color={colors.brandPrimary} />
              <Text style={styles.loadingText}>Syncing examination schedule and timelines...</Text>
            </View>
          ) : filteredEvents.length > 0 ? (
            filteredEvents.map((event) => {
              const isDeadline = event.event_type.includes("Deadline");
              const isExam = event.event_type.includes("Exam");
              const isAdmit = event.event_type.includes("Admit");

              let badgeBg = colors.surfaceTertiary;
              let badgeColor = colors.onSurfaceSecondary;
              if (isDeadline) {
                badgeBg = "#FEE2E2";
                badgeColor = "#B91C1C";
              } else if (isExam) {
                badgeBg = "#DBEAFE";
                badgeColor = "#1D4ED8";
              } else if (isAdmit) {
                badgeBg = "#DCFCE7";
                badgeColor = "#15803D";
              }

              return (
                <Pressable
                  key={event.id}
                  testID={`calendar-event-${event.id}`}
                  style={styles.eventCard}
                  onPress={() => {
                    router.push({
                      pathname: "/job/[id]",
                      params: { id: event.job_id },
                    });
                  }}
                >
                  <View style={styles.eventTopRow}>
                    <View style={[styles.eventTypeBadge, { backgroundColor: badgeBg }]}>
                      <Text style={[styles.eventTypeText, { color: badgeColor }]}>
                        {event.event_type}
                      </Text>
                    </View>
                    <View style={styles.boardBadge}>
                      <Text style={styles.boardBadgeText}>{event.board_code}</Text>
                    </View>
                  </View>

                  <Text style={styles.eventTitle} numberOfLines={2}>
                    {event.title.replace(/^(Deadline|Exam|Admit Card):\s*/, "")}
                  </Text>

                  <View style={styles.eventFooterRow}>
                    <View style={styles.dateBox}>
                      <Calendar size={13} color={colors.brandPrimary} />
                      <Text style={styles.dateText}>{event.date}</Text>
                    </View>

                    <Pressable
                      testID={`event-apply-link-${event.id}`}
                      style={styles.actionLink}
                      onPress={(e) => {
                        e.stopPropagation();
                        if (event.official_url) {
                          Linking.openURL(event.official_url).catch((err) =>
                            console.error("Error opening URL", err)
                          );
                        }
                      }}
                    >
                      <Text style={styles.actionLinkText}>Official Portal</Text>
                      <ExternalLink size={12} color={colors.brandPrimary} />
                    </Pressable>
                  </View>
                </Pressable>
              );
            })
          ) : (
            <View style={styles.emptyContainer}>
              <CheckCircle2 size={36} color={colors.success} />
              <Text style={styles.emptyTitle}>No scheduled events in this filter</Text>
            </View>
          )
        ) : (
          /* Application Pipeline List */
          isTrackerLoading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color={colors.brandPrimary} />
              <Text style={styles.loadingText}>Loading your application progress...</Text>
            </View>
          ) : filteredPipeline.length > 0 ? (
            filteredPipeline.map((item) => {
              let statusLabel = "Saved";
              let statusBg = colors.surfaceTertiary;
              let statusColor = colors.onSurfaceSecondary;

              if (item.status === "applied") {
                statusLabel = "Applied";
                statusBg = "#DBEAFE";
                statusColor = "#1D4ED8";
              } else if (item.status === "admit_card_ready") {
                statusLabel = "Admit Card Out";
                statusBg = "#DCFCE7";
                statusColor = "#15803D";
              } else if (item.status === "selected") {
                statusLabel = "Selected";
                statusBg = "#FEF3C7";
                statusColor = "#B45309";
              }

              return (
                <View
                  key={item.job_id}
                  testID={`pipeline-item-${item.job_id}`}
                  style={styles.pipelineCard}
                >
                  <View style={styles.pipelineHeader}>
                    <View style={[styles.statusBadge, { backgroundColor: statusBg }]}>
                      <Text style={[styles.statusBadgeText, { color: statusColor }]}>
                        {statusLabel}
                      </Text>
                    </View>
                    <View style={styles.pipelineActionRow}>
                      <Pressable
                        testID={`edit-tracker-${item.job_id}`}
                        style={styles.smallIconBtn}
                        onPress={() => openEditModal(item)}
                      >
                        <Edit2 size={13} color={colors.onSurface} />
                      </Pressable>
                      <Pressable
                        testID={`delete-tracker-${item.job_id}`}
                        style={styles.smallIconBtn}
                        onPress={() => removeTrackerMutation.mutate(item.job_id)}
                      >
                        <Trash2 size={13} color={colors.error} />
                      </Pressable>
                    </View>
                  </View>

                  <Pressable
                    onPress={() => {
                      router.push({
                        pathname: "/job/[id]",
                        params: { id: item.job_id },
                      });
                    }}
                  >
                    <Text style={styles.pipelineTitle}>{item.job_title}</Text>
                    <Text style={styles.pipelineBoard}>{item.board_code}</Text>
                  </Pressable>

                  {/* Application Data Grid */}
                  {Boolean(item.application_number || item.roll_number || item.exam_center) ? (
                    <View style={styles.trackerDetailsBox}>
                      {Boolean(item.application_number) ? (
                        <View style={styles.metaDataRow}>
                          <Text style={styles.metaDataLabel}>App No:</Text>
                          <Text style={styles.metaDataVal}>{item.application_number}</Text>
                        </View>
                      ) : null}
                      {Boolean(item.roll_number) ? (
                        <View style={styles.metaDataRow}>
                          <Text style={styles.metaDataLabel}>Roll No:</Text>
                          <Text style={styles.metaDataVal}>{item.roll_number}</Text>
                        </View>
                      ) : null}
                      {Boolean(item.exam_center) ? (
                        <View style={styles.metaDataRow}>
                          <Text style={styles.metaDataLabel}>Center:</Text>
                          <Text style={styles.metaDataVal}>{item.exam_center}</Text>
                        </View>
                      ) : null}
                    </View>
                  ) : null}

                  {Boolean(item.notes) ? (
                    <View style={styles.notesBox}>
                      <Text style={styles.notesText}>📝 {item.notes}</Text>
                    </View>
                  ) : null}
                </View>
              );
            })
          ) : (
            <View style={styles.emptyContainer}>
              <Bookmark size={36} color={colors.muted} />
              <Text style={styles.emptyTitle}>No tracked applications yet</Text>
              <Text style={styles.emptySubtitle}>
                Bookmark or mark jobs as 'Applied' from the job feed to organize your preparation pipeline.
              </Text>
              <Pressable
                testID="browse-jobs-btn"
                style={styles.emptyActionBtn}
                onPress={() => router.push("/(tabs)" as any)}
              >
                <Text style={styles.emptyActionText}>Browse Government Jobs</Text>
              </Pressable>
            </View>
          )
        )}
      </ScrollView>

      {/* Edit Tracker Item Modal */}
      {editingItem && (
        <Modal
          visible={!!editingItem}
          animationType="slide"
          transparent={true}
          onRequestClose={() => setEditingItem(null)}
        >
          <View style={styles.modalOverlay}>
            <View style={styles.modalContainer}>
              <View style={styles.modalHeader}>
                <Text style={styles.modalTitle}>Update Application Progress</Text>
                <Pressable
                  testID="close-tracker-modal-btn"
                  onPress={() => setEditingItem(null)}
                  style={styles.closeBtn}
                >
                  <X size={18} color={colors.onSurface} />
                </Pressable>
              </View>

              <ScrollView style={{ paddingHorizontal: 20 }} contentContainerStyle={{ paddingVertical: 14 }}>
                <Text style={styles.inputLabel}>Current Status</Text>
                <View style={styles.statusSelectRow}>
                  {[
                    { label: "Saved", val: "saved" },
                    { label: "Applied", val: "applied" },
                    { label: "Admit Card", val: "admit_card_ready" },
                    { label: "Exam Taken", val: "exam_taken" },
                    { label: "Selected", val: "selected" },
                  ].map((s) => (
                    <Pressable
                      key={s.val}
                      testID={`select-status-${s.val}`}
                      style={[
                        styles.statusChoiceChip,
                        editStatus === s.val && styles.statusChoiceChipActive,
                      ]}
                      onPress={() => setEditStatus(s.val)}
                    >
                      <Text
                        style={[
                          styles.statusChoiceText,
                          editStatus === s.val && styles.statusChoiceTextActive,
                        ]}
                      >
                        {s.label}
                      </Text>
                    </Pressable>
                  ))}
                </View>

                <Text style={styles.inputLabel}>Application / Registration Number</Text>
                <TextInput
                  testID="tracker-app-no-input"
                  style={styles.textInput}
                  placeholder="e.g. UPSC2026-89104"
                  placeholderTextColor={colors.muted}
                  value={editAppNo}
                  onChangeText={setEditAppNo}
                />

                <Text style={styles.inputLabel}>Roll Number (if allotted)</Text>
                <TextInput
                  testID="tracker-roll-no-input"
                  style={styles.textInput}
                  placeholder="e.g. 0891234"
                  placeholderTextColor={colors.muted}
                  value={editRollNo}
                  onChangeText={setEditRollNo}
                />

                <Text style={styles.inputLabel}>Exam City / Test Center</Text>
                <TextInput
                  testID="tracker-center-input"
                  style={styles.textInput}
                  placeholder="e.g. New Delhi Zone 2"
                  placeholderTextColor={colors.muted}
                  value={editExamCenter}
                  onChangeText={setEditExamCenter}
                />

                <Text style={styles.inputLabel}>Preparation Notes / Mock Scores</Text>
                <TextInput
                  testID="tracker-notes-input"
                  style={[styles.textInput, { height: 70, textAlignVertical: "top" }]}
                  placeholder="e.g. Completed Paper 1 syllabus revision; target score 120+"
                  placeholderTextColor={colors.muted}
                  value={editNotes}
                  onChangeText={setEditNotes}
                  multiline={true}
                />
              </ScrollView>

              <View style={styles.modalFooter}>
                <Pressable
                  testID="save-tracker-changes-btn"
                  style={styles.saveBtn}
                  onPress={handleSaveEdit}
                  disabled={updateTrackerMutation.isPending}
                >
                  <Text style={styles.saveBtnText}>Save Progress</Text>
                </Pressable>
              </View>
            </View>
          </View>
        </Modal>
      )}
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
  headerTop: {
    marginBottom: 8,
  },
  titleRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  headerTitle: {
    fontSize: 17,
    fontWeight: "800",
    color: colors.onSurface,
    letterSpacing: -0.3,
  },
  headerSubtitle: {
    fontSize: 11,
    color: colors.muted,
    marginTop: 1,
  },
  viewModeToggle: {
    flexDirection: "row",
    backgroundColor: colors.surfaceSecondary,
    borderRadius: 10,
    padding: 3,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: colors.border,
  },
  toggleBtn: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 8,
    borderRadius: 8,
    gap: 6,
  },
  toggleBtnActive: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
  },
  toggleBtnText: {
    fontSize: 12,
    color: colors.muted,
    fontWeight: "600",
  },
  toggleBtnTextActive: {
    color: colors.brandPrimary,
    fontWeight: "700",
  },
  filterChipRow: {
    paddingBottom: 10,
    gap: 8,
  },
  filterChip: {
    flexShrink: 0,
    height: 32,
    paddingHorizontal: 12,
    borderRadius: 16,
    backgroundColor: colors.surfaceSecondary,
    borderColor: colors.border,
    borderWidth: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  filterChipActive: {
    backgroundColor: colors.brandPrimary,
    borderColor: colors.brandPrimary,
  },
  filterChipText: {
    fontSize: 11,
    color: colors.onSurfaceSecondary,
    fontWeight: "600",
  },
  filterChipTextActive: {
    color: colors.onBrandPrimary,
    fontWeight: "700",
  },
  scrollContent: {
    paddingHorizontal: 16,
    paddingTop: 14,
    paddingBottom: 32,
  },
  eventCard: {
    backgroundColor: colors.surfaceSecondary,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 12,
    padding: 14,
    marginBottom: 10,
  },
  eventTopRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 6,
  },
  eventTypeBadge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  eventTypeText: {
    fontSize: 11,
    fontWeight: "700",
  },
  boardBadge: {
    backgroundColor: colors.surfaceTertiary,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  boardBadgeText: {
    fontSize: 10,
    fontWeight: "700",
    color: colors.onSurfaceSecondary,
  },
  eventTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: colors.onSurface,
    lineHeight: 19,
    marginBottom: 10,
  },
  eventFooterRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    borderTopWidth: 1,
    borderTopColor: colors.divider,
    paddingTop: 8,
  },
  dateBox: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
  },
  dateText: {
    fontSize: 12,
    fontWeight: "600",
    color: colors.onSurface,
  },
  actionLink: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
  },
  actionLinkText: {
    fontSize: 11,
    fontWeight: "700",
    color: colors.brandPrimary,
  },
  pipelineCard: {
    backgroundColor: colors.surfaceSecondary,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
  },
  pipelineHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 6,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  statusBadgeText: {
    fontSize: 11,
    fontWeight: "700",
  },
  pipelineActionRow: {
    flexDirection: "row",
    gap: 6,
  },
  smallIconBtn: {
    width: 28,
    height: 28,
    borderRadius: 6,
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  pipelineTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: colors.onSurface,
    marginBottom: 2,
  },
  pipelineBoard: {
    fontSize: 11,
    color: colors.muted,
    marginBottom: 8,
  },
  trackerDetailsBox: {
    backgroundColor: colors.surface,
    borderRadius: 8,
    padding: 8,
    borderWidth: 1,
    borderColor: colors.border,
    gap: 4,
    marginBottom: 8,
  },
  metaDataRow: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  metaDataLabel: {
    fontSize: 11,
    color: colors.muted,
    fontWeight: "500",
  },
  metaDataVal: {
    fontSize: 11,
    fontWeight: "700",
    color: colors.onSurface,
  },
  notesBox: {
    backgroundColor: colors.surfaceTertiary,
    borderRadius: 6,
    padding: 6,
  },
  notesText: {
    fontSize: 11,
    color: colors.onSurfaceSecondary,
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
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.5)",
    justifyContent: "flex-end",
  },
  modalContainer: {
    backgroundColor: colors.surface,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: "85%",
    paddingBottom: 24,
  },
  modalHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 20,
    paddingTop: 18,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  modalTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: colors.onSurface,
  },
  closeBtn: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.surfaceSecondary,
    alignItems: "center",
    justifyContent: "center",
  },
  inputLabel: {
    fontSize: 12,
    fontWeight: "700",
    color: colors.onSurface,
    marginTop: 10,
    marginBottom: 4,
  },
  statusSelectRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
    marginBottom: 6,
  },
  statusChoiceChip: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 6,
    backgroundColor: colors.surfaceSecondary,
    borderColor: colors.border,
    borderWidth: 1,
  },
  statusChoiceChipActive: {
    backgroundColor: colors.brandPrimary,
    borderColor: colors.brandPrimary,
  },
  statusChoiceText: {
    fontSize: 12,
    color: colors.onSurfaceSecondary,
    fontWeight: "500",
  },
  statusChoiceTextActive: {
    color: colors.onBrandPrimary,
    fontWeight: "700",
  },
  textInput: {
    backgroundColor: colors.surfaceSecondary,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    fontSize: 13,
    color: colors.onSurface,
    marginBottom: 4,
  },
  modalFooter: {
    paddingHorizontal: 20,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: colors.divider,
  },
  saveBtn: {
    backgroundColor: colors.brandPrimary,
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: "center",
    justifyContent: "center",
    minHeight: 44,
  },
  saveBtnText: {
    fontSize: 14,
    fontWeight: "700",
    color: colors.onBrandPrimary,
  },
}));
