import React, { useState } from "react";
import { ActivityIndicator, Alert, Pressable, Text, TextInput, View } from "react-native";
import { useRouter } from "expo-router";
import { useAuth } from "@/src/auth/AuthContext";
import { useTheme, makeStyles } from "@/src/theme";

export default function AuthScreen() {
  const router = useRouter();
  const { login, register } = useAuth();
  const { colors } = useTheme();
  const styles = useStyles();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [pending, setPending] = useState(false);

  const submit = async () => {
    if (!email.trim() || !password) {
      Alert.alert("Missing details", "Enter your email and password.");
      return;
    }
    if (mode === "register" && password.length < 8) {
      Alert.alert("Password too short", "Use at least 8 characters.");
      return;
    }

    setPending(true);
    try {
      if (mode === "login") await login(email, password);
      else await register(email, password);
      router.replace("/(tabs)");
    } catch (error: any) {
      Alert.alert(
        mode === "login" ? "Login failed" : "Registration failed",
        error?.message || "Please try again.",
      );
    } finally {
      setPending(false);
    }
  };

  return (
    <View style={[styles.screen, { backgroundColor: colors.surface }]}>
      <View style={styles.card}>
        <Text style={styles.eyebrow}>GOVCAREER AI</Text>
        <Text style={styles.title}>{mode === "login" ? "Welcome back" : "Create your account"}</Text>
        <Text style={styles.subtitle}>
          {mode === "login"
            ? "Sign in to see government jobs matched to your profile."
            : "Create your account to build your eligibility profile."}
        </Text>

        <Text style={styles.label}>Email</Text>
        <TextInput
          style={styles.input}
          value={email}
          onChangeText={setEmail}
          placeholder="you@example.com"
          placeholderTextColor={colors.muted}
          autoCapitalize="none"
          keyboardType="email-address"
          autoComplete="email"
        />

        <Text style={styles.label}>Password</Text>
        <TextInput
          style={styles.input}
          value={password}
          onChangeText={setPassword}
          placeholder="••••••••"
          placeholderTextColor={colors.muted}
          secureTextEntry
          autoCapitalize="none"
        />

        <Pressable style={styles.primaryButton} onPress={submit} disabled={pending}>
          {pending ? (
            <ActivityIndicator color={colors.onBrandPrimary} />
          ) : (
            <Text style={styles.primaryText}>{mode === "login" ? "Sign in" : "Create account"}</Text>
          )}
        </Pressable>

        <Pressable
          style={styles.switchButton}
          onPress={() => setMode(mode === "login" ? "register" : "login")}
          disabled={pending}
        >
          <Text style={styles.switchText}>
            {mode === "login" ? "New here? Create an account" : "Already have an account? Sign in"}
          </Text>
        </Pressable>
      </View>
    </View>
  );
}

const useStyles = makeStyles((colors) => ({
  screen: { flex: 1, justifyContent: "center", padding: 20 },
  card: {
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 18,
    padding: 22,
  },
  eyebrow: {
    fontSize: 11,
    fontWeight: "800",
    letterSpacing: 1.5,
    color: colors.brandPrimary,
    marginBottom: 10,
  },
  title: { fontSize: 28, fontWeight: "800", color: colors.onSurface, marginBottom: 8 },
  subtitle: { fontSize: 13, lineHeight: 19, color: colors.muted, marginBottom: 22 },
  label: { fontSize: 12, fontWeight: "700", color: colors.onSurface, marginBottom: 6, marginTop: 8 },
  input: {
    minHeight: 48,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    paddingHorizontal: 12,
    color: colors.onSurface,
    backgroundColor: colors.surface,
  },
  primaryButton: {
    minHeight: 48,
    borderRadius: 10,
    backgroundColor: colors.brandPrimary,
    alignItems: "center",
    justifyContent: "center",
    marginTop: 18,
  },
  primaryText: { color: colors.onBrandPrimary, fontSize: 14, fontWeight: "800" },
  switchButton: { minHeight: 44, alignItems: "center", justifyContent: "center", marginTop: 8 },
  switchText: { color: colors.brandPrimary, fontSize: 12, fontWeight: "700" },
}));
