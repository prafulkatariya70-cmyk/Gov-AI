import React from "react";
import { View, Text, Pressable, ActivityIndicator } from "react-native";
import { useTheme, makeStyles } from "@/src/theme";
import { Flame, Award, CheckCircle, ChevronRight, Zap } from "lucide-react-native";
import { useRouter } from "expo-router";

interface Props {
  streakCount: number;
  points: number;
  isCheckedInToday: boolean;
  onCheckIn: () => void;
  isLoading?: boolean;
}

export const DailyStreakCard: React.FC<Props> = ({
  streakCount,
  points,
  isCheckedInToday,
  onCheckIn,
  isLoading = false,
}) => {
  const router = useRouter();
  const { colors } = useTheme();
  const styles = useStyles();

  return (
    <View style={styles.card}>
      <View style={styles.leftCol}>
        <View style={styles.streakBadge}>
          <Flame size={18} color="#EA580C" fill="#EA580C" />
          <Text style={styles.streakCountText}>{streakCount} Day Streak</Text>
        </View>
        <Text style={styles.motivationText}>
          {isCheckedInToday
            ? "Daily habit completed! +25 Points added"
            : "Check in today to maintain your exam prep streak!"}
        </Text>
      </View>

      <View style={styles.rightCol}>
        {isCheckedInToday ? (
          <Pressable
            testID="view-daily-hub-btn"
            style={styles.doneBtn}
            onPress={() => router.push("/(tabs)/daily" as any)}
          >
            <CheckCircle size={14} color="#166534" />
            <Text style={styles.doneBtnText}>GK Hub</Text>
            <ChevronRight size={14} color="#166534" />
          </Pressable>
        ) : (
          <Pressable
            testID="daily-checkin-btn"
            style={styles.checkInBtn}
            onPress={onCheckIn}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator size="small" color={colors.onBrandPrimary} />
            ) : (
              <>
                <Zap size={14} color={colors.onBrandPrimary} fill={colors.onBrandPrimary} />
                <Text style={styles.checkInBtnText}>Check In</Text>
              </>
            )}
          </Pressable>
        )}
      </View>
    </View>
  );
};

const useStyles = makeStyles((colors) => ({
  card: {
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    padding: 12,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 14,
  },
  leftCol: {
    flex: 1,
    paddingRight: 8,
  },
  streakBadge: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    marginBottom: 4,
  },
  streakCountText: {
    fontSize: 14,
    fontWeight: "700",
    color: colors.onSurface,
  },
  motivationText: {
    fontSize: 11,
    color: colors.muted,
    lineHeight: 15,
  },
  rightCol: {
    alignItems: "flex-end",
  },
  checkInBtn: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.brandPrimary,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    gap: 4,
    minHeight: 36,
  },
  checkInBtnText: {
    fontSize: 12,
    fontWeight: "700",
    color: colors.onBrandPrimary,
  },
  doneBtn: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#DCFCE7",
    borderColor: "#86EFAC",
    borderWidth: 1,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
    gap: 4,
    minHeight: 36,
  },
  doneBtnText: {
    fontSize: 12,
    fontWeight: "700",
    color: "#166534",
  },
}));
