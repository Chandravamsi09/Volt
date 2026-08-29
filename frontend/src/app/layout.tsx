import "./globals.css";
import { Navbar } from "@/components/Navbar";
import { Sidebar } from "@/components/Sidebar";

export const metadata = {
  title: "Volt — Enterprise AI/ML & Data Platform",
  description: "Distributed Lakehouse, Feature Store, and MLOps Platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-gray-100 flex flex-col min-h-screen">
        <Navbar />
        <div className="flex flex-1">
          <Sidebar />
          <main className="flex-1 p-8 overflow-y-auto max-w-7xl mx-auto w-full">{children}</main>
        </div>
      </body>
    </html>
  );
}
