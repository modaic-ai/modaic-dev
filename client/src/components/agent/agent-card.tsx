import React from "react";
import Link from "next/link";
import { PublicAgent } from "@/types/agent";
import { Button } from "@/components/ui/button";
import { formatDistanceToNow } from "date-fns";

interface AgentCardProps {
  agent: PublicAgent;
}

export function AgentCard({ agent }: AgentCardProps) {
  const formatDate = (date: Date) => {
    return formatDistanceToNow(new Date(date), { addSuffix: true });
  };

  return (
    <div className="group relative rounded-lg border bg-card p-6 shadow-sm transition-all hover:shadow-md">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <Link 
            href={`/${agent.adminId}/${agent.name}`}
            className="block group-hover:no-underline"
          >
            <h3 className="font-semibold text-lg leading-tight group-hover:text-primary transition-colors">
              {agent.name}
            </h3>
          </Link>
          <p className="text-sm text-muted-foreground mt-1">
            by {agent.adminId}
          </p>
        </div>
        <div className="text-xs text-muted-foreground">
          v{agent.version}
        </div>
      </div>

      {/* Description */}
      <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
        {agent.description || "No description provided"}
      </p>

      {/* Tags */}
      {agent.tags && agent.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-4">
          {agent.tags.slice(0, 3).map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center rounded-full bg-secondary px-2 py-1 text-xs font-medium text-secondary-foreground"
            >
              {tag}
            </span>
          ))}
          {agent.tags.length > 3 && (
            <span className="text-xs text-muted-foreground">
              +{agent.tags.length - 3} more
            </span>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <div>
          Updated {formatDate(agent.updated)}
        </div>
        <div className="flex items-center gap-4">
          {/* Add stats here if available */}
          <span>★ 0</span>
          <span>🍴 0</span>
        </div>
      </div>

      {/* Hover overlay */}
      <div className="absolute inset-0 rounded-lg bg-primary/5 opacity-0 transition-opacity group-hover:opacity-100 pointer-events-none" />
    </div>
  );
}