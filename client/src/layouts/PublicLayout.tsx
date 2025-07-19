import { cn } from "@/lib/utils";
import "@/styles/globals.css";
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuIndicator,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "@/components/ui/navigation-menu";

export const metadata = {
  title: "spydr - For the questions without answers.",
  description:
    "Dive into the first community-driven search engine that transforms how you explore and interact with the internet.",
};

export default function PublicLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className={cn("min-h-screen bg-background font-sans antialiased")}>
      <div className="relative max-w-[1440px] mx-auto">
        <NavigationMenu>
          <NavigationMenuList>
            <NavigationMenuItem>
              <NavigationMenuTrigger>Item One</NavigationMenuTrigger>
              <NavigationMenuContent>
                <NavigationMenuLink>Link</NavigationMenuLink>
              </NavigationMenuContent>
            </NavigationMenuItem>
          </NavigationMenuList>
        </NavigationMenu>
        {children}
        <div>footer here</div>
      </div>
    </div>
  );
}
