import { api } from "@/lib/api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

export function useInviteContributor(repoId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (emailToInvite: string) => {
      const response = await api.post(`/contributor/repo/${repoId}`, {
        emailToInvite,
      });
      return response.data.result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["contributor", "repo", repoId],
      });
    },
    onError: (err: any) => {
      console.error(err);
    },
  });
}

export function useRevokeInvite(repoId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (contributorId: string) => {
      const response = await api.delete(
        `/contributor/repo/${repoId}/${contributorId}/invite`
      );
      return response.data.result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["contributor", "repo", repoId],
      });
    },
    onError: (err: any) => {
      console.error(err);
    },
  });
}

export function useGetAllContributorsForRepo(repoId?: string | null) {
  return useQuery({
    queryKey: ["contributor", "repo", repoId],
    queryFn: async () => {
      if (!repoId) return null;
      const response = await api.get(`/contributor/repo/${repoId}`);
      return response.data.result;
    },
    enabled: !!repoId,
  });
}

export function useToggleContributorRole(repoId: string) {
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
        `/contributor/repo/${repoId}/${contributorId}/role`,
        { role }
      );
      return response.data.result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["contributor", "repo", repoId],
      });
    },
    onError: (err: any) => {
      console.error(err);
    },
  });
}

export function useDeleteContributor(repoId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (contributorId: string) => {
      const response = await api.delete(
        `/contributor/repo/${repoId}/${contributorId}`
      );
      return response.data.result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["contributor", "repo", repoId],
      });
    },
    onError: (err: any) => {
      console.error(err);
    },
  });
}

export function useAcceptInvite(repoId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (userId: string) => {
      const response = await api.patch(
        `/contributor/repo/${repoId}/${userId}/accept`
      );
      return response.data.result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["contributor", "repo", repoId],
      });
    },
    onError: (err: any) => {
      console.error(err);
    },
  });
}

export function useRejectInvite(repoId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (userId: string) => {
      const response = await api.delete(
        `/contributor/repo/${repoId}/${userId}/invite`
      );
      return response.data.result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["contributor", "repo", repoId],
      });
    },
    onError: (err: any) => {
      console.error(err);
    },
  });
}

export function useCheckAuthorization(repoId?: string | null) {
  return useQuery({
    queryKey: ["contributor", "authorization", repoId],
    queryFn: async () => {
      if (!repoId) return null;
      const response = await api.get(`/contributor/repo/${repoId}/authorization`);
      return response.data;
    },
    enabled: !!repoId,
  });
}