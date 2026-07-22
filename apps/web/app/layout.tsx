import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Life Atlas",
  description: "Your personal world atlas - track places you've visited, lived, and loved.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full">{children}</body>
    </html>
  );
}
