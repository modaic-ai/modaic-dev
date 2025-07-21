import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { Agent, PublicAgent } from "@/types/agent";

// Get user's agents
export const useUserAgents = (username: string) => {
  return useQuery({
    queryKey: ["agents", "user", username],
    queryFn: async () => {
      const response = await apiClient.get(`/agents/user/${username}`);
      return response.data as PublicAgent[];
    },
    enabled: !!username,
  });
};

// Get single agent
export const useAgent = (username: string, agentName: string) => {
  return useQuery({
    queryKey: ["agents", username, agentName],
    queryFn: async () => {
      const response = await apiClient.get(`/agents/${username}/${agentName}`);
      return response.data as PublicAgent;
    },
    enabled: !!(username && agentName),
  });
};

// Search public agents
export const useSearchAgents = (query: string, tags?: string[]) => {
  return useQuery({
    queryKey: ["agents", "search", query, tags],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (query) params.append("q", query);
      if (tags?.length) params.append("tags", tags.join(","));
      
      const response = await apiClient.get(`/agents/search?${params.toString()}`);
      return response.data as PublicAgent[];
    },
    enabled: !!query || (tags && tags.length > 0),
  });
};

// Get user's API key
export const useApiKey = () => {
  return useQuery({
    queryKey: ["user", "api-key"],
    queryFn: async () => {
      const response = await apiClient.get("/user/me/api-key");
      return response.data as { apiKey: string; username: string };
    },
  });
};

// Regenerate API key
export const useRegenerateApiKey = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async () => {
      const response = await apiClient.post("/user/me/api-key/regenerate");
      return response.data as { apiKey: string; message: string };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user", "api-key"] });
    },
  });
};