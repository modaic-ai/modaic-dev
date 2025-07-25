import { ReactElement } from "react";
import { SettingsLayout } from "@/layouts/Layout";
import { useRouter } from "next/router";
import withAuth from "@/providers/auth-provider";

function Index() {
  const router = useRouter();
  router.push("/settings/profile");
  return <></>;
}

Index.getLayout = (page: ReactElement) => (
  <SettingsLayout>{page}</SettingsLayout>
);

export default withAuth(Index);
