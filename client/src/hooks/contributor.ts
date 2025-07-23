import { api } from "@/lib/api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

export function useInviteContributor(agentId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (emailToInvite: string) => {
      const response = await api.post(`/contributor/agent/${agentId}`, {
        emailToInvite,
      });
      return response.data.result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["contributor", "agent", agentId],
      });
    },
    onError: (err: any) => {
      console.error(err);
    },
  });
}

export function useRevokeInvite(agentId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (contributorId: string) => {
      const response = await api.delete(
        `/contributor/agent/${agentId}/${contributorId}/invite`
      );
      return response.data.result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["contributor", "agent", agentId],
      });
    },
    onError: (err: any) => {
      console.error(err);
    },
  });
}

export function useGetAllContributorsForAgent(agentId?: string | null) {
  return useQuery({
    queryKey: ["contributor", "agent", agentId],
    queryFn: async () => {
      if (!agentId) return null;
      const response = await api.get(`/contributor/agent/${agentId}`);
      return response.data.result;
    },
    enabled: !!agentId,
  });
}

export function useToggleContributorRole(agentId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      contributorId,
      role,
    }: {
      contributorId: string;
      role: "owner" | "write" | "read";
    }) => {
      const response = await api.patch(
        `/contributor/agent/${agentId}/${contributorId}/role`,
        { role }
      );
      return response.data.result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["contributor", "agent", agentId],
      });
    },
    onError: (err: any) => {
      console.error(err);
    },
  });
}

export function useDeleteContributor(agentId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (contributorId: string) => {
      const response = await api.delete(
        `/contributor/agent/${agentId}/${contributorId}`
      );
      return response.data.result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["contributor", "agent", agentId],
      });
    },
    onError: (err: any) => {
      console.error(err);
    },
  });
}

export function useAcceptInvite(agentId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (userId: string) => {
      const response = await api.patch(
        `/contributor/agent/${agentId}/${userId}/accept`
      );
      return response.data.result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["contributor", "agent", agentId],
      });
    },
    onError: (err: any) => {
      console.error(err);
    },
  });
}

export function useRejectInvite(agentId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (userId: string) => {
      const response = await api.delete(
        `/contributor/agent/${agentId}/${userId}/invite`
      );
      return response.data.result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["contributor", "agent", agentId],
      });
    },
    onError: (err: any) => {
      console.error(err);
    },
  });
}

export function useCheckAuthorization(agentId?: string | null) {
  return useQuery({
    queryKey: ["contributor", "authorization", agentId],
    queryFn: async () => {
      if (!agentId) return null;
      const response = await api.get(
        `/contributor/agent/${agentId}/authorization`
      );
      return response.data;
    },
    enabled: !!agentId,
  });
}
