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
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/src/api/apiClient";
import { useTheme, makeStyles } from "@/src/theme";
import {
  Flame,
  Award,
  BookOpen,
  HelpCircle,
  CheckCircle2,
  XCircle,
  Zap,
  Sparkles,
  Quote,
  ShieldCheck,
  ChevronRight,
  RotateCcw,
} from "lucide-react-native";

export default function DailyCapsuleScreen() {
  const insets = useSafeAreaInsets();
  const { colors } = useTheme();
  const styles = useStyles();
  const queryClient = useQueryClient();

  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, number>>({});
  const [quizSubmitted, setQuizSubmitted] = useState(false);
  const [quizResults, setQuizResults] = useState<any>(null);

  const {
    data: capsuleData,
    isLoading,
    isRefetching,
    refetch,
  } = useQuery({
    queryKey: ["daily-capsule"],
    queryFn: () => api.getDailyCapsule(),
  });

  // Mutations
  const checkinMutation = useMutation({
    mutationFn: () => api.checkinDaily(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["daily-capsule"] });
      queryClient.invalidateQueries({ queryKey: ["profile"] });
    },
  });

  const submitQuizMutation = useMutation({
    mutationFn: (answers: Record<string, number>) => api.submitQuiz(answers),
    onSuccess: (data) => {
      setQuizSubmitted(true);
      setQuizResults(data);
      queryClient.invalidateQueries({ queryKey: ["daily-capsule"] });
      queryClient.invalidateQueries({ queryKey: ["profile"] });
    },
  });

  const capsule = capsuleData?.capsule;
  const streakCount = capsuleData?.user_streak || 0;
  const userPoints = capsuleData?.user_points || 0;
  const isCheckedIn = capsuleData?.is_checked_in_today || false;

  const handleSelectOption = (questionId: string, optionIndex: number) => {
    if (quizSubmitted) return;
    setSelectedAnswers((prev) => ({
      ...prev,
      [questionId]: optionIndex,
    }));
  };

  const handleSubmitQuiz = () => {
    submitQuizMutation.mutate(selectedAnswers);
  };

  const handleRetakeQuiz = () => {
    setSelectedAnswers({});
    setQuizSubmitted(false);
    setQuizResults(null);
  };

  const questions = capsule?.quiz_questions || [];
  const currentAffairs = capsule?.current_affairs || [];
  const answeredCount = Object.keys(selectedAnswers).length;

  return (
    <View style={[styles.screen, { paddingTop: insets.top }]}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerRow}>
          <View>
            <View style={styles.titleRow}>
              <Flame size={22} color="#EA580C" fill="#EA580C" />
              <Text style={styles.headerTitle}>Daily GK & Habit Hub</Text>
            </View>
            <Text style={styles.headerSubtitle}>
              Daily current affairs, polity bytes & mini test series
            </Text>
          </View>

          <View style={styles.pointsBadge}>
            <Award size={14} color={colors.brandPrimary} />
            <Text style={styles.pointsText}>{userPoints} XP</Text>
          </View>
        </View>

        {/* Daily Streak Card */}
        <View style={styles.streakHeroBox}>
          <View style={{ flex: 1 }}>
            <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
              <Flame size={20} color="#EA580C" fill="#EA580C" />
              <Text style={styles.streakNumberText}>{streakCount} Days Active</Text>
            </View>
            <Text style={styles.streakSubText}>
              {isCheckedIn
                ? "Daily study streak maintained! Points credited."
                : "Claim today's check-in to build exam consistency."}
            </Text>
          </View>

          {!isCheckedIn ? (
            <Pressable
              testID="claim-daily-streak-btn"
              style={styles.checkinActionBtn}
              onPress={() => checkinMutation.mutate()}
              disabled={checkinMutation.isPending}
            >
              {checkinMutation.isPending ? (
                <ActivityIndicator size="small" color={colors.onBrandPrimary} />
              ) : (
                <>
                  <Zap size={14} color={colors.onBrandPrimary} fill={colors.onBrandPrimary} />
                  <Text style={styles.checkinActionText}>Claim +25 XP</Text>
                </>
              )}
            </Pressable>
          ) : (
            <View style={styles.claimedBadge}>
              <CheckCircle2 size={14} color="#15803D" />
              <Text style={styles.claimedBadgeText}>Checked In</Text>
            </View>
          )}
        </View>
      </View>

      {/* Main Content */}
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
            <Text style={styles.loadingText}>Curating today's high-yield GK bytes...</Text>
          </View>
        ) : (
          <>
            {/* Daily Quote / Theme */}
            {capsule?.daily_quote ? (
              <View style={styles.quoteCard}>
                <Quote size={20} color={colors.brandPrimary} style={{ opacity: 0.7 }} />
                <Text style={styles.quoteText}>{capsule.daily_quote}</Text>
                <Text style={styles.themeTag}>Focus: {capsule.theme}</Text>
              </View>
            ) : null}

            {/* Section 1: Daily Current Affairs Bytes */}
            <View style={styles.sectionHeaderRow}>
              <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
                <BookOpen size={16} color={colors.brandPrimary} />
                <Text style={styles.sectionHeading}>Today's Verified Current Affairs</Text>
              </View>
              <Text style={styles.sectionCountText}>{currentAffairs.length} Briefs</Text>
            </View>

            {currentAffairs.map((item, idx) => (
              <View key={idx} testID={`news-item-${idx}`} style={styles.newsCard}>
                <View style={styles.newsMetaRow}>
                  <View style={styles.newsCategoryBadge}>
                    <Text style={styles.newsCategoryText}>{item.category}</Text>
                  </View>
                  <Text style={styles.newsDateText}>{item.date}</Text>
                </View>

                <Text style={styles.newsTitle}>{item.title}</Text>
                <Text style={styles.newsSummary}>{item.summary}</Text>

                <View style={styles.relevanceBox}>
                  <Sparkles size={12} color={colors.brandPrimary} />
                  <Text style={styles.relevanceText}>
                    <Text style={{ fontWeight: "700" }}>Exam Utility:</Text> {item.exam_relevance}
                  </Text>
                </View>
              </View>
            ))}

            {/* Section 2: 5-Question Daily GK & Polity Quiz */}
            <View style={[styles.sectionHeaderRow, { marginTop: 18 }]}>
              <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
                <HelpCircle size={16} color={colors.brandPrimary} />
                <Text style={styles.sectionHeading}>Daily 5-Min Exam GK Quiz</Text>
              </View>
              {quizSubmitted ? (
                <View style={styles.scoreBadge}>
                  <Text style={styles.scoreBadgeText}>
                    Score: {quizResults?.score}/{quizResults?.total}
                  </Text>
                </View>
              ) : (
                <Text style={styles.sectionCountText}>{answeredCount}/5 Answered</Text>
              )}
            </View>

            {/* Quiz Result Feedback Banner */}
            {quizSubmitted && quizResults && (
              <View style={styles.quizFeedbackBanner}>
                <Award size={20} color="#15803D" />
                <View style={{ flex: 1 }}>
                  <Text style={styles.quizFeedbackTitle}>
                    {quizResults.feedback} (+{quizResults.points_earned} XP Earned)
                  </Text>
                  <Text style={styles.quizFeedbackSub}>
                    Review the detailed solutions and subject tags below.
                  </Text>
                </View>
                <Pressable
                  testID="retake-quiz-btn"
                  style={styles.retakeBtn}
                  onPress={handleRetakeQuiz}
                >
                  <RotateCcw size={12} color={colors.brandPrimary} />
                  <Text style={styles.retakeBtnText}>Retake</Text>
                </Pressable>
              </View>
            )}

            {/* Questions List */}
            {questions.map((q, qIdx) => {
              const selectedOpt = selectedAnswers[q.id];
              const resultItem = quizResults?.results?.find((r: any) => r.id === q.id);

              return (
                <View key={q.id} testID={`quiz-question-${q.id}`} style={styles.questionCard}>
                  <View style={styles.questionMetaRow}>
                    <Text style={styles.questionNum}>Question {qIdx + 1} of 5</Text>
                    <View style={styles.subjectBadge}>
                      <Text style={styles.subjectBadgeText}>{q.subject}</Text>
                    </View>
                  </View>

                  <Text style={styles.questionText}>{q.question}</Text>

                  {/* Options */}
                  <View style={styles.optionsList}>
                    {q.options.map((opt, optIdx) => {
                      const isSelected = selectedOpt === optIdx;
                      const isCorrect = q.correct_option_index === optIdx;
                      
                      let optionStyle = styles.optionItem;
                      let optionTextStyle = styles.optionText;

                      if (isSelected && !quizSubmitted) {
                        optionStyle = styles.optionItemSelected;
                        optionTextStyle = styles.optionTextSelected;
                      } else if (quizSubmitted) {
                        if (isCorrect) {
                          optionStyle = styles.optionItemCorrect;
                          optionTextStyle = styles.optionTextCorrect;
                        } else if (isSelected && !isCorrect) {
                          optionStyle = styles.optionItemWrong;
                          optionTextStyle = styles.optionTextWrong;
                        }
                      }

                      return (
                        <Pressable
                          key={optIdx}
                          testID={`quiz-q${q.id}-opt${optIdx}`}
                          style={optionStyle}
                          onPress={() => handleSelectOption(q.id, optIdx)}
                          disabled={quizSubmitted}
                        >
                          <View style={styles.optionIndexCircle}>
                            <Text style={styles.optionIndexChar}>
                              {String.fromCharCode(65 + optIdx)}
                            </Text>
                          </View>
                          <Text style={optionTextStyle}>{opt}</Text>
                          {quizSubmitted && isCorrect && (
                            <CheckCircle2 size={16} color="#15803D" style={{ marginLeft: "auto" }} />
                          )}
                          {quizSubmitted && isSelected && !isCorrect && (
                            <XCircle size={16} color="#B91C1C" style={{ marginLeft: "auto" }} />
                          )}
                        </Pressable>
                      );
                    })}
                  </View>

                  {/* Explanation after submission */}
                  {quizSubmitted && (
                    <View style={styles.explanationBox}>
                      <ShieldCheck size={14} color={colors.brandPrimary} />
                      <Text style={styles.explanationText}>
                        <Text style={{ fontWeight: "700" }}>Explanation: </Text>
                        {q.explanation}
                      </Text>
                    </View>
                  )}
                </View>
              );
            })}

            {/* Quiz Submit CTA */}
            {!quizSubmitted && questions.length > 0 && (
              <Pressable
                testID="submit-daily-quiz-btn"
                style={[
                  styles.submitQuizBtn,
                  answeredCount === 0 && styles.submitQuizBtnDisabled,
                ]}
                onPress={handleSubmitQuiz}
                disabled={answeredCount === 0 || submitQuizMutation.isPending}
              >
                {submitQuizMutation.isPending ? (
                  <ActivityIndicator size="small" color={colors.onBrandPrimary} />
                ) : (
                  <>
                    <Award size={16} color={colors.onBrandPrimary} />
                    <Text style={styles.submitQuizBtnText}>
                      Submit Daily Quiz ({answeredCount}/{questions.length})
                    </Text>
                  </>
                )}
              </Pressable>
            )}
          </>
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
  pointsBadge: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.brandTertiary,
    borderColor: colors.brandSecondary,
    borderWidth: 1,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
    gap: 4,
  },
  pointsText: {
    fontSize: 12,
    fontWeight: "700",
    color: colors.onBrandTertiary,
  },
  streakHeroBox: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surfaceSecondary,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 12,
    padding: 12,
    marginBottom: 10,
    justifyContent: "space-between",
  },
  streakNumberText: {
    fontSize: 15,
    fontWeight: "800",
    color: colors.onSurface,
  },
  streakSubText: {
    fontSize: 11,
    color: colors.muted,
    marginTop: 2,
  },
  checkinActionBtn: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.brandPrimary,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    gap: 4,
    minHeight: 36,
  },
  checkinActionText: {
    fontSize: 12,
    fontWeight: "700",
    color: colors.onBrandPrimary,
  },
  claimedBadge: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#DCFCE7",
    borderColor: "#86EFAC",
    borderWidth: 1,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
    gap: 4,
  },
  claimedBadgeText: {
    fontSize: 11,
    fontWeight: "700",
    color: "#15803D",
  },
  scrollContent: {
    paddingHorizontal: 16,
    paddingTop: 14,
    paddingBottom: 36,
  },
  quoteCard: {
    backgroundColor: colors.surfaceSecondary,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 12,
    padding: 14,
    marginBottom: 14,
  },
  quoteText: {
    fontSize: 13,
    fontStyle: "italic",
    color: colors.onSurface,
    lineHeight: 19,
    marginVertical: 6,
  },
  themeTag: {
    fontSize: 11,
    fontWeight: "600",
    color: colors.brandPrimary,
  },
  sectionHeaderRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 10,
  },
  sectionHeading: {
    fontSize: 14,
    fontWeight: "700",
    color: colors.onSurface,
  },
  sectionCountText: {
    fontSize: 11,
    color: colors.muted,
    fontWeight: "500",
  },
  scoreBadge: {
    backgroundColor: "#DCFCE7",
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  scoreBadgeText: {
    fontSize: 11,
    fontWeight: "700",
    color: "#15803D",
  },
  newsCard: {
    backgroundColor: colors.surfaceSecondary,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 12,
    padding: 12,
    marginBottom: 10,
  },
  newsMetaRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 6,
  },
  newsCategoryBadge: {
    backgroundColor: colors.surfaceTertiary,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  newsCategoryText: {
    fontSize: 10,
    fontWeight: "700",
    color: colors.brandPrimary,
  },
  newsDateText: {
    fontSize: 10,
    color: colors.muted,
  },
  newsTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: colors.onSurface,
    marginBottom: 4,
    lineHeight: 18,
  },
  newsSummary: {
    fontSize: 12,
    color: colors.onSurfaceSecondary,
    lineHeight: 17,
    marginBottom: 8,
  },
  relevanceBox: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surfaceTertiary,
    borderRadius: 6,
    padding: 6,
    gap: 6,
  },
  relevanceText: {
    fontSize: 11,
    color: colors.onSurfaceSecondary,
    flex: 1,
    lineHeight: 15,
  },
  quizFeedbackBanner: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#DCFCE7",
    borderColor: "#86EFAC",
    borderWidth: 1,
    padding: 12,
    borderRadius: 10,
    gap: 10,
    marginBottom: 12,
  },
  quizFeedbackTitle: {
    fontSize: 13,
    fontWeight: "700",
    color: "#15803D",
  },
  quizFeedbackSub: {
    fontSize: 11,
    color: "#166534",
  },
  retakeBtn: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    gap: 4,
  },
  retakeBtnText: {
    fontSize: 11,
    fontWeight: "600",
    color: colors.brandPrimary,
  },
  questionCard: {
    backgroundColor: colors.surfaceSecondary,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
  },
  questionMetaRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  questionNum: {
    fontSize: 11,
    fontWeight: "700",
    color: colors.muted,
  },
  subjectBadge: {
    backgroundColor: colors.surfaceTertiary,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  subjectBadgeText: {
    fontSize: 10,
    fontWeight: "600",
    color: colors.onSurfaceSecondary,
  },
  questionText: {
    fontSize: 14,
    fontWeight: "700",
    color: colors.onSurface,
    lineHeight: 20,
    marginBottom: 12,
  },
  optionsList: {
    gap: 8,
  },
  optionItem: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 8,
    padding: 10,
    gap: 8,
  },
  optionItemSelected: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.brandTertiary,
    borderColor: colors.brandPrimary,
    borderWidth: 1.5,
    borderRadius: 8,
    padding: 10,
    gap: 8,
  },
  optionItemCorrect: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#DCFCE7",
    borderColor: "#15803D",
    borderWidth: 1.5,
    borderRadius: 8,
    padding: 10,
    gap: 8,
  },
  optionItemWrong: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#FEE2E2",
    borderColor: "#B91C1C",
    borderWidth: 1.5,
    borderRadius: 8,
    padding: 10,
    gap: 8,
  },
  optionIndexCircle: {
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: colors.surfaceTertiary,
    alignItems: "center",
    justifyContent: "center",
  },
  optionIndexChar: {
    fontSize: 11,
    fontWeight: "700",
    color: colors.onSurfaceSecondary,
  },
  optionText: {
    fontSize: 13,
    color: colors.onSurface,
    flex: 1,
  },
  optionTextSelected: {
    fontSize: 13,
    color: colors.onBrandTertiary,
    fontWeight: "700",
    flex: 1,
  },
  optionTextCorrect: {
    fontSize: 13,
    color: "#15803D",
    fontWeight: "700",
    flex: 1,
  },
  optionTextWrong: {
    fontSize: 13,
    color: "#B91C1C",
    fontWeight: "700",
    flex: 1,
  },
  explanationBox: {
    flexDirection: "row",
    alignItems: "flex-start",
    backgroundColor: colors.surfaceTertiary,
    borderRadius: 8,
    padding: 10,
    gap: 8,
    marginTop: 10,
  },
  explanationText: {
    fontSize: 11,
    color: colors.onSurfaceSecondary,
    lineHeight: 16,
    flex: 1,
  },
  submitQuizBtn: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.brandPrimary,
    paddingVertical: 14,
    borderRadius: 10,
    gap: 8,
    marginTop: 6,
    minHeight: 48,
  },
  submitQuizBtnDisabled: {
    opacity: 0.5,
  },
  submitQuizBtnText: {
    fontSize: 15,
    fontWeight: "700",
    color: colors.onBrandPrimary,
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
}));
