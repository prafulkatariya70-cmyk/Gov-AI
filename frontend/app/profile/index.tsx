import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  ScrollView,
  Pressable,
  ActivityIndicator,
  Alert,
} from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/src/api/apiClient";
import { useTheme, makeStyles } from "@/src/theme";
import {
  ArrowLeft,
  Save,
  UserCheck,
  Calendar,
  Sparkles,
  GraduationCap,
  MapPin,
  ShieldCheck,
  Check,
  AlertCircle,
} from "lucide-react-native";

const CATEGORIES = [
  { label: "General / Unreserved (UR)", val: "General", relaxation: "0 Years" },
  { label: "OBC (Non-Creamy Layer)", val: "OBC-NCL", relaxation: "+3 Years" },
  { label: "Scheduled Caste (SC)", val: "SC", relaxation: "+5 Years" },
  { label: "Scheduled Tribe (ST)", val: "ST", relaxation: "+5 Years" },
  { label: "Economically Weaker Section (EWS)", val: "EWS", relaxation: "0 Years" },
  { label: "Persons with Benchmark Disabilities (PwD)", val: "PwD", relaxation: "+10 Years" },
  { label: "Ex-Servicemen (Defense)", val: "Ex-Servicemen", relaxation: "+5 Years" },
];

const QUALIFICATIONS = [
  "10th Pass",
  "12th Pass",
  "Diploma (Polytechnic)",
  "Graduate",
  "B.Tech/B.E.",
  "Post Graduate",
  "MBBS / Medical",
  "LLB (Law)",
  "B.Ed (Teaching)",
];

const STATES = [
  "Uttar Pradesh",
  "Bihar",
  "Delhi",
  "Rajasthan",
  "Maharashtra",
  "Madhya Pradesh",
  "Karnataka",
  "Tamil Nadu",
  "West Bengal",
  "Gujarat",
  "Telangana",
  "Andhra Pradesh",
  "Haryana",
  "Punjab",
  "Kerala",
  "Odisha",
  "Assam",
  "Jharkhand",
  "Chhattisgarh",
  "Uttarakhand",
  "Himachal Pradesh",
];

const CERTIFICATIONS = [
  "CCC Computer Certification",
  "B.Ed Degree",
  "Typing Speed 35 WPM English",
  "Typing Speed 30 WPM Hindi",
  "Driving License LMV",
  "CTET Paper 1/2 Qualified",
  "NCC 'B' or 'C' Certificate",
];

