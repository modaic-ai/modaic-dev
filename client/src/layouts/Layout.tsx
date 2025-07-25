import { cn } from "@/lib/utils";
import { Navbar } from "./Navbar";
import Footer from "./Footer";

interface BaseLayoutProps {
  children: React.ReactNode;
  showFooter?: boolean;
  showSidebar?: boolean;
  sideBarContent?: React.ReactNode;
  sidebarOverflow?: boolean;
  mainClassName?: string;
  containerClassName?: string;
  sidebarClassName?: string;
}

function BaseLayout({
  children,
  showFooter = true,
  showSidebar = false,
  sideBarContent,
  sidebarOverflow = false,
  mainClassName = "",
  containerClassName = "",
  sidebarClassName = "",
}: BaseLayoutProps) {
  return (
    <div
      className={cn("bg-background font-sans antialiased", containerClassName)}
    >
      <div className="relative mx-auto">
        <Navbar />
        <main className={cn("flex min-h-screen max-w-[1440px]", mainClassName)}>
          {showSidebar && (
            <aside
              className={cn(
                "min-w-1/4 px-16 py-8 border-r-1 bg-[linear-gradient(to_right,oklch(0.1715_0.0211_275.24),oklch(0.2064_0.0338_265.53))] flex flex-col",
                sidebarClassName,
                sidebarOverflow ? "overflow-hidden" : ""
              )}
            >
              <div className="flex flex-col items-center">{sideBarContent}</div>
            </aside>
          )}
          <div className={cn(showSidebar ? "flex-1 py-8 px-4" : "")}>
            {children}
          </div>
        </main>
        {showFooter && <Footer />}
      </div>
    </div>
  );
}

function PublicLayout({ children }: { children: React.ReactNode }) {
  return (
    <BaseLayout showSidebar mainClassName="min-h-screen">
      <div className="flex-1 px-4">{children}</div>
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

function SettingsLayout({
  children,
  sideBarContent,
  sidebarClassName,
  showFooter = false,
}: {
  children: React.ReactNode;
  sideBarContent?: React.ReactNode;
  sidebarClassName?: string;
  showFooter?: boolean;
}) {
  return (
    <BaseLayout
      showSidebar
      sidebarOverflow
      sideBarContent={sideBarContent}
      sidebarClassName={sidebarClassName}
      showFooter={showFooter}
    >
      {children}
    </BaseLayout>
  );
}

function ProfileLayout({
  children,
  sideBarContent,
  sidebarClassName,
}: {
  children: React.ReactNode;
  sideBarContent?: React.ReactNode;
  sidebarClassName?: string;
}) {
  return (
    <BaseLayout
      showSidebar
      sidebarOverflow
      sideBarContent={sideBarContent}
      sidebarClassName={sidebarClassName}
    >
      {children}
    </BaseLayout>
  );
}

function Layout({ children }: { children: React.ReactNode }) {
  return <PublicLayout>{children}</PublicLayout>;
}

export { Layout, LandingPageLayout, AuthLayout, SettingsLayout, ProfileLayout };
