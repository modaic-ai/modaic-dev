import "@/styles/globals.css";
import type { AppProps } from "next/app";
import { useState, useEffect, type ReactElement, type ReactNode } from "react";
import type { NextPage } from "next";
import { Inter as FontSans } from "next/font/google";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StytchProvider } from "@stytch/nextjs";
import { createStytchUIClient } from "@stytch/nextjs/ui";
import { environment } from "@/environment";
import { Analytics } from "@vercel/analytics/react";
import { toast } from "sonner";
import AppLayout from "@/layouts/AppLayout";
import { handleLinkedInWebView } from "@/lib/utils";
import { Toaster as SonnerToaster } from "sonner";

export type NextPageWithLayout<P = {}, IP = P> = NextPage<P, IP> & {
  getLayout?: (page: ReactElement) => ReactNode;
};

type AppPropsWithLayout = AppProps & {
  Component: NextPageWithLayout;
};

const fontSans = FontSans({
  weight: ["400", "500", "600", "700", "800", "900"],
  subsets: ["latin"],
  variable: "--font-sans",
});

const queryClient = new QueryClient();
export const stytch = createStytchUIClient(
  environment.stytch_public_token as string,
  {
    cookieOptions: {
      availableToSubdomains: true,
      domain: environment.client_url
        ?.replace("https://", "")
        .replace("www.", ""),
    },
  }
);

export default function App({ Component, pageProps }: AppPropsWithLayout) {
  const getLayout =
    Component.getLayout || ((page) => <AppLayout>{page}</AppLayout>);
  const [isOnline, setIsOnline] = useState(true);
  const [toastId, setToastId] = useState<any>(null);
  useEffect(() => {
    handleLinkedInWebView();
  }, []);

  //handle internet connectivity
  useEffect(() => {
    //set initial status
    setIsOnline(navigator.onLine);

    //handler functions for online/offline events
    const handleOnline = () => {
      setIsOnline(true);
      if (toastId) {
        toast("Your internet connection has been restored.", {
          duration: 3000,
        });
      }
    };

    const handleOffline = () => {
      setIsOnline(false);
      const id = toast("No Internet Connection", {
        duration: Infinity,
      });
      setToastId(id);
    };

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    //clean up event listeners
    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, [toast, toastId]);

  return (
    <StytchProvider stytch={stytch}>
      <QueryClientProvider client={queryClient}>
        <div className={fontSans.className}>
          {getLayout(
            <>
              <Analytics />
              <div className={`${fontSans.className}`}>
                <Component {...pageProps} />
                <SonnerToaster />
              </div>
            </>
          )}
        </div>
      </QueryClientProvider>
    </StytchProvider>
  );
}
