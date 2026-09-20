import React from "react";
import {
  View,
  Text,
  Modal,
  Pressable,
  ScrollView,
  Linking,
} from "react-native";
import { useTheme, makeStyles } from "@/src/theme";
import { Job } from "@/src/types";
import {
  X,
  FileText,
  Download,
  ExternalLink,
  ShieldCheck,
  Calendar,
  IndianRupee,
  AlertTriangle,
} from "lucide-react-native";

interface Props {
  visible: boolean;
  onClose: () => void;
  job: Job;
}

export const OfficialNotificationModal: React.FC<Props> = ({
  visible,
  onClose,
  job,
}) => {
  const { colors } = useTheme();
  const styles = useStyles();

  const handleOpenPdf = () => {
    if (job.official_notification_pdf_url) {
      Linking.openURL(job.official_notification_pdf_url).catch((err) =>
        console.error("Error opening notification PDF", err)
      );
    }
  };

  const handleOpenOfficialSite = () => {
    if (job.official_website_url) {
      Linking.openURL(job.official_website_url).catch((err) =>
        console.error("Error opening official website", err)
      );
    }
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={true}
      onRequestClose={onClose}
    >
      <View style={styles.overlay}>
        <View style={styles.container}>
          {/* Header */}
          <View style={styles.header}>
            <View style={styles.headerTitleBox}>
              <FileText size={18} color={colors.brandPrimary} />
              <View>
                <Text style={styles.title}>Official Gazette Notice</Text>
                <Text style={styles.subtitle}>{job.board_code} • {job.title}</Text>
              </View>
            </View>
            <Pressable
              testID="close-notification-modal-btn"
              onPress={onClose}
              hitSlop={8}
              style={styles.closeBtn}
            >
              <X size={20} color={colors.onSurface} />
            </Pressable>
          </View>

          {/* Document Content */}
          <ScrollView style={styles.body} contentContainerStyle={styles.scrollContent}>
            {/* Seal & Board Banner */}
            <View style={styles.gazetteSealBanner}>
              <ShieldCheck size={24} color={colors.brandPrimary} />
              <View style={{ flex: 1 }}>
                <Text style={styles.sealBoardText}>{job.board}</Text>
                <Text style={styles.gazetteSub}>Govt of India / State Gazette Publication</Text>
              </View>
            </View>

            {/* Notification Summary */}
            <View style={styles.sectionCard}>
              <Text style={styles.cardHeader}>1. Vacancy & Post Summary</Text>
              <Text style={styles.bodyText}>
                Online applications are invited for recruitment to the post of{" "}
                <Text style={{ fontWeight: "700" }}>{job.post_name}</Text> ({job.job_type} Government Service) for total{" "}
                <Text style={{ fontWeight: "700" }}>{job.total_vacancies.toLocaleString("en-IN")}</Text> advertised positions.
              </Text>
            </View>

            {/* Crucial Dates */}
            <View style={styles.sectionCard}>
              <Text style={styles.cardHeader}>2. Crucial Schedule & Timeline</Text>
              <View style={styles.dateRow}>
                <Calendar size={14} color={colors.muted} />
                <Text style={styles.dateLabel}>Notification Released:</Text>
                <Text style={styles.dateVal}>{job.notification_date}</Text>
              </View>
              <View style={styles.dateRow}>
                <Calendar size={14} color={colors.brandPrimary} />
                <Text style={styles.dateLabel}>Online Application Window:</Text>
                <Text style={styles.dateVal}>{job.start_date} to {job.last_date}</Text>
              </View>
              <View style={styles.dateRow}>
                <Calendar size={14} color={colors.error} />
                <Text style={styles.dateLabel}>Tentative Exam Date:</Text>
                <Text style={styles.dateVal}>{job.exam_date}</Text>
              </View>
            </View>

            {/* Eligibility & Relaxation */}
            <View style={styles.sectionCard}>
              <Text style={styles.cardHeader}>3. Minimum Prescribed Eligibility</Text>
              <Text style={styles.bodyText}>
                • <Text style={{ fontWeight: "700" }}>Educational Qualification:</Text> {job.qualification_details}
              </Text>
              <Text style={styles.bodyText}>
                • <Text style={{ fontWeight: "700" }}>Age Limit:</Text> {job.min_age} to {job.max_age} years (Relaxation: OBC +3y, SC/ST +5y, PwD +10y as per Govt rules).
              </Text>
              <Text style={styles.bodyText}>
                • <Text style={{ fontWeight: "700" }}>Domicile Clause:</Text> {job.domicile_rule}
              </Text>
            </View>

            {/* Pay Scale & Emoluments */}
            <View style={styles.sectionCard}>
              <Text style={styles.cardHeader}>4. Pay Scale & Emoluments</Text>
              <View style={styles.dateRow}>
                <IndianRupee size={14} color={colors.success} />
                <Text style={styles.dateLabel}>Pay Band:</Text>
                <Text style={styles.dateVal}>{job.salary_scale}</Text>
              </View>
              <Text style={[styles.bodyText, { marginTop: 4 }]}>
                Estimated In-Hand Salary: <Text style={{ fontWeight: "700" }}>{job.in_hand_salary}</Text>
              </Text>
            </View>

            {/* Important Candidate Instructions */}
            {job.important_instructions && job.important_instructions.length > 0 && (
              <View style={[styles.sectionCard, { backgroundColor: "#FFFBEB", borderColor: "#FCD34D" }]}>
                <View style={{ flexDirection: "row", alignItems: "center", gap: 6, marginBottom: 6 }}>
                  <AlertTriangle size={15} color="#B45309" />
                  <Text style={[styles.cardHeader, { color: "#B45309", marginBottom: 0 }]}>Important Gazette Instructions</Text>
                </View>
                {job.important_instructions.map((inst, idx) => (
                  <Text key={idx} style={[styles.bodyText, { color: "#78350F", marginBottom: 4 }]}>
                    {idx + 1}. {inst}
                  </Text>
                ))}
              </View>
            )}
          </ScrollView>

          {/* Footer CTAs */}
          <View style={styles.footer}>
            <Pressable
              testID="open-official-site-btn"
              style={styles.outlineBtn}
              onPress={handleOpenOfficialSite}
            >
              <ExternalLink size={15} color={colors.brandPrimary} />
              <Text style={styles.outlineBtnText}>Board Website</Text>
            </Pressable>

            <Pressable
              testID="download-official-pdf-btn"
              style={styles.primaryBtn}
              onPress={handleOpenPdf}
            >
              <Download size={15} color={colors.onBrandPrimary} />
              <Text style={styles.primaryBtnText}>Download PDF</Text>
            </Pressable>
          </View>
        </View>
      </View>
    </Modal>
  );
};

