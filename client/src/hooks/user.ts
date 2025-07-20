import { api } from "@/lib/api";
import { toast } from "sonner";
import { PublicUser, UpdateUserRequest } from "@/types/user";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useQueryClient } from "@tanstack/react-query";

export function useCheckLoggedInUser() {
  return useQuery({
    queryKey: ["user"],
    queryFn: async (): Promise<PublicUser | null> => {
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
      await api.post("/auth/logout");
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
      const response = await api.get(`/users/`, {
        params: { userId },
      });
      const data = await response.data.result;
      return data;
    },
    enabled: !!userId,
    staleTime: 120000, //2 minute stale time
  });
}

export function useFetchUserByUsername(username?: string | null) {
  return useQuery({
    queryKey: ["user", username],
    queryFn: async () => {
      if (!username) return null;
      const response = await api.get(`/users/username/${username}`);
      const data = await response.data.result;
      return data;
    },
    enabled: !!username,
  });
}

export function useUpdateUser() {
  return useMutation({
    mutationFn: async (updates: UpdateUserRequest) => {
      const response = await api.patch(`/users/edit/`, updates, {
        headers: { "Content-Type": "application/json" },
      });
      const data = await response.data.result;
      return data;
    },
    onError: (err: any) => {
      console.error(err);
    },
  });
}

export function useCheckEmailExists() {
  return useMutation({
    mutationFn: async (email: string) => {
      const response = await api.get(`/users/check/email/`, {
        params: { email },
      });
      const data = await response.data.result;
      return data;
    },
    onError: (err: any) => {
      console.error(err);
    },
  });
}

export function usePinRepo(repoId: string, userId: string | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      if (!userId) return;
      const response = await api.patch(`/users/pin/repo/${repoId}`);
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

export function useUnpinRepo(repoId: string, userId?: string | null) {
  return useMutation({
    mutationFn: async () => {
      if (!userId) return;
      const response = await api.patch(`/users/unpin/repo/${repoId}`);
      const data = await response.data.result;
      return data;
    },
    onError: (err: any) => {
      console.error(err);
    },
  });
}

export function useFetchPinnedRepos(userId?: string | null) {
  return useQuery({
    queryKey: ["user", "pinned", "repos", userId],
    queryFn: async () => {
      const response = await api.get(`/users/pinned/repos/${userId}`);
      const data = await response.data.result;
      return data;
    },
    enabled: !!userId,
  });
}

export function useUnsaveRepo(repoId: string | null) {
  return useMutation({
    mutationFn: async () => {
      const response = await api.patch(`/users/unsave/repo/${repoId}`);
      const data = await response.data.result;
      return data;
    },
    onError: (err: any) => {
      console.error(err);
    },
  });
}

export function useFetchSavedRepos(userId?: string | null) {
  return useQuery({
    queryKey: ["user", "saved", "repos"],
    queryFn: async () => {
      const response = await api.get(`/users/saved/repos/${userId}`);
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
