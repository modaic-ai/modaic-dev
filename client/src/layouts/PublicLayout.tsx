import { cn } from "@/lib/utils";
import { Navbar } from "./Navbar";
import Footer from "./Footer";
import { useUser } from "@/providers/user-provider";

function PublicLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className={cn("bg-background font-sans antialiased")}>
      <div className="relative max-w-[1440px] mx-auto">
        <Navbar />
        <main className="flex min-h-screen ">
          <aside className="w-1/4 dark:bg-muted-background border-r-1"></aside>
          <div className="flex-1 px-6 py-12">{children}</div>
        </main>
        <Footer />
      </div>
    </div>
  );
}

function PublicAppLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className={cn("min-h-screen bg-background font-sans antialiased")}>
      <div className="relative max-w-[1440px] mx-auto">
        <Navbar />
        <main className="px-16 flex">
          <aside className="w-64 dark:bg-muted-background"></aside>
          <div className="flex-1 p-6">{children}</div>
        </main>
        <Footer />
      </div>
    </div>
  );
}

function LandingPageLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className={cn("min-h-screen bg-background font-sans antialiased")}>
      <div className="relative max-w-[1440px] mx-auto">
        <Navbar />
        <main className="flex items-center justify-center min-h-[80dvh]">
          <div>{children}</div>
        </main>
        <Footer />
      </div>
    </div>
  );
}

function AuthLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className={cn("min-h-screen bg-background font-sans antialiased")}>
      <div className="relative max-w-[1440px] mx-auto">
        <Navbar />
        <main className="flex items-center justify-center min-h-[90dvh]">
          <div>{children}</div>
        </main>
      </div>
    </div>
  );
}

function Layout({ children }: Readonly<{ children: React.ReactNode }>) {
  const { user } = useUser();
  if (user) return <PublicAppLayout>{children}</PublicAppLayout>;
  return <PublicLayout>{children}</PublicLayout>;
}

export { Layout, LandingPageLayout, AuthLayout };
