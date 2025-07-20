import { api } from "@/lib/api";
import { UpdateRepoRequest } from "@/types/repo";
import {
  useInfiniteQuery,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

export function useFetchUserRepos(criteria?: string) {
  return useInfiniteQuery({
    queryKey: ["user", "repos", criteria],
    queryFn: async ({ pageParam = { page: 1, direction: "forward" } }) => {
      const response = await api.get(`/repos/all/user`, {
        params: {
          page: pageParam.page,
          page_size: 10,
          criteria: criteria,
        },
      });
      return {
        ...response.data,
      };
    },
    initialPageParam: { page: 1, direction: "forward" },
    getPreviousPageParam: (lastPage, allPages) => {
      return lastPage.prevCursor;
    },
    getNextPageParam: (lastPage) => {
      if (!lastPage.nextCursor) return undefined;
      return { page: lastPage.nextCursor, direction: "forward" };
    },
  });
}

export const useFetchLikedRepos = () => {
  return useQuery({
    queryKey: ["repos", "liked"],
    queryFn: async () => {
      const response = await api.get("/repos/liked/user");
      return response.data.result;
    },
  });
};

export const useCreateRepo = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (config: any) => {
      const response = await api.post("/repos/create", config);
      return response.data.result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["webs", "all"] });
    },
    onError: () => {},
  });
};

export const useFetchSavedRepos = () => {
  return useQuery({
    queryKey: ["repos", "saved"],
    queryFn: async () => {
      const response = await api.get("/repos/saved/user");
      return response.data.result;
    },
  });
};

export const useUploadImageToRepo = (repoId: string | undefined | null) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ files }: { files: File[] }) => {
      if (!repoId) return;
      const formData = new FormData();

      files.forEach((file) => {
        formData.append("files", file);
      });

      const { data } = await api.post(`/repos/upload/image/${repoId}`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      return data.imageUrls;
    },
    onError: (error: any) => {
      console.error("Image upload failed:", error);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["images", "repo", repoId] });
    },
  });
};

export const useDeleteImageFromRepo = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      repoId,
      imageUrl,
    }: {
      repoId: string;
      imageUrl: string;
    }) => {
      const imageName = imageUrl.split("/").pop();
      const response = await api.delete(
        `/repos/delete/image/${repoId}/${imageName}`
      );
      return response.data.result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["images", "repo"] });
    },
  });
};

export function useGetAllImagesForRepo(repoId?: string | null) {
  return useQuery({
    queryKey: ["images", "repo", repoId],
    queryFn: async () => {
      const response = await api.get(`/repos/images/repo/${repoId}`);
      return response.data.result;
    },
    enabled: !!repoId,
    staleTime: Infinity,
  });
}

export function useDeleteRepo() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (repoId: string) => {
      const response = await api.delete(`/repos/delete/${repoId}`);
      return response.data.result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["repos", "all"] });
    },
    onError: () => {},
  });
}

export const useUpdateRepo = (repoId: string | null | undefined) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (config: UpdateRepoRequest) => {
      if (!repoId) return;
      const response = await api.patch(`/repos/update/${repoId}`, config, {
        headers: { "Content-Type": "application/json" },
      });
      return response.data.result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["webs", "all"] });
    },
    onError: () => {},
  });
};

export function useFetchPublicRepos() {
  return useInfiniteQuery({
    queryKey: ["repos", "public"],
    queryFn: async ({ pageParam = null }) => {
      const response = await api.get("/repos/all", {
        params: {
          cursor: pageParam,
          limit: 10,
          visibility: "Public",
        },
      });
      return response.data;
    },
    initialPageParam: null,
    getNextPageParam: (lastPage) => {
      return lastPage.nextCursor;
    },
  });
}

export function useFetchProfileRepos(
  userId: string,
  visibility: string | null = null
) {
  return useInfiniteQuery({
    queryKey: ["repos", "profile", userId],
    queryFn: async ({ pageParam = null }) => {
      const response = await api.get("/repos/all", {
        params: {
          cursor: pageParam,
          limit: 10,
          userId: userId,
          visibility,
        },
      });
      return response.data;
    },
    initialPageParam: null,
    getNextPageParam: (lastPage) => {
      return lastPage.nextCursor;
    },
    enabled: !!userId,
  });
}

export function useFetchPopularRepos(limit: number) {
  return useQuery({
    queryKey: ["repos", "popular", limit],
    queryFn: async () => {
      const response = await api.get("/repos/popular", {
        params: {
          limit,
        },
      });
      return response.data.result;
    },
    enabled: !!limit,
  });
}

export const useFetchRepoById = (repoId?: string | null) => {
  return useQuery({
    queryKey: ["repo", repoId],
    queryFn: async () => {
      if (!repoId) return null;
      const response = await api.get(`/repos/repo/${repoId}`);
      return response.data.result;
    },
    enabled: !!repoId,
  });
};

export function useLikeRepo(repoId: string) {
  return useMutation({
    mutationFn: async () => {
      if (!repoId) return;
      const response = await api.post(`/repos/like/${repoId}`);
      return response.data.result;
    },
    onSuccess: () => {},
    onError: () => {},
  });
}

export function useUnlikeRepo(repoId: string) {
  return useMutation({
    mutationFn: async () => {
      if (!repoId) return;
      const response = await api.post(`/repos/unlike/${repoId}`);
      return response.data.result;
    },
    onSuccess: () => {},
    onError: () => {},
  });
}

export function useAddTagToRepo(repoId: string) {
  return useMutation({
    mutationFn: async (tag: string) => {
      const response = await api.patch(`/repos/add/tag/${repoId}/${tag}`);
      return response.data.result;
    },
    onSuccess: () => {},
    onError: () => {},
  });
}

export function useRemoveTagFromRepo(repoId: string) {
  return useMutation({
    mutationFn: async (tag: string) => {
      const response = await api.patch(`/repos/remove/tag/${repoId}/${tag}`);
      return response.data.result;
    },
    onSuccess: () => {},
    onError: () => {},
  });
}

export type IterateRepoPayload = {
  name: string;
  description: string;
  withConnections: boolean;
};

export function useIterateRepo(repoId: string) {
  return useMutation({
    mutationFn: async (config: IterateRepoPayload) => {
      const response = await api.post(`/repos/iterate/${repoId}`, config);
      return response.data.result;
    },
    onSuccess: () => {},
    onError: () => {},
  });
}

export type SearchFilter = {
  visibility?: "Public" | "Private";
  userId?: string;
  repoId?: string;
};

export function useSearchRepos(query: string, filters?: SearchFilter) {
  return useQuery({
    queryKey: ["repos", "search", query, filters],
    queryFn: async () => {
      const params = new URLSearchParams({
        query,
      });

      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            if (Array.isArray(value)) {
              value.forEach((v) => params.append(key, v));
            } else {
              params.append(key, value.toString());
            }
          }
        });
      }

      const response = await api.get("/repos/search", { params });
      return response.data.result;
    },
    enabled: !!query,
  });
}

export function useFetchContributers(repoId?: string | null) {
  return useQuery({
    queryKey: ["repos", "contributers", repoId],
    queryFn: async () => {
      const response = await api.get(`/repos/contributers/${repoId}`);
      return response.data.result;
    },
    enabled: !!repoId,
  });
}