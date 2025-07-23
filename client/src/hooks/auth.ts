import { api } from "@/lib/api";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { AxiosError } from "axios";

type BackendRegisterRequest = {
  email: string;
  password: string;
  username: string;
  fullName?: string;
  stytchUserId: string;
};

type BackendRegisterResponse = {
  message: string;
  userId: string;
  agentId: string;
  email: string;
  username: string;
};

type OnboardingPayload = {
  firstName: string;
  lastName?: string;
  username: string;
  bio?: string;
  occupation: string;
  company?: string;
  purpose: string;
  interest?: string;
};

export function useSubmitRegister() {
  const queryClient = useQueryClient();
  return useMutation<
    BackendRegisterResponse,
    AxiosError,
    BackendRegisterRequest
  >({
    mutationFn: async (registerPayload) => {
      const response = await api.post(`/auth/register`, registerPayload);
      return response.data;
    },
    onSuccess: (data) => {
      toast.success(data.message || "Registration successful!");
      queryClient.invalidateQueries({ queryKey: ["user"] });
      toast("Registration complete");
      const returnTo = localStorage.getItem("returnTo");
      if (returnTo) {
        localStorage.removeItem("returnTo");
        window.location.href = returnTo;
      } else {
        window.location.href = `/agents`;
      }
    },
    onError: (error: AxiosError) => {
      console.log(error);
      toast.error(mapErrorCode(error.response?.status as number));
      console.error("Registration error:", error);
    },
  });
}

type CompleteOauthRequest = {
  stytchUserId: string;
  email: string;
  firstName: string;
  lastName: string;
  profilePictureUrl: string;
};

export function useCompleteOauth() {
  return useMutation({
    mutationFn: async (payload: CompleteOauthRequest) => {
      console.log("Sending OAuth completion request:", payload);
      const response = await api.post(`/auth`, payload);
      console.log("OAuth completion response:", response.data);
      return response.data.redirect;
    },
    onSuccess: (redirectUrl) => {
      console.log("OAuth completion successful, redirect URL:", redirectUrl);
    },
    onError: (error: any) => {
      console.error("OAuth completion error:", error);
      toast.error("Authentication failed");
    },
  });
}

export function useCompleteOnboarding() {
  return useMutation({
    mutationFn: async (onboardingPayload: OnboardingPayload) => {
      const response = await api.post(`/auth/onboarding`, onboardingPayload);
      const data = await response.data.result;
      return data;
    },
    onError: (err: any) => {
      console.error(err);
      toast.error("Onboarding failed");
    },
  });
}

const mapErrorCode = (code: number) => {
  switch (code) {
    case 400:
      return "Username already exists.";
    case 401:
      return "Invalid email or password.";
    case 403:
      return "Forbidden";
    case 404:
      return "Not Found";
    case 500:
      return "Please use a stronger password.";
    default:
      return "Unknown Error";
  }
};
