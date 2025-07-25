import { useRouter } from "next/router";
import { useEffect, ComponentType } from "react";
import { useStytchUser } from "@stytch/nextjs";
import { LoadingState } from "@/pages/[entity-name]";

interface WithAuthProps {
  [key: string]: any;
}

type ComponentWithLayout = ComponentType<any> & {
  getLayout?: (page: React.ReactElement) => React.ReactNode;
};

export default function withAuth<T extends WithAuthProps>(
  Component: ComponentWithLayout
) {
  function AuthenticatedComponent(props: T) {
    const router = useRouter();
    const { user, isInitialized } = useStytchUser();

    useEffect(() => {
      if (isInitialized && !user) {
        localStorage.setItem("returnTo", window.location.href);
        window.location.href = "/auth";
      }
    }, [isInitialized, user, router]);

    if (!isInitialized) {
      return (
        <div className="flex justify-center items-center h-screen">
          <LoadingState />
        </div>
      );
    }

    if (!user) {
      return (
        <div className="flex justify-center items-center h-screen">
          <LoadingState />
        </div>
      );
    }

    return <Component {...props} />;
  }

  if (Component.getLayout) {
    AuthenticatedComponent.getLayout = Component.getLayout;
  }

  AuthenticatedComponent.displayName = `withAuth(${Component.displayName || Component.name})`;

  return AuthenticatedComponent;
}
