export const colors = {
  primary: "#0ea5e9",
  primaryDark: "#0369a1",
  success: "#16a34a",
  warning: "#d97706",
  neutral: "#6b7280",
};

export const matchScoreColor = (score: number): string => {
  if (score > 0.8) return colors.success;
  if (score > 0.6) return colors.warning;
  return colors.neutral;
};
