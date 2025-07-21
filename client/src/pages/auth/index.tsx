import { useState, useEffect, ReactElement } from "react";
import Head from "next/head";
import { AuthLayout } from "@/layouts/PublicLayout";
import { AuthHeader } from "@/components/auth/auth-header";
import { EmailStepForm } from "@/components/auth/email-step-form";
import { LoginForm } from "@/components/auth/login-form";
import { RegisterForm } from "@/components/auth/register-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useStytch } from "@stytch/nextjs";
import { toast } from "sonner";
import { useCheckEmailExists } from "@/hooks/user";
import { useSubmitRegister } from "@/hooks/auth";
import { useUser } from "@/providers/user-provider";

const emailSchema = z.object({ email: z.email() });
const loginSchema = z.object({
  email: z.email(),
  password: z.string().min(6),
});
const registerSchema = z.object({
  email: z.email(),
  username: z
    .string()
    .min(6)
    .max(14)
    .regex(/^[a-zA-Z0-9_]+$/),
  password: z.string().min(6),
});

export const SESSION_MINUTES = 10080;

function AuthPage() {
  const [step, setStep] = useState("email");
  const [userEmail, setUserEmail] = useState("");
  const client = useStytch();
  const { user } = useUser();

  const { mutateAsync: checkEmailExists, isPending: isCheckingEmail } =
    useCheckEmailExists();
  const { mutateAsync: submitRegister, isPending: isRegistering } =
    useSubmitRegister();

  const emailForm = useForm({
    resolver: zodResolver(emailSchema),
    defaultValues: { email: "" },
  });
  const loginForm = useForm({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });
  const registerForm = useForm({
    resolver: zodResolver(registerSchema),
    defaultValues: { email: "", username: "", password: "" },
  });

  useEffect(() => {
    if (step === "login") loginForm.setValue("email", userEmail);
    if (step === "register") registerForm.setValue("email", userEmail);
  }, [step, userEmail, loginForm, registerForm]);

  const resetToEmail = () => {
    setStep("email");
    setUserEmail("");
    emailForm.reset({ email: "" });
  };

  const onEmailSubmit = async (data: any) => {
    const exists = await checkEmailExists(data.email);
    setUserEmail(data.email);
    setStep(exists ? "login" : "register");
  };

  const onLoginSubmit = async (data: any) => {
    try {
      const response = await client.passwords.authenticate({
        email: data.email,
        password: data.password,
        session_duration_minutes: SESSION_MINUTES,
      });
      if (response.session) {
        toast("Login successful");
        const returnTo = localStorage.getItem("returnTo");
        if (returnTo) {
          localStorage.removeItem("returnTo");
          window.location.href = returnTo;
        } else {
          window.location.href = `/agents`;
        }
      }
    } catch (err: any) {
      toast.error(err.message);
    }
  };

  const onRegisterSubmit = async (data: any) => {
    try {
      const response = await client.passwords.create({
        email: data.email,
        password: data.password,
        session_duration_minutes: SESSION_MINUTES,
      });
      if (response.session) {
        await submitRegister({
          email: data.email,
          username: data.username,
          password: data.password,
          stytchUserId: response.user_id,
        });
      }
    } catch (err: any) {
      toast.error(err.message);
    }
  };

  return (
    <div className="h-[90dvh] flex flex-col justify-center items-center">
      <Head>
        <title>Sign in or create an account | Modaic</title>
      </Head>
      <AuthHeader step={step} email={userEmail} />
      {step === "email" && (
        <EmailStepForm
          form={emailForm}
          onSubmit={onEmailSubmit}
          isPending={isCheckingEmail}
        />
      )}
      {step === "login" && (
        <LoginForm
          form={loginForm}
          onSubmit={onLoginSubmit}
          isPending={false}
          onBack={resetToEmail}
        />
      )}
      {step === "register" && (
        <RegisterForm
          form={registerForm}
          onSubmit={onRegisterSubmit}
          isPending={isRegistering}
          onBack={resetToEmail}
        />
      )}
    </div>
  );
}

AuthPage.getLayout = (page: ReactElement) => (
  <AuthLayout>{page}</AuthLayout>
);
export default AuthPage;
