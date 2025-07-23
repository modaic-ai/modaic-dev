import React, { useState } from "react";
import { useGetApiKey, useRegenerateApiKey } from "@/hooks/agent";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";

export function ApiKeyManager() {
  const [showKey, setShowKey] = useState(false);
  const { data: apiData, isLoading, error } = useGetApiKey();
  const regenerateApiKey = useRegenerateApiKey();

  const handleCopyKey = () => {
    if (apiData?.apiKey) {
      navigator.clipboard.writeText(apiData.apiKey);
      toast.success("API key copied to clipboard");
    }
  };

  const handleRegenerateKey = async () => {
    if (confirm("Are you sure you want to regenerate your API key? This will invalidate your current key.")) {
      try {
        await regenerateApiKey.mutateAsync();
        toast.success("API key regenerated successfully");
        setShowKey(false);
      } catch (error) {
        toast.error("Failed to regenerate API key");
      }
    }
  };

  if (error) {
    return (
      <div className="rounded-lg border bg-card p-6">
        <h3 className="text-lg font-semibold mb-4">🔑 API Key</h3>
        <div className="text-center py-8">
          <p className="text-muted-foreground">Failed to load API key</p>
          <Button variant="outline" size="sm" className="mt-3" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-lg border bg-card p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">🔑 API Key</h3>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowKey(!showKey)}
            disabled={isLoading}
          >
            {showKey ? "Hide" : "Show"}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRegenerateKey}
            disabled={isLoading || regenerateApiKey.isPending}
          >
            {regenerateApiKey.isPending ? "Regenerating..." : "Regenerate"}
          </Button>
        </div>
      </div>

      <p className="text-sm text-muted-foreground mb-4">
        Use this API key with the Modaic SDK to push and pull your agents.
      </p>

      <div className="space-y-4">
        <div>
          <Label htmlFor="api-key">API Key</Label>
          <div className="flex gap-2 mt-1">
            {isLoading ? (
              <Skeleton className="h-9 flex-1" />
            ) : (
              <Input
                id="api-key"
                type={showKey ? "text" : "password"}
                value={apiData?.apiKey || ""}
                readOnly
                className="font-mono"
              />
            )}
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleCopyKey}
              disabled={isLoading || !apiData?.apiKey}
            >
              Copy
            </Button>
          </div>
        </div>

        {apiData?.username && (
          <div>
            <Label htmlFor="username">Username</Label>
            <Input
              id="username"
              value={apiData.username}
              readOnly
              className="mt-1"
            />
          </div>
        )}
      </div>

      <div className="mt-6 p-4 bg-muted/50 rounded-lg">
        <h4 className="font-medium mb-2">🚀 Quick Setup</h4>
        <div className="space-y-3">
          <div>
            <p className="text-sm font-medium mb-1">1. Install the Modaic SDK</p>
            <code className="block bg-background p-2 rounded text-sm">
              pip install modaic-sdk
            </code>
          </div>
          
          <div>
            <p className="text-sm font-medium mb-1">2. Configure your API key</p>
            <code className="block bg-background p-2 rounded text-sm">
              modaic login --api-key {showKey && apiData?.apiKey ? apiData.apiKey : "YOUR_API_KEY"}
            </code>
          </div>
          
          <div>
            <p className="text-sm font-medium mb-1">3. Push your first agent</p>
            <code className="block bg-background p-2 rounded text-sm">
              modaic push ./my-agent
            </code>
          </div>
        </div>
      </div>
    </div>
  );
}