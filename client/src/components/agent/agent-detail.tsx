import React, { useState } from "react";
import { PublicAgent } from "@/types/agent";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { formatDistanceToNow } from "date-fns";
import ReactMarkdown from "react-markdown";

interface AgentDetailProps {
  agent: PublicAgent;
}

export function AgentDetail({ agent }: AgentDetailProps) {
  const [activeTab, setActiveTab] = useState<"readme" | "config">("readme");

  const formatDate = (date: Date) => {
    return formatDistanceToNow(new Date(date), { addSuffix: true });
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold">{agent.name}</h1>
            <p className="text-lg text-muted-foreground mt-1">
              by {agent.adminId}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-muted-foreground">v{agent.version}</span>
            <Button variant="outline" size="sm">
              ⭐ Star
            </Button>
            <Button variant="outline" size="sm">
              🍴 Fork
            </Button>
          </div>
        </div>

        {agent.description && (
          <p className="text-muted-foreground mb-4">{agent.description}</p>
        )}

        {/* Tags */}
        {agent.tags && agent.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {agent.tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center rounded-full bg-secondary px-3 py-1 text-sm font-medium text-secondary-foreground"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Meta info */}
        <div className="flex items-center gap-6 text-sm text-muted-foreground">
          <span>Created {formatDate(agent.created)}</span>
          <span>Updated {formatDate(agent.updated)}</span>
          <span>Last mirrored {formatDate(agent.lastMirrored)}</span>
        </div>
      </div>

      <Separator className="mb-6" />

      {/* Content Tabs */}
      <div className="mb-6">
        <div className="flex gap-4 border-b">
          <button
            className={`pb-3 px-1 text-sm font-medium border-b-2 transition-colors ${
              activeTab === "readme"
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
            onClick={() => setActiveTab("readme")}
          >
            📖 README
          </button>
          <button
            className={`pb-3 px-1 text-sm font-medium border-b-2 transition-colors ${
              activeTab === "config"
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
            onClick={() => setActiveTab("config")}
          >
            ⚙️ Configuration
          </button>
        </div>
      </div>

      {/* Tab Content */}
      <div className="min-h-[400px]">
        {activeTab === "readme" ? (
          <div className="prose prose-sm max-w-none dark:prose-invert">
            {agent.readmeContent ? (
              <ReactMarkdown>{agent.readmeContent}</ReactMarkdown>
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                <p>No README available for this agent.</p>
              </div>
            )}
          </div>
        ) : (
          <div className="bg-muted/50 rounded-lg p-4">
            <pre className="text-sm overflow-auto">
              <code>
                {agent.configYaml && Object.keys(agent.configYaml).length > 0
                  ? JSON.stringify(agent.configYaml, null, 2)
                  : "# No configuration available"}
              </code>
            </pre>
          </div>
        )}
      </div>

      {/* Usage Instructions */}
      <Separator className="my-8" />
      
      <div className="bg-muted/30 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">🚀 Getting Started</h3>
        <div className="space-y-4">
          <div>
            <h4 className="font-medium mb-2">Install the Modaic SDK</h4>
            <code className="block bg-background p-3 rounded text-sm">
              pip install modaic-sdk
            </code>
          </div>
          
          <div>
            <h4 className="font-medium mb-2">Use this agent in your project</h4>
            <code className="block bg-background p-3 rounded text-sm">
              {`from modaic import Agent

agent = Agent.from_hub("${agent.adminId}/${agent.name}")
result = agent.run("Your input here")`}
            </code>
          </div>
        </div>
      </div>
    </div>
  );
}