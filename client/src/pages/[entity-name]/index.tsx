import React, { ReactElement, useState } from "react";
import { useRouter } from "next/router";
import { useGetUserAgents } from "@/hooks/agent";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ProfileLayout } from "@/layouts/Layout";
import UserAvatar from "@/components/user/user-avatar";
import { useFetchEntityByUsername } from "@/hooks/user";
import { UserType } from "@/types/user";
import { BoxIcon } from "@/layouts/icons";
import { JellyTriangle } from "ldrs/react";
import { ArrowRight } from "lucide-react";
import { useUser } from "@/providers/user-provider";

// constants
const MOCK_AGENT_COUNT = 10;

// sub-components
function ProfileActions() {
  const router = useRouter();
  return (
    <div className="flex gap-2">
      <Button
        variant="outline"
        size="sm"
        className="text-xs px-3 py-1 border-slate-600 text-slate-300 hover:bg-slate-800"
        onClick={() => router.push(`/settings/profile`)}
      >
        Edit profile
      </Button>
      <Button
        variant="outline"
        size="sm"
        onClick={() => router.push(`/settings/account`)}
        className="text-xs px-3 py-1 border-slate-600 text-slate-300 hover:bg-slate-800"
      >
        Settings
      </Button>
    </div>
  );
}

function GitHubIcon() {
  return (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path
        fillRule="evenodd"
        d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 10.017C20 4.484 15.522 0 10 0z"
        clipRule="evenodd"
      />
    </svg>
  );
}

function SectionItem({
  icon,
  title,
  subtitle,
}: {
  icon: React.ReactNode;
  title: string;
  subtitle?: string;
}) {
  return (
    <div className="mb-8">
      <div className="flex items-center gap-3 text-slate-300 mb-2">
        <div className="w-5 h-5 rounded-full bg-slate-700/50 flex items-center justify-center">
          {icon}
        </div>
        <span className="text-lg font-bold">{title}</span>
      </div>
      {subtitle && <p className="text-slate-500 text-sm ml-8">{subtitle}</p>}
    </div>
  );
}

function ProfileHeader({ entity }: { entity: UserType }) {
  const { user } = useUser();
  const isAuthorized = user && entity.userId === user.userId;
  return (
    <div className="mb-8">
      <div className="mb-4">
        <UserAvatar deactive userId={entity.userId} dimension={180} />
      </div>

      <h1 className="text-2xl font-bold text-white mb-1">
        {entity.fullName || entity.username}
      </h1>

      <p className="text-slate-400 text-sm mb-6 bg-background/50 rounded-sm w-fit">{entity.username}</p>

      {isAuthorized && <ProfileActions />}
    </div>
  );
}

export function ProfileSideBarContent({ entity }: { entity: UserType }) {
  return (
    <div className="w-full">
      <ProfileHeader entity={entity} />

      <Separator className="bg-slate-700/50 mb-6" />

      <SectionItem icon={<GitHubIcon />} title={entity.username} />

      <SectionItem
        icon={<span className="text-lg">🏢</span>}
        title="Organizations"
        subtitle="None yet"
      />
    </div>
  );
}

function AgentCard({
  entity,
  entityName,
  index,
  onCardClick,
}: {
  entity: UserType;
  entityName: string;
  index: number;
  onCardClick: () => void;
}) {
  return (
    <div
      key={index}
      onClick={onCardClick}
      className="group bg-slate-700/50 flex flex-col gap-1 cursor-pointer rounded-lg p-2 px-3 bg-[linear-gradient(to_left,oklch(0.1715_0.0211_275.24),oklch(0.2064_0.0338_265.53))] hover:bg-[linear-gradient(to_right,oklch(0.1715_0.0211_275.24),oklch(0.2064_0.0338_265.53))] border"
    >
      <div className="flex flex-row items-center gap-2">
        <UserAvatar userId={entity.userId} dimension={22} />
        <p className="text-md font-medium group-hover:text-orange-400 transition-all duration-200 ease-in-out">
          {entity.username}/agent-{index + 1}
        </p>
      </div>

      <div>
        <p className="text-sm leading-3 text-muted-foreground font-semibold">
          Updated 27 minutes ago
        </p>
      </div>
    </div>
  );
}

function AgentsSection({
  entity,
  entityName,
  agents,
  router,
}: {
  entity: UserType;
  entityName: string;
  agents: any[] | undefined;
  router: any;
}) {
  const handleCardClick = (index: number) => {
    router.push(`/${entityName}/agent${index + 1}`);
  };

  return (
    <div className="flex-1 p-8">
      {/* section header */}
      <div className="flex items-center gap-2 mb-4">
        <BoxIcon className="h-4 w-4" />
        <span className="font-bold tracking-tight">Agents</span>
        <span className="text-muted-foreground">
          ({(agents && agents.length) || 0})
        </span>
        <ArrowRight
          className="hover:translate-x-1 text-muted-foreground hover:text-orange-400 transition-all duration-200 ease-in-out cursor-pointer"
          strokeWidth={4}
          size={16}
          onClick={() => router.push(`/${entityName}/agents`)}
        />
      </div>

      {/* agents grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-4">
        {Array.from({ length: MOCK_AGENT_COUNT }).map((_, index) => (
          <AgentCard
            key={index}
            entity={entity}
            entityName={entityName as string}
            index={index}
            onCardClick={() => handleCardClick(index)}
          />
        ))}
      </div>
    </div>
  );
}

export function LoadingState() {
  return (
    <div className="flex justify-center items-center h-64">
      <JellyTriangle />
    </div>
  );
}

export function ErrorState() {
  return (
    <div className="flex justify-center items-center h-64">
      <div className="text-red-400">Error loading profile</div>
    </div>
  );
}

// main component
function UserProfilePage() {
  const router = useRouter();
  const entityName = router.query["entity-name"];

  // data fetching
  const {
    data: entity,
    isLoading: entityLoading,
    error: entityError,
  } = useFetchEntityByUsername((entityName as string) || "");

  const entityNameStr = Array.isArray(entityName) ? entityName[0] : entityName;
  const { data: agents, isLoading } = useGetUserAgents(entityNameStr || "");

  // loading and error states
  if (entityLoading) {
    return <LoadingState />;
  }

  if (entityError || !entity) {
    return <ErrorState />;
  }

  // main render
  return (
    <ProfileLayout sideBarContent={<ProfileSideBarContent entity={entity} />}>
      <AgentsSection
        entity={entity}
        entityName={entityNameStr || ""}
        agents={agents}
        router={router}
      />
    </ProfileLayout>
  );
}

UserProfilePage.getLayout = (page: ReactElement) => page;

export default UserProfilePage;
