import { cn } from "@/lib/utils";
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar";
import { AppSidebar } from "@/layouts/AppSideBar";

export default function AppLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const isMobile = window.innerWidth < 768;
  if (isMobile) {
    return (
      <div
        className={cn(
          " bg-background pt-[75px] z-80 font-sans antialiased flex flex-col relative"
        )}
      >
        {children}
      </div>
    );
  }

  return (
    <SidebarProvider
      className={cn("h-screen bg-background font-sans antialiased")}
    >
      <AppSidebar />
      <SidebarInset className="overflow-x-hidden">{children}</SidebarInset>
    </SidebarProvider>
  );
}
