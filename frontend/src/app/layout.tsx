import type { Metadata } from "next";
import { NextIntlClientProvider } from "next-intl";
import { getLocale, getMessages } from "next-intl/server";

import { Sidebar } from "@/components/layout/Sidebar";
import "./globals.css";

export const metadata: Metadata = {
  title: "OpenAgent - AI 驱动的全生命周期软件开发平台",
  description:
    "AI-driven full lifecycle software development platform with sandboxed execution",
};

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const locale = await getLocale();
  const messages = await getMessages();

  return (
    <html lang={locale} className="dark">
      <body className="flex h-screen overflow-hidden">
        <NextIntlClientProvider messages={messages}>
          <Sidebar />
          <main className="flex-1 overflow-hidden">{children}</main>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
