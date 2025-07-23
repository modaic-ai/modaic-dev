import { ReactElement, useCallback, useEffect, useRef, useState } from "react";
import { AuthLayout } from "@/layouts/PublicLayout";
import { useStytch } from "@stytch/nextjs";
import { useCompleteOauth } from "@/hooks/auth";
import { toast } from "sonner";
import { useRouter } from "next/router";
import { useUser } from "@/providers/user-provider";
import { JellyTriangle } from "ldrs/react";
import "ldrs/react/JellyTriangle.css";

export const SESSION_MINUTES = 10077;

const GoogleCallback = () => {
  const client = useStytch();
  const { mutateAsync: completeOauth } = useCompleteOauth();
  const router = useRouter();
  const { token } = router.query;
  const { user } = useUser();
  const [isProcessing, setIsProcessing] = useState(false);
  const hasProcessed = useRef(false);

  const authenticate = useCallback(async () => {
    if (hasProcessed.current || isProcessing) {
      console.log("Authentication already in progress or completed");
      return;
    }

    if (!token || typeof token !== "string") {
      console.error("No valid token found");
      toast.error("Invalid authentication token");
      return;
    }

    hasProcessed.current = true;
    setIsProcessing(true);

    try {
      console.log("Starting OAuth authentication...");

      const response = await client.oauth.authenticate(token, {
        session_duration_minutes: SESSION_MINUTES,
      });

      if (response.session && response.user) {
        console.log("Stytch authentication successful, completing OAuth...");

        const redirectUrl = await completeOauth({
          stytchUserId: response.user_id,
          firstName: response.user.name?.first_name || "",
          lastName: response.user.name?.last_name || "",
          email: response.user.emails?.[0]?.email || "",
          profilePictureUrl:
            response.user.providers?.[0]?.profile_picture_url || "",
        });

        console.log(
          "OAuth completion successful, redirecting to:",
          redirectUrl
        );
        const returnTo = localStorage.getItem("returnTo");
        if (returnTo) {
          localStorage.removeItem("returnTo");
          window.location.href = returnTo;
        } else if (redirectUrl) {
          window.location.href = redirectUrl;
        } else {
          window.location.href = user
            ? `/agents`
            : "/agents";
        }
      } else {
        throw new Error("No session or user returned from Stytch");
      }
    } catch (error: any) {
      console.error("Authentication error:", error);
      hasProcessed.current = false;
      setIsProcessing(false);

      toast.error(error.message || "Please try logging in again");

      setTimeout(() => {
        window.location.href = "/";
      }, 2000);
    }
  }, [client, completeOauth, token, router, isProcessing, user]);

  useEffect(() => {
    if (router.isReady && token && !hasProcessed.current) {
      console.log("Router ready, triggering authentication");
      authenticate();
    }
  }, [router.isReady, token, authenticate, user]);

  return (
    <div className="w-full h-[90dvh] flex justify-center items-center">
      <div className="text-center flex flex-col items-center justify-center">
        <p className="text-lg mb-4">
          {isProcessing ? "Logging you in..." : "Preparing authentication..."}
        </p>
        {isProcessing && (
          <JellyTriangle
            size="30"
            speed="1.75"
            color="white"
          />
        )}
      </div>
    </div>
  );
};

GoogleCallback.getLayout = (page: ReactElement) => {
  return <AuthLayout>{page}</AuthLayout>;
};

export default GoogleCallback;
