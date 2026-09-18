import React, { useState } from "react";
import {
  View,
  Text,
  Modal,
  Pressable,
  ScrollView,
  StyleSheet,
} from "react-native";
import { useTheme, makeStyles } from "@/src/theme";
import { X, Check, RotateCcw } from "lucide-react-native";

export interface FilterState {
  category: string;
  job_type: string;
  state: string;
  qualification: string;
  sort_by: string;
}

interface Props {
  visible: boolean;
  onClose: () => void;
  filters: FilterState;
  onApply: (newFilters: FilterState) => void;
  onReset: () => void;
}

const CATEGORIES = [
  "All Categories",
  "Civil Services",
  "Staff Selection",
  "Railways",
  "Banking & PSU",
  "Police & Paramilitary",
  "Defense",
  "State PSC",
  "Teaching",
  "Engineering & Tech",
];

const JOB_TYPES = ["All Types", "Central", "State"];

const STATES = [
  "All India",
  "Uttar Pradesh",
  "Bihar",
  "Rajasthan",
  "Maharashtra",
  "Delhi",
  "Madhya Pradesh",
  "Karnataka",
  "Tamil Nadu",
  "West Bengal",
  "Gujarat",
  "Telangana",
];

const QUALIFICATIONS = [
  "All Qualifications",
  "10th Pass",
  "12th Pass",
  "Diploma",
  "Graduate",
  "B.Tech/B.E.",
  "Post Graduate",
  "LLB",
  "B.Ed",
];

const SORT_OPTIONS = [
  { label: "Smart Match % (Highest)", value: "recommended" },
  { label: "Closing Soon (Urgent)", value: "closing_soon" },
  { label: "Highest Vacancies", value: "vacancies" },
  { label: "Recently Added", value: "latest" },
];

export const FilterModal: React.FC<Props> = ({
  visible,
  onClose,
  filters,
  onApply,
  onReset,
}) => {
  const { colors } = useTheme();
  const styles = useStyles();

  const [localFilters, setLocalFilters] = useState<FilterState>(filters);

  // Sync with prop when opened
  React.useEffect(() => {
    if (visible) {
      setLocalFilters(filters);
    }
  }, [visible, filters]);

  const handleApply = () => {
    onApply(localFilters);
    onClose();
  };

  const handleReset = () => {
    const defaultFilters: FilterState = {
      category: "All Categories",
      job_type: "All Types",
      state: "All India",
      qualification: "All Qualifications",
      sort_by: "recommended",
    };
    setLocalFilters(defaultFilters);
    onReset();
    onClose();
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={true}
      onRequestClose={onClose}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContainer}>
          {/* Header */}
          <View style={styles.modalHeader}>
            <View>
              <Text style={styles.modalTitle}>Filter Govt Jobs</Text>
              <Text style={styles.modalSubtitle}>Refine by state, sector & degree</Text>
            </View>
            <Pressable
              testID="close-filter-modal-btn"
              onPress={onClose}
              hitSlop={8}
              style={styles.closeBtn}
            >
              <X size={20} color={colors.onSurface} />
            </Pressable>
          </View>

          {/* Body */}
          <ScrollView
            style={styles.modalBody}
            contentContainerStyle={styles.modalScrollContent}
            showsVerticalScrollIndicator={false}
          >
            {/* Sort By */}
            <Text style={styles.sectionTitle}>Sort Results</Text>
            <View style={styles.chipGrid}>
              {SORT_OPTIONS.map((opt) => {
                const isSelected = localFilters.sort_by === opt.value;
                return (
                  <Pressable
                    key={opt.value}
                    testID={`filter-sort-${opt.value}`}
                    onPress={() => setLocalFilters({ ...localFilters, sort_by: opt.value })}
                    style={[styles.chip, isSelected && styles.chipSelected]}
                  >
                    <Text
                      style={[styles.chipText, isSelected && styles.chipTextSelected]}
                    >
                      {opt.label}
                    </Text>
                    {isSelected && <Check size={14} color={colors.onBrandPrimary} />}
                  </Pressable>
                );
              })}
            </View>

            {/* Job Type (Central vs State) */}
            <Text style={styles.sectionTitle}>Government Level</Text>
            <View style={styles.chipGrid}>
              {JOB_TYPES.map((type) => {
                const isSelected = localFilters.job_type === type;
                return (
                  <Pressable
                    key={type}
                    testID={`filter-type-${type}`}
                    onPress={() => setLocalFilters({ ...localFilters, job_type: type })}
                    style={[styles.chip, isSelected && styles.chipSelected]}
                  >
                    <Text
                      style={[styles.chipText, isSelected && styles.chipTextSelected]}
                    >
                      {type}
                    </Text>
                    {isSelected && <Check size={14} color={colors.onBrandPrimary} />}
                  </Pressable>
                );
              })}
            </View>

            {/* Category / Sector */}
            <Text style={styles.sectionTitle}>Category & Board</Text>
            <View style={styles.chipGrid}>
              {CATEGORIES.map((cat) => {
                const isSelected = localFilters.category === cat;
                return (
                  <Pressable
                    key={cat}
                    testID={`filter-category-${cat.replace(/\s+/g, "-")}`}
                    onPress={() => setLocalFilters({ ...localFilters, category: cat })}
                    style={[styles.chip, isSelected && styles.chipSelected]}
                  >
                    <Text
                      style={[styles.chipText, isSelected && styles.chipTextSelected]}
                    >
                      {cat}
                    </Text>
                    {isSelected && <Check size={14} color={colors.onBrandPrimary} />}
                  </Pressable>
                );
              })}
            </View>

            {/* Education Degree */}
            <Text style={styles.sectionTitle}>Minimum Qualification</Text>
            <View style={styles.chipGrid}>
              {QUALIFICATIONS.map((qual) => {
                const isSelected = localFilters.qualification === qual;
                return (
                  <Pressable
                    key={qual}
                    testID={`filter-qual-${qual.replace(/\s+/g, "-")}`}
                    onPress={() => setLocalFilters({ ...localFilters, qualification: qual })}
                    style={[styles.chip, isSelected && styles.chipSelected]}
                  >
                    <Text
                      style={[styles.chipText, isSelected && styles.chipTextSelected]}
                    >
                      {qual}
                    </Text>
                    {isSelected && <Check size={14} color={colors.onBrandPrimary} />}
                  </Pressable>
                );
              })}
            </View>

            {/* State Domicile */}
            <Text style={styles.sectionTitle}>State / Region</Text>
            <View style={styles.chipGrid}>
              {STATES.map((st) => {
                const isSelected = localFilters.state === st;
                return (
                  <Pressable
                    key={st}
                    testID={`filter-state-${st.replace(/\s+/g, "-")}`}
                    onPress={() => setLocalFilters({ ...localFilters, state: st })}
                    style={[styles.chip, isSelected && styles.chipSelected]}
                  >
                    <Text
                      style={[styles.chipText, isSelected && styles.chipTextSelected]}
                    >
                      {st}
                    </Text>
                    {isSelected && <Check size={14} color={colors.onBrandPrimary} />}
                  </Pressable>
                );
              })}
            </View>
          </ScrollView>

          {/* Footer Actions */}
          <View style={styles.modalFooter}>
            <Pressable
              testID="reset-filters-btn"
              style={styles.resetBtn}
              onPress={handleReset}
            >
              <RotateCcw size={16} color={colors.onSurface} />
              <Text style={styles.resetBtnText}>Reset All</Text>
            </Pressable>

            <Pressable
              testID="apply-filters-btn"
              style={styles.applyBtn}
              onPress={handleApply}
            >
              <Text style={styles.applyBtnText}>Apply Filters</Text>
            </Pressable>
          </View>
        </View>
      </View>
    </Modal>
  );
};

