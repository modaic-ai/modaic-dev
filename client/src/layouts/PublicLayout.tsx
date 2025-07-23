import { cn } from "@/lib/utils";
import { Navbar } from "./Navbar";
import Footer from "./Footer";
import { useUser } from "@/providers/user-provider";

interface BaseLayoutProps {
  children: React.ReactNode;
  showFooter?: boolean;
  showSidebar?: boolean;
  sidebarOverflow?: boolean;
  mainClassName?: string;
  containerClassName?: string;
}

function BaseLayout({
  children,
  showFooter = true,
  showSidebar = false,
  sidebarOverflow = false,
  mainClassName = "",
  containerClassName = "",
}: BaseLayoutProps) {
  return (
    <div
      className={cn("bg-background font-sans antialiased", containerClassName)}
    >
      <div className="relative max-w-[1440px] mx-auto">
        <Navbar />
        <main className={cn("flex min-h-screen", mainClassName)}>
          {showSidebar && (
            <aside
              className={cn(
                "w-1/4 border-r-1 bg-[linear-gradient(to_right,oklch(0.1715_0.0211_275.24),oklch(0.2064_0.0338_265.53))]",
                sidebarOverflow ? "overflow-hidden" : ""
              )}
            />
          )}
          <div className={cn(showSidebar ? "flex-1 p-12" : "")}>{children}</div>
        </main>
        {showFooter && <Footer />}
      </div>
    </div>
  );
}

function PublicLayout({ children }: { children: React.ReactNode }) {
  return (
    <BaseLayout showSidebar mainClassName="min-h-screen">
      <div className="flex-1 px-12">{children}</div>
    </BaseLayout>
  );
}

function PublicAppLayout({ children }: { children: React.ReactNode }) {
  return (
    <BaseLayout showSidebar sidebarOverflow>
      {children}
    </BaseLayout>
  );
}

function LandingPageLayout({ children }: { children: React.ReactNode }) {
  return (
    <BaseLayout
      containerClassName="min-h-screen"
      mainClassName="items-center justify-center min-h-[90dvh]"
    >
      <div>{children}</div>
    </BaseLayout>
  );
}

function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <BaseLayout
      showFooter={false}
      containerClassName="min-h-screen"
      mainClassName="items-center justify-center min-h-[90dvh]"
    >
      <div>{children}</div>
    </BaseLayout>
  );
}

function Layout({ children }: { children: React.ReactNode }) {
  const { user } = useUser();
  return user ? (
    <PublicAppLayout>{children}</PublicAppLayout>
  ) : (
    <PublicLayout>{children}</PublicLayout>
  );
}

export { Layout, LandingPageLayout, AuthLayout };
