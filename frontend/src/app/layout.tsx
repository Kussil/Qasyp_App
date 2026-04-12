import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Qasyp — B2B Matchmaking Platform",
  description: "AI-powered B2B matchmaking for Kazakhstan",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
