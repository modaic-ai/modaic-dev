import { Button } from "@/components/ui/button";
import { googleIcon } from "@/components/auth/icons";
import { useStytch } from "@stytch/nextjs";

export const OAuthButton = () => {
  const client = useStytch();
  const redirectUrl = window.location.origin + "/auth/authenticate";
  console.log("handleGoogleSignIn at ", redirectUrl);
  const handleGoogleSignIn = () => {
    client.oauth.google.start({
      login_redirect_url: redirectUrl,
      signup_redirect_url: redirectUrl,
    });
  };

  return (
    <Button
      type="button"
      variant="outline"
      className="w-full flex items-center justify-center gap-2"
      onClick={handleGoogleSignIn}
    >
      {googleIcon} Continue with Google
    </Button>
  );
};
