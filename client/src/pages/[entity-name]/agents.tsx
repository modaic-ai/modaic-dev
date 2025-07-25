import React, { ReactElement, useState } from "react";
import { ProfileSideBarContent } from ".";
import { ProfileLayout } from "@/layouts/Layout";
import { useRouter } from "next/router";
import { useFetchEntityByUsername } from "@/hooks/user";
import { useGetUserAgents } from "@/hooks/agent";
import { LoadingState } from "@/pages/[entity-name]/index";
import { ErrorState } from "@/pages/[entity-name]/index";

function AgentsPage() {
    const router = useRouter();
    const entityName = router.query["entity-name"];
    const [activeTab, setActiveTab] = useState<"models" | "datasets">("models");

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
        <div>agents here</div>
      </ProfileLayout>
    );
}

AgentsPage.getLayout = (page: ReactElement) => page;

export default AgentsPage;
