import "./globals.css";

export const metadata = {
  title: "AI App Compiler",
  description: "Prompt to production architecture generator",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}