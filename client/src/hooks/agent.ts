import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Agent, PublicAgent } from "@/types/agent";

// get user's agents
export const useGetUserAgents = (username: string) => {
  return useQuery({
    queryKey: ["agents", "user", username],
    queryFn: async () => {
      const response = await api.get(`/agents/user/${username}`);
      return response.data as PublicAgent[];
    },
    enabled: !!username,
  });
};

// get single agent
export const useGetAgent = (username: string, agentName: string) => {
  return useQuery({
    queryKey: ["agents", username, agentName],
    queryFn: async () => {
      const response = await api.get(`/agents/${username}/${agentName}`);
      return response.data as PublicAgent;
    },
    enabled: !!(username && agentName),
  });
};

// search public agents
export const useSearchAgents = (query: string, tags?: string[]) => {
  return useQuery({
    queryKey: ["agents", "search", query, tags],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (query) params.append("q", query);
      if (tags?.length) params.append("tags", tags.join(","));

      const response = await api.get(`/agents/search?${params.toString()}`);
      return response.data as PublicAgent[];
    },
    enabled: !!query || (tags && tags.length > 0),
  });
};

// get user's API key
export const useGetApiKey = () => {
  return useQuery({
    queryKey: ["user", "api-key"],
    queryFn: async () => {
      const response = await api.get("/user/me/api-key");
      return response.data as { apiKey: string; username: string };
    },
  });
};

// regenerate API key
export const useRegenerateApiKey = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      const response = await api.post("/user/me/api-key/regenerate");
      return response.data as { apiKey: string; message: string };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user", "api-key"] });
    },
  });
};
