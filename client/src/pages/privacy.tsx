import React from "react";
import { ReactElement } from "react";
import { Layout } from "@/layouts/PublicLayout";

function Privacy() {
  return <div>Privacy</div>;
}

Privacy.getLayout = (page: ReactElement) => {
  return <Layout>{page}</Layout>;
};

export default Privacy;
