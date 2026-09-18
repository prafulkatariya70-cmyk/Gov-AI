import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { useTheme } from "@/src/theme";
import { Sparkles, CheckCircle2, AlertCircle } from "lucide-react-native";

interface Props {
  score: number;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
  isFullyEligible?: boolean;
  testID?: string;
}

export const MatchScoreBadge: React.FC<Props> = ({
  score,
  size = "md",
  showLabel = true,
  isFullyEligible = true,
  testID = "match-score-badge",
}) => {
  const { colors } = useTheme();

  // Color logic
  let bg = colors.brandTertiary;
  let text = colors.onBrandTertiary;
  let border = colors.brandSecondary;
  let label = "Good Match";

  if (score >= 85) {
    bg = "#DCFCE7";
    text = "#15803D";
    border = "#86EFAC";
    label = "High Match";
  } else if (score >= 65) {
    bg = "#FEF3C7";
    text = "#B45309";
    border = "#FCD34D";
    label = "Eligible";
  } else {
    bg = "#F3F4F6";
    text = "#6B7280";
    border = "#E5E7EB";
    label = "Check Criteria";
  }

  const isSmall = size === "sm";
  const isLarge = size === "lg";

  return (
    <View
      testID={testID}
      style={[
        styles.container,
        {
          backgroundColor: bg,
          borderColor: border,
          paddingHorizontal: isSmall ? 6 : isLarge ? 12 : 8,
          paddingVertical: isSmall ? 2 : isLarge ? 6 : 4,
          borderRadius: isLarge ? 12 : 8,
        },
      ]}
    >
      {score >= 85 ? (
        <Sparkles size={isSmall ? 10 : isLarge ? 16 : 12} color={text} />
      ) : isFullyEligible ? (
        <CheckCircle2 size={isSmall ? 10 : isLarge ? 16 : 12} color={text} />
      ) : (
        <AlertCircle size={isSmall ? 10 : isLarge ? 16 : 12} color={text} />
      )}
      <Text
        style={[
          styles.scoreText,
          {
            color: text,
            fontSize: isSmall ? 11 : isLarge ? 15 : 12,
          },
        ]}
      >
        {score}% {showLabel ? label : "Match"}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    borderWidth: 1,
    alignSelf: "flex-start",
  },
  scoreText: {
    fontWeight: "700",
    letterSpacing: -0.2,
  },
});
