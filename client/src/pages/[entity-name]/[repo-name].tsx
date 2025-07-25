import React from "react";
import { useRouter } from "next/router";
import { AgentDetail } from "@/components/agent/agent-detail";
import { useGetAgent } from "@/hooks/agent";
import { Skeleton } from "@/components/ui/skeleton";
import { Layout, ProfileLayout } from "@/layouts/Layout";
import { NextPageWithLayout } from "@/pages/_app";

const AgentPage: NextPageWithLayout = () => {
  const router = useRouter();
  const { entityName, repoName } = router.query;

  const entityNameStr = Array.isArray(entityName) ? entityName[0] : entityName;
  const repoNameStr = Array.isArray(repoName) ? repoName[0] : repoName;

  const {
    data: agent,
    isLoading,
    error,
  } = useGetAgent(entityNameStr || "", repoNameStr || "");

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="mb-8">
          <Skeleton className="h-8 w-64 mb-2" />
          <Skeleton className="h-5 w-32 mb-4" />
          <Skeleton className="h-4 w-full mb-2" />
          <Skeleton className="h-4 w-3/4 mb-4" />

          <div className="flex gap-2 mb-4">
            <Skeleton className="h-6 w-16 rounded-full" />
            <Skeleton className="h-6 w-20 rounded-full" />
            <Skeleton className="h-6 w-12 rounded-full" />
          </div>

          <div className="flex gap-6">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-4 w-32" />
          </div>
        </div>

        <div className="border-t pt-6">
          <div className="flex gap-4 mb-6">
            <Skeleton className="h-10 w-24" />
            <Skeleton className="h-10 w-32" />
          </div>

          <div className="space-y-3">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-4 w-4/6" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center py-12">
          <div className="mx-auto max-w-sm">
            <div className="rounded-full bg-muted p-3 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
              <svg
                className="w-8 h-8 text-muted-foreground"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold">Agent not found</h3>
            <p className="text-muted-foreground mt-2">
              The agent "{entityNameStr}/{repoNameStr}" could not be found.
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!agent) {
    return null;
  }

  return <AgentDetail agent={agent} />;
};

AgentPage.getLayout = (page) => <ProfileLayout>{page}</ProfileLayout>;

export default AgentPage;
