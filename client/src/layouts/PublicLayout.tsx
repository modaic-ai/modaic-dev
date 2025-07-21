import { cn } from "@/lib/utils";
import { Navbar } from "./Navbar";
import Footer from "./Footer";

export default function PublicLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className={cn("min-h-screen bg-background font-sans antialiased")}>
      <div className="relative max-w-[1440px] mx-auto">
        <Navbar />
        <div className="px-16">{children}</div>
        <Footer />
      </div>
    </div>
  );
}
