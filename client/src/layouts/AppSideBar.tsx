"use client";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarTrigger,
} from "@/components/ui/sidebar";

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar
      collapsible="icon"
      {...props}
      className="flex justify-center p-0 border-l-none h-screen"
    >
      <SidebarContent>
        <div className="mt-auto px-2">
          <SidebarTrigger />
        </div>
      </SidebarContent>
      <SidebarFooter className="mb-2 px-2 relative"></SidebarFooter>
    </Sidebar>
  );
}
