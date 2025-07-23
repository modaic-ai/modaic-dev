import React, { ReactElement, useState } from "react";
import { AgentList } from "@/components/agent/agent-list";
import { useSearchAgents } from "@/hooks/agent";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Layout } from "@/layouts/PublicLayout";

function AgentsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState<"recent" | "popular">("recent");

  const { data: agents, isLoading } = useSearchAgents(
    searchQuery,
    selectedTags
  );

  const popularTags = [
    "natural-language",
    "code-generation",
    "data-analysis",
    "automation",
    "chatbot",
    "vision",
    "audio",
    "text-processing",
  ];

  const handleTagClick = (tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  };

  const clearFilters = () => {
    setSearchQuery("");
    setSelectedTags([]);
  };

  return (
    <div className="">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-xl font-bold mb-2">AI Agent Hub</h1>
        <p className="text-muted-foreground">
          Discover, share, and deploy AI agents built by the community
        </p>
      </div>

      {/* Search and Filters */}
      <div className="mb-8 space-y-4">
        <div className="flex gap-4">
          <div className="flex-1">
            <Input
              placeholder="Search agents... (e.g. 'sentiment analysis', 'chatbot')"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full"
            />
          </div>
          <Select
            value={sortBy}
            onValueChange={(value: "recent" | "popular") => setSortBy(value)}
          >
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="recent">Recent</SelectItem>
              <SelectItem value="popular">Popular</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Tag Filters */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">Filter by tags:</label>
            {(selectedTags.length > 0 || searchQuery) && (
              <Button variant="ghost" size="sm" onClick={clearFilters}>
                Clear filters
              </Button>
            )}
          </div>

          <div className="flex flex-wrap gap-2">
            {popularTags.map((tag) => (
              <Button
                key={tag}
                variant={selectedTags.includes(tag) ? "default" : "outline"}
                size="sm"
                onClick={() => handleTagClick(tag)}
                className="text-xs"
              >
                {tag}
              </Button>
            ))}
          </div>
        </div>

        {/* Active Filters Display */}
        {(selectedTags.length > 0 || searchQuery) && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <span>Active filters:</span>
            {searchQuery && (
              <span className="bg-primary/10 text-primary px-2 py-1 rounded text-xs">
                "{searchQuery}"
              </span>
            )}
            {selectedTags.map((tag) => (
              <span
                key={tag}
                className="bg-secondary px-2 py-1 rounded text-xs"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Results */}
      <div>
        {searchQuery || selectedTags.length > 0 ? (
          <>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold">
                Search Results
                {agents && ` (${agents.length} found)`}
              </h2>
            </div>
            <AgentList
              agents={agents || []}
              loading={isLoading}
              emptyMessage="No agents found matching your search criteria."
            />
          </>
        ) : (
          <>
            <div className="mb-6">
              <h2 className="text-xl font-semibold mb-2">Featured Agents</h2>
              <p className="text-muted-foreground">
                Popular and recently updated agents from the community
              </p>
            </div>

            {/* For now, show empty state with search prompt */}
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
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold">Discover AI Agents</h3>
                <p className="text-muted-foreground mt-2 mb-4">
                  Search for agents or browse by category to get started.
                </p>
                <Button
                  onClick={() => setSearchQuery("chatbot")}
                  variant="outline"
                  size="sm"
                >
                  Try searching "chatbot"
                </Button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

AgentsPage.getLayout = (page: ReactElement) => {
  return <Layout>{page}</Layout>;
};

export default AgentsPage;
