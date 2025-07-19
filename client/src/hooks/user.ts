import { api } from "@/lib/api";
import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { toast } from "sonner";

export function useUpdateUser(userId: string) {
  return useMutation({
    mutationFn: async (updates: any) => {
      const response = await api.patch(`/user/${userId}`, updates, {
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
