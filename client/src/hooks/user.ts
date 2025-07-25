import { api } from "@/lib/api";
import { toast } from "sonner";
import { PrivateUser, UpdateUserRequest } from "@/types/user";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useQueryClient } from "@tanstack/react-query";

export function useCheckLoggedInUser() {
  return useQuery({
    queryKey: ["user"],
    queryFn: async (): Promise<PrivateUser | null> => {
      const response = await api.get("/auth/me");
      if (response.data) {
        return response.data;
      } else {
        return null;
      }
    },
    retry: false,
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      await api.delete("/auth/session");
    },
    onSuccess: () => {
      queryClient.setQueryData(["user"], null);
      queryClient.invalidateQueries({ queryKey: ["user"] });

      toast("Logged out");
    },
  });
}

export function useFetchUserById(userId?: string | null) {
  return useQuery({
    queryKey: ["user", userId],
    queryFn: async () => {
      if (!userId) return null;
      const response = await api.get(`/user/${userId}`);
      console.log(response.data);
      const data = await response.data;
      return data;
    },
    enabled: !!userId,
    staleTime: 120000, //2 minute stale time
  });
}

export function useFetchEntityByUsername(username?: string | null) {
  return useQuery({
    queryKey: ["user", username],
    queryFn: async () => {
      if (!username) return null;
      const response = await api.get(`/user/username/${username}`);
      console.log(response.data);
      const data = await response.data;
      return data;
    },
    enabled: !!username,
  });
}

export function useUpdateUser() {
  return useMutation({
    mutationFn: async (updates: UpdateUserRequest & { userId: string }) => {
      const { userId, ...updateData } = updates;
      const response = await api.put(`/user/${userId}`, updateData, {
        headers: { "Content-Type": "application/json" },
      });
      const data = await response.data;
      return data;
    },
    onSuccess: () => {
      toast("Profile updated successfully");
    },
    onError: (err: any) => {
      console.error(err);
      toast("Failed to update profile");
    },
  });
}

export function useCheckEmailExists() {
  return useMutation({
    mutationFn: async (email: string) => {
      const response = await api.get(`/user/check/email/`, {
        params: { email },
      });
      const data = response.data.exists;
      return data;
    },
    onError: (err: any) => {
      console.error(err);
    },
  });
}

export function usePinAgent(agentId: string, userId: string | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      if (!userId) return;
      const response = await api.patch(`/user/pin/agent/${agentId}`);
      const data = await response.data.result;
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["user", "pinned", "repos", userId],
      });
    },
    onError: (err: any) => {
      console.error(err);
    },
  });
}

export function useUnpinAgent(agentId: string, userId?: string | null) {
  return useMutation({
    mutationFn: async () => {
      if (!userId) return;
      const response = await api.patch(`/user/unpin/agent/${agentId}`);
      const data = await response.data.result;
      return data;
    },
    onError: (err: any) => {
      console.error(err);
    },
  });
}

export function useFetchPinnedAgents(userId?: string | null) {
  return useQuery({
    queryKey: ["user", "pinned", "agents", userId],
    queryFn: async () => {
      const response = await api.get(`/user/pinned/agents/${userId}`);
      const data = await response.data.result;
      return data;
    },
    enabled: !!userId,
  });
}

export function useUnsaveAgent(agentId: string | null) {
  return useMutation({
    mutationFn: async () => {
      const response = await api.patch(`/user/unsave/agent/${agentId}`);
      const data = await response.data.result;
      return data;
    },
    onError: (err: any) => {
      console.error(err);
    },
  });
}

export function useFetchSavedAgents(userId?: string | null) {
  return useQuery({
    queryKey: ["user", "saved", "agents"],
    queryFn: async () => {
      const response = await api.get(`/user/saved/agents/${userId}`);
      const data = await response.data.result;
      return data;
    },
    enabled: !!userId,
  });
}

export const useUploadProfileImage = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();

      formData.append("file", file);

      const { data } = await api.post(
        `/users/replace/profile/picture`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      return data.result;
    },
    onError: (error: any) => {
      console.error("Image upload failed:", error);
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["user"] });
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });
};

export function useDeleteUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (userId: string) => {
      const response = await api.delete(`/user/${userId}`);
      return response.data.result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user"] });
    },
    onError: (err: any) => {
      console.error(err);
    },
  });
}

export function useCompleteOnboarding() {
  return useMutation({
    mutationFn: async (onboardingData: {
      firstName: string;
      lastName?: string;
      username: string;
      bio?: string;
      occupation: string;
      company?: string;
      purpose: string;
      interest?: string;
    }) => {
      const response = await api.post("/auth/onboarding", onboardingData, {
        headers: { "Content-Type": "application/json" },
      });
      return response.data.result;
    },
    onError: (err: any) => {
      console.error(err);
    },
  });
}