const useStyles = makeStyles((colors) => ({
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
    minHeight: "50%",
    paddingBottom: 24,
  },
  modalHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 20,
    paddingTop: 18,
    paddingBottom: 14,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: colors.onSurface,
  },
  modalSubtitle: {
    fontSize: 12,
    color: colors.muted,
    marginTop: 2,
  },
  closeBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.surfaceSecondary,
    alignItems: "center",
    justifyContent: "center",
  },
  modalBody: {
    paddingHorizontal: 20,
  },
  modalScrollContent: {
    paddingVertical: 14,
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: "700",
    color: colors.brandPrimary,
    textTransform: "uppercase",
    letterSpacing: 0.5,
    marginTop: 14,
    marginBottom: 8,
  },
  chipGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  chip: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surfaceSecondary,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    gap: 6,
  },
  chipSelected: {
    backgroundColor: colors.brandPrimary,
    borderColor: colors.brandPrimary,
  },
  chipText: {
    fontSize: 13,
    color: colors.onSurfaceSecondary,
    fontWeight: "500",
  },
  chipTextSelected: {
    color: colors.onBrandPrimary,
    fontWeight: "700",
  },
  modalFooter: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 20,
    paddingTop: 14,
    borderTopWidth: 1,
    borderTopColor: colors.divider,
    gap: 12,
  },
  resetBtn: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surfaceSecondary,
    gap: 6,
    minHeight: 44,
  },
  resetBtnText: {
    fontSize: 14,
    fontWeight: "600",
    color: colors.onSurface,
  },
  applyBtn: {
    flex: 1,
    backgroundColor: colors.brandPrimary,
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: "center",
    justifyContent: "center",
    minHeight: 44,
  },
  applyBtnText: {
    fontSize: 15,
    fontWeight: "700",
    color: colors.onBrandPrimary,
  },
}));
