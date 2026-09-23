import { useMemo } from "react";
import { Appearance, StyleSheet, useColorScheme } from "react-native";

export type ColorScheme = "light" | "dark";

const light = {
  // ---------------------------------------------------------------------------
  // Surfaces: Editorial warm paper aesthetic from design guidelines
  // ---------------------------------------------------------------------------
  surface: "#FAF8F5",
  onSurface: "#1C1917",
  surfaceSecondary: "#F5F2EB",
  onSurfaceSecondary: "#292524",
  surfaceTertiary: "#EAE5DC",
  onSurfaceTertiary: "#44403C",
  surfaceInverse: "#1C1917",
  onSurfaceInverse: "#FAF8F5",
  muted: "#78716C",

  // ---------------------------------------------------------------------------
  // Brand: Terracotta official authoritative tone
  // ---------------------------------------------------------------------------
  brand: "#9A3412",
  onBrand: "#FAF8F5",
  brandPrimary: "#9A3412",
  onBrandPrimary: "#FAF8F5",
  brandSecondary: "#C2410C",
  onBrandSecondary: "#FAF8F5",
  brandTertiary: "#FFEDD5",
  onBrandTertiary: "#7C2D12",

  // ---------------------------------------------------------------------------
  // Status: Semantic
  // ---------------------------------------------------------------------------
  success: "#166534",
  onSuccess: "#F0FDF4",
  warning: "#B45309",
  onWarning: "#FFFBEB",
  error: "#991B1B",
  onError: "#FEF2F2",
  info: "#1E40AF",
  onInfo: "#EFF6FF",

  // ---------------------------------------------------------------------------
  // Lines & Borders
  // ---------------------------------------------------------------------------
  border: "#E7E2D8",
  borderStrong: "#D6CBD0",
  divider: "#EFECE6",
};

const dark = {
  surface: "#1C1917",
  onSurface: "#FAF8F5",
  surfaceSecondary: "#292524",
  onSurfaceSecondary: "#F5F2EB",
  surfaceTertiary: "#3A3532",
  onSurfaceTertiary: "#EAE5DC",
  surfaceInverse: "#FAF8F5",
  onSurfaceInverse: "#1C1917",
  muted: "#A8A29E",

  brand: "#FB923C",
  onBrand: "#1C1917",
  brandPrimary: "#FB923C",
  onBrandPrimary: "#1C1917",
  brandSecondary: "#EA580C",
  onBrandSecondary: "#FAF8F5",
  brandTertiary: "#7C2D12",
  onBrandTertiary: "#FFEDD5",

  success: "#22C55E",
  onSuccess: "#052E16",
  warning: "#F59E0B",
  onWarning: "#451A03",
  error: "#EF4444",
  onError: "#450A0A",
  info: "#3B82F6",
  onInfo: "#082F49",

  border: "#3A3532",
  borderStrong: "#57534E",
  divider: "#2D2A28",
};

export type ThemeColors = typeof light;

export const defaultScheme = "light" satisfies ColorScheme;

export const themes: { light: ThemeColors; dark: ThemeColors } = { light, dark };

export function setColorScheme(scheme: ColorScheme | null) {
  Appearance.setColorScheme?.(scheme ?? "light");
}

setColorScheme?.(defaultScheme);

export function useTheme(): { scheme: ColorScheme; colors: ThemeColors } {
  const system = useColorScheme();
  const scheme: ColorScheme = system === "dark" ? "dark" : "light";
  return { scheme, colors: themes[scheme] };
}

export function makeStyles(
  factory: (colors: ThemeColors) => StyleSheet.NamedStyles<any>,
): () => StyleSheet.NamedStyles<any> {
  return function useStyles(): StyleSheet.NamedStyles<any> {
    const { colors } = useTheme();
    return useMemo(() => StyleSheet.create(factory(colors)), [colors]);
  };
}
