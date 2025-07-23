import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { OAuthButton } from "@/components/auth/oauth-button";

export const EmailStepForm = ({
  form,
  onSubmit,
  isPending,
}: {
  form: any;
  onSubmit: (data: any) => Promise<void>;
  isPending: boolean;
}) => (
  <Form {...form}>
    <form
      onSubmit={form.handleSubmit(onSubmit)}
      className="w-md w-full space-y-6"
    >
      <OAuthButton />

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-background px-2 text-muted-foreground">
            Or continue with
          </span>
        </div>
      </div>

      <FormField
        control={form.control}
        name="email"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Email</FormLabel>
            <FormControl>
              <Input
                {...field}
                type="email"
                placeholder="you@example.com"
                data-testid="email-input"
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
      <Button
        type="submit"
        className="w-full font-semibold"
        disabled={isPending}
        data-testid="continue-with-email"
      >
        {isPending ? "Verifying..." : "Continue with Email"}
      </Button>
      <div className="pt-2 text-xs text-center text-muted-foreground">
        By continuing, you agree to our{" "}
        <Link
          href="/terms"
          className="underline hover:font-semibold"
        >
          Terms
        </Link>{" "}
        and{" "}
        <Link
          href="/privacy"
          className="underline hover:font-semibold"
        >
          Privacy Policy
        </Link>
        .
      </div>
    </form>
  </Form>
);
