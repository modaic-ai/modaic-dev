import React, { useState } from "react";
import { useRouter } from "next/router";
import { AgentList } from "@/components/agent/AgentList";
import { ApiKeyManager } from "@/components/user/api-key-manager";
import { useUserAgents } from "@/hooks/agent";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import AppLayout from "@/layouts/AppLayout";
import { NextPageWithLayout } from "@/pages/_app";

const UserProfilePage: NextPageWithLayout = () => {
  const router = useRouter();
  const { entityName } = router.query;
  const [activeTab, setActiveTab] = useState<"agents" | "settings">("agents");
  
  const entityNameStr = Array.isArray(entityName) ? entityName[0] : entityName;
  
  const { data: agents, isLoading } = useUserAgents(entityNameStr || '');

  if (!entityNameStr) {
    return <div>Loading...</div>;
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold">{entityNameStr}</h1>
            <p className="text-muted-foreground mt-1">AI Agent Developer</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" size="sm">
              Follow
            </Button>
            <Button size="sm">
              + New Agent
            </Button>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="mb-6">
        <div className="flex gap-6 border-b">
          <button
            className={`pb-3 px-1 text-sm font-medium border-b-2 transition-colors ${
              activeTab === "agents"
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
            onClick={() => setActiveTab("agents")}
          >
            🤖 Agents {agents ? `(${agents.length})` : ''}
          </button>
          <button
            className={`pb-3 px-1 text-sm font-medium border-b-2 transition-colors ${
              activeTab === "settings"
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
            onClick={() => setActiveTab("settings")}
          >
            ⚙️ Settings
          </button>
        </div>
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === "agents" ? (
          <div>
            <div className="mb-6">
              <h2 className="text-xl font-semibold mb-2">Published Agents</h2>
              <p className="text-muted-foreground">
                AI agents created and shared by {entityNameStr}
              </p>
            </div>
            
            <AgentList 
              agents={agents || []} 
              loading={isLoading}
              emptyMessage={`${entityNameStr} hasn't published any agents yet.`}
            />
          </div>
        ) : (
          <div className="max-w-2xl">
            <div className="mb-6">
              <h2 className="text-xl font-semibold mb-2">Developer Settings</h2>
              <p className="text-muted-foreground">
                Manage your API credentials and development tools
              </p>
            </div>
            
            <ApiKeyManager />
          </div>
        )}
      </div>
    </div>
  );
};

UserProfilePage.getLayout = (page) => <AppLayout>{page}</AppLayout>;

export default UserProfilePage;
