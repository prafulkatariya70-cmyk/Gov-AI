import React from "react";
import { Platform } from "react-native";
import { Tabs } from "expo-router";
import { useTheme } from "@/src/theme";
import {
  Briefcase,
  Sparkles,
  Calendar,
  Flame,
} from "lucide-react-native";

export default function TabLayout() {
  const { colors } = useTheme();

  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.brandPrimary,
        tabBarInactiveTintColor: colors.muted,
        tabBarStyle: {
          backgroundColor: colors.surface,
          borderTopColor: colors.border,
          borderTopWidth: 1,
          ...(Platform.OS === "web" ? { height: 64 } : {}),
        },
        tabBarItemStyle: {
          alignSelf: "center",
        },
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: "600",
          marginBottom: 4,
        },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: "Feed",
          tabBarLabel: "Jobs Feed",
          tabBarIcon: ({ color, size }) => <Briefcase size={22} color={color} />,
        }}
      />
      <Tabs.Screen
        name="recommended"
        options={{
          title: "Matches",
          tabBarLabel: "My Matches",
          tabBarIcon: ({ color, size }) => <Sparkles size={22} color={color} />,
        }}
      />
      <Tabs.Screen
        name="calendar"
        options={{
          title: "Calendar",
          tabBarLabel: "Deadlines",
          tabBarIcon: ({ color, size }) => <Calendar size={22} color={color} />,
        }}
      />
      <Tabs.Screen
        name="daily"
        options={{
          title: "Daily Hub",
          tabBarLabel: "GK Hub",
          tabBarIcon: ({ color, size }) => <Flame size={22} color={color} />,
        }}
      />
    </Tabs>
  );
}