const useStyles = makeStyles((colors) => ({
  overlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.6)",
    justifyContent: "flex-end",
  },
  container: {
    backgroundColor: colors.surface,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: "90%",
    minHeight: "65%",
    paddingBottom: 24,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 20,
    paddingTop: 18,
    paddingBottom: 14,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  headerTitleBox: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    flex: 1,
    paddingRight: 8,
  },
  title: {
    fontSize: 16,
    fontWeight: "700",
    color: colors.onSurface,
  },
  subtitle: {
    fontSize: 12,
    color: colors.muted,
  },
  closeBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.surfaceSecondary,
    alignItems: "center",
    justifyContent: "center",
  },
  body: {
    paddingHorizontal: 20,
  },
  scrollContent: {
    paddingVertical: 16,
  },
  gazetteSealBanner: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surfaceTertiary,
    padding: 12,
    borderRadius: 10,
    gap: 10,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: colors.border,
  },
  sealBoardText: {
    fontSize: 13,
    fontWeight: "700",
    color: colors.onSurface,
  },
  gazetteSub: {
    fontSize: 11,
    color: colors.muted,
  },
  sectionCard: {
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    padding: 12,
    marginBottom: 12,
  },
  cardHeader: {
    fontSize: 13,
    fontWeight: "700",
    color: colors.brandPrimary,
    marginBottom: 6,
  },
  bodyText: {
    fontSize: 12,
    color: colors.onSurfaceSecondary,
    lineHeight: 18,
    marginBottom: 4,
  },
  dateRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    marginVertical: 3,
  },
  dateLabel: {
    fontSize: 12,
    color: colors.muted,
    fontWeight: "500",
  },
  dateVal: {
    fontSize: 12,
    color: colors.onSurface,
    fontWeight: "700",
    marginLeft: "auto",
  },
  footer: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 20,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: colors.divider,
    gap: 12,
  },
  outlineBtn: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 12,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: colors.brandPrimary,
    backgroundColor: colors.surface,
    gap: 6,
    minHeight: 44,
  },
  outlineBtnText: {
    fontSize: 13,
    fontWeight: "700",
    color: colors.brandPrimary,
  },
  primaryBtn: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 12,
    borderRadius: 10,
    backgroundColor: colors.brandPrimary,
    gap: 6,
    minHeight: 44,
  },
  primaryBtnText: {
    fontSize: 13,
    fontWeight: "700",
    color: colors.onBrandPrimary,
  },
}));
