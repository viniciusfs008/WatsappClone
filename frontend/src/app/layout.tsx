import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import dynamic from 'next/dynamic';
const ThemeProvider = dynamic(() => import('./providers/theme-provider'), {
  ssr: false,
});

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ZapZap",
  description: "Chat entre amigos",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-br">
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
