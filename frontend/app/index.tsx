import React from "react";
import { ActivityIndicator, View } from "react-native";
import { Redirect } from "expo-router";
import { useAuth } from "@/src/auth/AuthContext";
import { useTheme } from "@/src/theme";

export default function Index() {
  const { isLoading, isAuthenticated } = useAuth();
  const { colors } = useTheme();

  if (isLoading) {
    return (
      <View style={{ flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: colors.surface }}>
        <ActivityIndicator size="large" color={colors.brandPrimary} />
      </View>
    );
  }

  return <Redirect href={isAuthenticated ? "/(tabs)" : "/auth"} />;
}
