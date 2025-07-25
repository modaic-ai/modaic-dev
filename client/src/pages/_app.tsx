import "@/styles/globals.css";
import type { AppProps } from "next/app";
import { useState, useEffect, type ReactElement, type ReactNode } from "react";
import type { NextPage } from "next";
import { Space_Grotesk } from "next/font/google";
import { Noto_Sans_Sunuwar } from "next/font/google";
import { Work_Sans } from "next/font/google";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StytchProvider } from "@stytch/nextjs";
import { createStytchUIClient } from "@stytch/nextjs/ui";
import { environment } from "@/environment";
import { toast } from "sonner";
import { handleLinkedInWebView } from "@/lib/utils";
import { Toaster } from "sonner";
import Head from "next/head";
import { ThemeProvider } from "@/providers/theme-proivder";
import { Layout } from "@/layouts/Layout";
import { UserProvider } from "@/providers/user-provider";

export type NextPageWithLayout<P = {}, IP = P> = NextPage<P, IP> & {
  getLayout?: (page: ReactElement) => ReactNode;
};

type AppPropsWithLayout = AppProps & {
  Component: NextPageWithLayout;
};

export const fontGrotesk = Space_Grotesk({
  weight: ["300", "400", "500", "600", "700"],
  subsets: ["latin"],
  variable: "--font-grotesk",
});

export const fontNotoSansSunuwar = Noto_Sans_Sunuwar({
  weight: ["400"],
  subsets: ["latin", "sunuwar"],
  variable: "--font-noto-sans-sunuwar",
});

export const fontWorkSans = Work_Sans({
  weight: ["300", "400", "500", "600", "700", "800", "900"],
  subsets: ["latin"],
  variable: "--font-work-sans",
});

const queryClient = new QueryClient();
const stytch = createStytchUIClient(environment.stytch_public_token as string,
  {
  cookieOptions: {
    availableToSubdomains: true,
    domain: environment.client_url?.replace("https://", "").replace("www.", ""),
  },
});

export default function App({ Component, pageProps }: AppPropsWithLayout) {
  const getLayout = Component.getLayout || ((page) => <Layout>{page}</Layout>);
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
        toast.success("Your internet connection has been restored.", {
          duration: 3000,
        });
      }
    };

    const handleOffline = () => {
      setIsOnline(false);
      const id = toast.error("No Internet Connection", {
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
    <QueryClientProvider client={queryClient}>
      <StytchProvider stytch={stytch}>
        <Head>
          <title>Modaic - The AI Application Platform</title>
          <meta
            name="description"
            content="The internet wasn't made for AI. The new era of software requires bottom-up infrastructure to build lasting AI solutions."
          />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <meta property="og:title" content="The Future is Modular" />
          <meta
            property="og:description"
            content="The internet wasn't made for AI. The new era of software requires bottom-up infrastructure to build lasting AI solutions."
          />
          <meta property="og:image" content="/opengraph-image.jpg" />
          <meta property="og:url" content="https://modaic.dev" />
          <meta property="og:type" content="website" />
          <link rel="icon" href="/favicon.ico" />
          <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        </Head>
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          <UserProvider>
            {getLayout(
              <>
                <div className={`${fontWorkSans.className} overflow-hidden`}>
                  <Component {...pageProps} />
                  <Toaster />
                </div>
              </>
            )}
          </UserProvider>
        </ThemeProvider>
      </StytchProvider>
    </QueryClientProvider>
  );
}
