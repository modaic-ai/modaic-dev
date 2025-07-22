"use client";

import * as React from "react";
import Link from "next/link";
import { List } from "lucide-react";

import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";
import Image from "next/image";
import { cn } from "@/lib/utils";
import { BoxIcon, CommunityIcon, DocsIcon } from "./icons";
import { Separator } from "@radix-ui/react-separator";

export function Navbar() {
  return (
    <div className="fixed bg-background top-0 left-0 right-0 z-50">
      <NavigationMenu
        className="py-2 justify-between px-16 border-b border-b-[0.5px]"
        viewport={false}
      >
        <NavigationMenuList>
          <NavigationMenuItem className="flex items-center">
            <NavigationMenuLink href="/">
              <div className="flex gap-2 items-center -ml-1 justify-center h-full rounded-full">
                <Image
                  src={"/mosaicnobg.png"}
                  alt="logo"
                  width={36}
                  height={36}
                  className="rounded-full hover:animate-spin-slow"
                  priority
                />
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold text-2xl tracking-tighter">
                    modaic
                  </span>
                </div>
              </div>
            </NavigationMenuLink>
          </NavigationMenuItem>
        </NavigationMenuList>
        <NavigationMenuList>
          <NavigationMenuItem>
            <NavigationMenuLink
              href="/agents"
              className={navigationMenuTriggerStyle()}
            >
              <div className="flex gap-2 items-center">
                <BoxIcon />
                Agents
              </div>
            </NavigationMenuLink>
          </NavigationMenuItem>

          <NavigationMenuItem>
            <NavigationMenuLink
              href="/auth"
              className={navigationMenuTriggerStyle()}
            >
              <div className="flex gap-2 items-center">
                <CommunityIcon />
                Community
              </div>
            </NavigationMenuLink>
          </NavigationMenuItem>

          <NavigationMenuItem>
            <NavigationMenuLink
              href="/docs"
              className={navigationMenuTriggerStyle()}
            >
              <div className="flex gap-2 items-center">
                <DocsIcon />
                Docs
              </div>
            </NavigationMenuLink>
          </NavigationMenuItem>
          <NavigationMenuItem>
            <NavigationMenuTrigger hideChevron>
              <List size={16} />
            </NavigationMenuTrigger>
            <NavigationMenuContent>
              <ul className="grid w-[200px] gap-4">
                <li>
                  <NavigationMenuLink className="rounded-md" asChild>
                    <Link href="#">
                      <div className="font-medium">Components</div>
                      <div className="text-muted-foreground">
                        Browse all components in the library.
                      </div>
                    </Link>
                  </NavigationMenuLink>
                  <NavigationMenuLink className="rounded-md" asChild>
                    <Link href="#">
                      <div className="font-medium">Documentation</div>
                      <div className="text-muted-foreground">
                        Learn how to use the library.
                      </div>
                    </Link>
                  </NavigationMenuLink>
                  <NavigationMenuLink className="rounded-md" asChild>
                    <Link href="#">
                      <div className="font-medium">Blog</div>
                      <div className="text-muted-foreground">
                        Read our latest blog posts.
                      </div>
                    </Link>
                  </NavigationMenuLink>
                </li>
              </ul>
            </NavigationMenuContent>
          </NavigationMenuItem>

          <div className="h-full bg-border text-foreground w-[1px]">
            <p className="opacity-0">.</p>
          </div>
          <NavigationMenuItem>
            <NavigationMenuLink
              href="/auth"
              className={navigationMenuTriggerStyle()}
            >
              Login
            </NavigationMenuLink>
          </NavigationMenuItem>
          <NavigationMenuItem>
            <NavigationMenuLink
              href="/auth"
              className={cn(
                navigationMenuTriggerStyle(),
                "dark:bg-foreground dark:text-background hover:opacity-75 transition-all duration-200 ease-in-out"
              )}
            >
              Sign Up
            </NavigationMenuLink>
          </NavigationMenuItem>
        </NavigationMenuList>
      </NavigationMenu>
    </div>
  );
}
