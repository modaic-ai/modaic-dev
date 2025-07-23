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
import UserAvatar from "@/components/user/user-avatar";
import { useCheckLoggedInUser, useLogout } from "@/hooks/user";
import { useRouter } from "next/router";

export function Navbar() {
  const { data: user } = useCheckLoggedInUser();
  const { mutate: logout } = useLogout();
  return (
    <div className="bg-background z-50">
      <NavigationMenu
        className="py-1 justify-between px-16 border-b border-b-[0.5px]"
        viewport={false}
      >
        <NavigationMenuList>
          <NavigationMenuItem className="flex items-center">
            <NavigationMenuLink href="/">
              <div className="flex gap-1 items-center -ml-1 justify-center h-full rounded-full pr-1">
                <Image
                  src={"/mosaicnobg.png"}
                  alt="logo"
                  width={36}
                  height={36}
                  className="rounded-full hover:animate-spin-slow"
                  priority
                />
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-black text-xl tracking-tighter">
                    Modaic
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
              <div className="group flex gap-2 items-center">
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
              <div className="group flex gap-2 items-center">
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
              <div className="group flex gap-2 items-center">
                <DocsIcon />
                Docs
              </div>
            </NavigationMenuLink>
          </NavigationMenuItem>
          <NavigationMenuItem>
            <NavigationMenuTrigger className="cursor-pointer" hideChevron>
              <List size={16} />
            </NavigationMenuTrigger>
            <NavigationMenuContent>
              <ul className="grid w-[200px] gap-4">
                <li>
                  <NavigationMenuLink className="rounded-md" asChild>
                    <Link href="#">
                      <div className="font-semibold">Components</div>
                    </Link>
                  </NavigationMenuLink>
                  <NavigationMenuLink className="rounded-md" asChild>
                    <Link href="#">
                      <div className="font-semibold">Documentation</div>
                    </Link>
                  </NavigationMenuLink>
                  <NavigationMenuLink className="rounded-md" asChild>
                    <Link href="#">
                      <div className="font-semibold">Blog</div>
                    </Link>
                  </NavigationMenuLink>
                </li>
              </ul>
            </NavigationMenuContent>
          </NavigationMenuItem>

          <div className="h-full bg-border text-foreground w-[1px]">
            <p className="opacity-0">.</p>
          </div>
          {renderUserMenu(user, logout)}
        </NavigationMenuList>
      </NavigationMenu>
    </div>
  );
}

const renderUserMenu = (user: any, logout: any) => {
  const router = useRouter();
  if (!user) {
    return (
      <>
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
      </>
    );
  }
  return (
    <NavigationMenuItem className="flex items-center">
      <NavigationMenuTrigger
        className="cursor-pointer hover:bg-transparent dark:hover:bg-transparent group-hover:bg-transparent dark:group-hover:bg-transparent"
        hideChevron
      >
        <UserAvatar dimension={30} userId={user.userId} />
      </NavigationMenuTrigger>

      <NavigationMenuContent>
        <ul className="w-[200px]">
          <li>
            <NavigationMenuLink
              className="rounded-md text-lg font-bold flex flex-col"
              href="#"
            >
              <span className="text-sm font-semibold text-muted-foreground">
                Profile
              </span>
              <div className="flex flex-row items-center gap-2 hover:underline">
                <UserAvatar dimension={20} userId={user.userId} />
                {user.username}
              </div>
            </NavigationMenuLink>
          </li>
          <li>
            <NavigationMenuLink
              className="rounded-md font-semibold hover:underline"
              href="#"
            >
              Settings
            </NavigationMenuLink>
          </li>
          <li>
            <NavigationMenuLink
              className="rounded-md font-semibold hover:underline"
              onClick={() => {
                logout();
                router.push("/");
              }}
            >
              <span>Sign Out</span>
            </NavigationMenuLink>
          </li>
        </ul>
      </NavigationMenuContent>
    </NavigationMenuItem>
  );
};