export default function ProfileScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { colors } = useTheme();
  const styles = useStyles();
  const queryClient = useQueryClient();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [dob, setDob] = useState("2000-08-14");
  const [category, setCategory] = useState("OBC-NCL");
  const [gender, setGender] = useState("Male");
  const [domicileState, setDomicileState] = useState("Uttar Pradesh");
  const [qualification, setQualification] = useState("B.Tech/B.E.");
  const [stream, setStream] = useState("Computer Science & Engineering");
  const [heightCm, setHeightCm] = useState("175");
  const [selectedCerts, setSelectedCerts] = useState<string[]>([]);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const { data: profile, isLoading } = useQuery({
    queryKey: ["profile"],
    queryFn: () => api.getProfile(),
  });

  useEffect(() => {
    if (profile) {
      setFullName(profile.full_name || "");
      setEmail(profile.email || "");
      setPhone(profile.phone || "");
      setDob(profile.dob || "2000-08-14");
      setCategory(profile.category || "OBC-NCL");
      setGender(profile.gender || "Male");
      setDomicileState(profile.domicile_state || "Uttar Pradesh");
      setQualification(profile.qualification || "B.Tech/B.E.");
      setStream(profile.stream || "Computer Science");
      setHeightCm(String(profile.height_cm || 175));
      setSelectedCerts(profile.additional_certs || []);
    }
  }, [profile]);

  const updateProfileMutation = useMutation({
    mutationFn: (data: any) => api.updateProfile(data),
    onSuccess: () => {
      setSaveSuccess(true);
      queryClient.invalidateQueries({ queryKey: ["profile"] });
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      queryClient.invalidateQueries({ queryKey: ["recommended-jobs"] });
      setTimeout(() => {
        setSaveSuccess(false);
        router.back();
      }, 1000);
    },
  });

  const handleToggleCert = (cert: string) => {
    if (selectedCerts.includes(cert)) {
      setSelectedCerts(selectedCerts.filter((c) => c !== cert));
    } else {
      setSelectedCerts([...selectedCerts, cert]);
    }
  };

  const handleSave = () => {
    updateProfileMutation.mutate({
      full_name: fullName,
      email,
      phone,
      dob,
      category,
      gender,
      domicile_state: domicileState,
      qualification,
      stream,
      height_cm: parseInt(heightCm, 10) || 170,
      additional_certs: selectedCerts,
    });
  };

  // Live Age computation
  const calculatedAge = React.useMemo(() => {
    try {
      const birth = new Date(dob);
      const now = new Date();
      let age = now.getFullYear() - birth.getFullYear();
      const m = now.getMonth() - birth.getMonth();
      if (m < 0 || (m === 0 && now.getDate() < birth.getDate())) {
        age--;
      }
      return isNaN(age) ? 25 : age;
    } catch {
      return 25;
    }
  }, [dob]);

  if (isLoading) {
    return (
      <View style={[styles.screen, styles.centerContainer, { paddingTop: insets.top }]}>
        <ActivityIndicator size="large" color={colors.brandPrimary} />
      </View>
    );
  }

  return (
    <View style={[styles.screen, { paddingTop: insets.top }]}>
      {/* Top Header */}
      <View style={styles.topHeader}>
        <Pressable
          testID="profile-back-btn"
          style={styles.headerIconBtn}
          onPress={() => router.back()}
          hitSlop={8}
        >
          <ArrowLeft size={18} color={colors.onSurface} />
        </Pressable>

        <Text style={styles.headerTitleText}>Candidate Eligibility Profile</Text>

        <Pressable
          testID="save-profile-top-btn"
          style={styles.saveTopBtn}
          onPress={handleSave}
          disabled={updateProfileMutation.isPending}
        >
          {updateProfileMutation.isPending ? (
            <ActivityIndicator size="small" color={colors.onBrandPrimary} />
          ) : (
            <Text style={styles.saveTopBtnText}>Save</Text>
          )}
        </Pressable>
      </View>

      {/* Main Form Scroll */}
      <ScrollView
        contentContainerStyle={[styles.scrollContent, { paddingBottom: 120 }]}
        showsVerticalScrollIndicator={false}
      >
        {/* Success Banner */}
        {saveSuccess && (
          <View style={styles.successBanner}>
            <Check size={16} color="#15803D" />
            <Text style={styles.successBannerText}>
              Profile Saved! Eligibility scores recalculated for all jobs.
            </Text>
          </View>
        )}

        {/* Live Age & Relaxation Callout */}
        <View style={styles.liveCalculationBox}>
          <Sparkles size={18} color={colors.brandPrimary} />
          <View style={{ flex: 1 }}>
            <Text style={styles.liveAgeText}>
              Current Calculated Age: <Text style={{ color: colors.brandPrimary }}>{calculatedAge} Years</Text>
            </Text>
            <Text style={styles.liveRelaxationText}>
              Category: {category} ({CATEGORIES.find((c) => c.val === category)?.relaxation} relaxation applicable in central & state exams)
            </Text>
          </View>
        </View>

        {/* Section 1: Basic Information */}
        <Text style={styles.formSectionHeader}>1. Personal Identity</Text>

        <Text style={styles.inputLabel}>Full Name</Text>
        <TextInput
          testID="profile-name-input"
          style={styles.textInput}
          placeholder="Candidate Full Name"
          placeholderTextColor={colors.muted}
          value={fullName}
          onChangeText={setFullName}
        />

        <Text style={styles.inputLabel}>Date of Birth (YYYY-MM-DD)</Text>
        <TextInput
          testID="profile-dob-input"
          style={styles.textInput}
          placeholder="2000-08-14"
          placeholderTextColor={colors.muted}
          value={dob}
          onChangeText={setDob}
        />

        <Text style={styles.inputLabel}>Gender</Text>
        <View style={styles.chipRow}>
          {["Male", "Female", "Other"].map((g) => (
            <Pressable
              key={g}
              testID={`profile-gender-${g.toLowerCase()}`}
              style={[styles.choiceChip, gender === g && styles.choiceChipActive]}
              onPress={() => setGender(g)}
            >
              <Text
                style={[
                  styles.choiceChipText,
                  gender === g && styles.choiceChipTextActive,
                ]}
              >
                {g}
              </Text>
            </Pressable>
          ))}
        </View>

        {/* Section 2: Reservation & Domicile */}
        <Text style={styles.formSectionHeader}>2. Category & State Domicile</Text>

        <Text style={styles.inputLabel}>Reservation Category</Text>
        <View style={styles.categoryChoicesList}>
          {CATEGORIES.map((cat) => {
            const isSelected = category === cat.val;
            return (
              <Pressable
                key={cat.val}
                testID={`profile-category-${cat.val}`}
                style={[styles.categoryCard, isSelected && styles.categoryCardActive]}
                onPress={() => setCategory(cat.val)}
              >
                <View style={{ flex: 1 }}>
                  <Text style={[styles.catName, isSelected && styles.catNameActive]}>
                    {cat.label}
                  </Text>
                  <Text style={styles.catRelaxation}>
                    Age Relaxation Benefit: {cat.relaxation}
                  </Text>
                </View>
                {isSelected && <Check size={16} color={colors.brandPrimary} />}
              </Pressable>
            );
          })}
        </View>

        <Text style={styles.inputLabel}>State of Domicile</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.horizontalChips}>
          {STATES.map((st) => (
            <Pressable
              key={st}
              testID={`profile-state-${st.replace(/\s+/g, "-")}`}
              style={[
                styles.choiceChip,
                domicileState === st && styles.choiceChipActive,
              ]}
              onPress={() => setDomicileState(st)}
            >
              <Text
                style={[
                  styles.choiceChipText,
                  domicileState === st && styles.choiceChipTextActive,
                ]}
              >
                {st}
              </Text>
            </Pressable>
          ))}
        </ScrollView>

        {/* Section 3: Educational Qualifications */}
        <Text style={styles.formSectionHeader}>3. Educational Qualifications</Text>

        <Text style={styles.inputLabel}>Highest Qualification Level</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.horizontalChips}>
          {QUALIFICATIONS.map((q) => (
            <Pressable
              key={q}
              testID={`profile-qual-${q.replace(/\s+/g, "-")}`}
              style={[
                styles.choiceChip,
                qualification === q && styles.choiceChipActive,
              ]}
              onPress={() => setQualification(q)}
            >
              <Text
                style={[
                  styles.choiceChipText,
                  qualification === q && styles.choiceChipTextActive,
                ]}
              >
                {q}
              </Text>
            </Pressable>
          ))}
        </ScrollView>

        <Text style={styles.inputLabel}>Degree Name & Specialization Stream</Text>
        <TextInput
          testID="profile-stream-input"
          style={styles.textInput}
          placeholder="e.g. B.Tech Computer Science / B.Com / B.A History"
          placeholderTextColor={colors.muted}
          value={stream}
          onChangeText={setStream}
        />

        {/* Section 4: Physical & Certifications */}
        <Text style={styles.formSectionHeader}>4. Physical Standards & Certifications</Text>

        <Text style={styles.inputLabel}>Height (cm) - for Police & Defense</Text>
        <TextInput
          testID="profile-height-input"
          style={styles.textInput}
          placeholder="175"
          placeholderTextColor={colors.muted}
          keyboardType="numeric"
          value={heightCm}
          onChangeText={setHeightCm}
        />

        <Text style={styles.inputLabel}>Additional Certifications & Skills</Text>
        <View style={styles.certsGrid}>
          {CERTIFICATIONS.map((cert) => {
            const isChecked = selectedCerts.includes(cert);
            return (
              <Pressable
                key={cert}
                testID={`profile-cert-${cert.replace(/\s+/g, "-")}`}
                style={[styles.certChip, isChecked && styles.certChipActive]}
                onPress={() => handleToggleCert(cert)}
              >
                <Text style={[styles.certChipText, isChecked && styles.certChipTextActive]}>
                  {cert}
                </Text>
                {isChecked && <Check size={14} color={colors.onBrandPrimary} />}
              </Pressable>
            );
          })}
        </View>
      </ScrollView>

      {/* Sticky Bottom Save CTA */}
      <View style={[styles.bottomBar, { paddingBottom: Math.max(insets.bottom, 14) }]}>
        <Pressable
          testID="save-profile-bottom-btn"
          style={styles.saveBottomBtn}
          onPress={handleSave}
          disabled={updateProfileMutation.isPending}
        >
          {updateProfileMutation.isPending ? (
            <ActivityIndicator size="small" color={colors.onBrandPrimary} />
          ) : (
            <>
              <Save size={16} color={colors.onBrandPrimary} />
              <Text style={styles.saveBottomBtnText}>Save Candidate Profile</Text>
            </>
          )}
        </Pressable>
      </View>
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
  saveTopBtn: {
    backgroundColor: colors.brandPrimary,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
  },
  saveTopBtnText: {
    color: colors.onBrandPrimary,
    fontWeight: "700",
    fontSize: 12,
  },
  scrollContent: {
    paddingHorizontal: 16,
    paddingTop: 14,
  },
  successBanner: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#DCFCE7",
    borderColor: "#86EFAC",
    borderWidth: 1,
    padding: 12,
    borderRadius: 10,
    gap: 8,
    marginBottom: 14,
  },
  successBannerText: {
    fontSize: 12,
    fontWeight: "600",
    color: "#15803D",
    flex: 1,
  },
  liveCalculationBox: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1.5,
    borderColor: colors.brandSecondary,
    borderRadius: 12,
    padding: 12,
    gap: 10,
    marginBottom: 14,
  },
  liveAgeText: {
    fontSize: 14,
    fontWeight: "700",
    color: colors.onSurface,
  },
  liveRelaxationText: {
    fontSize: 11,
    color: colors.muted,
    marginTop: 2,
  },
  formSectionHeader: {
    fontSize: 13,
    fontWeight: "800",
    color: colors.brandPrimary,
    textTransform: "uppercase",
    letterSpacing: 0.5,
    marginTop: 14,
    marginBottom: 8,
  },
  inputLabel: {
    fontSize: 12,
    fontWeight: "700",
    color: colors.onSurface,
    marginBottom: 6,
    marginTop: 6,
  },
  textInput: {
    backgroundColor: colors.surfaceSecondary,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 13,
    color: colors.onSurface,
    marginBottom: 8,
  },
  chipRow: {
    flexDirection: "row",
    gap: 8,
    marginBottom: 8,
  },
  horizontalChips: {
    flexDirection: "row",
    marginBottom: 8,
  },
  choiceChip: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: colors.surfaceSecondary,
    borderColor: colors.border,
    borderWidth: 1,
    marginRight: 8,
  },
  choiceChipActive: {
    backgroundColor: colors.brandPrimary,
    borderColor: colors.brandPrimary,
  },
  choiceChipText: {
    fontSize: 12,
    fontWeight: "600",
    color: colors.onSurfaceSecondary,
  },
  choiceChipTextActive: {
    color: colors.onBrandPrimary,
    fontWeight: "700",
  },
  categoryChoicesList: {
    gap: 6,
    marginBottom: 8,
  },
  categoryCard: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    backgroundColor: colors.surfaceSecondary,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 8,
    padding: 10,
  },
  categoryCardActive: {
    borderColor: colors.brandPrimary,
    backgroundColor: colors.brandTertiary,
  },
  catName: {
    fontSize: 12,
    fontWeight: "600",
    color: colors.onSurface,
  },
  catNameActive: {
    color: colors.onBrandTertiary,
    fontWeight: "700",
  },
  catRelaxation: {
    fontSize: 11,
    color: colors.muted,
    marginTop: 2,
  },
  certsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginBottom: 10,
  },
  certChip: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surfaceSecondary,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 7,
    gap: 6,
  },
  certChipActive: {
    backgroundColor: colors.brandPrimary,
    borderColor: colors.brandPrimary,
  },
  certChipText: {
    fontSize: 12,
    color: colors.onSurfaceSecondary,
    fontWeight: "500",
  },
  certChipTextActive: {
    color: colors.onBrandPrimary,
    fontWeight: "700",
  },
  bottomBar: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: colors.surface,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    paddingHorizontal: 16,
    paddingTop: 10,
  },
  saveBottomBtn: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.brandPrimary,
    paddingVertical: 14,
    borderRadius: 10,
    gap: 8,
    minHeight: 48,
  },
  saveBottomBtnText: {
    fontSize: 15,
    fontWeight: "700",
    color: colors.onBrandPrimary,
  },
}));
