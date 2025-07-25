import React, { ReactElement } from "react";
import { Layout } from "@/layouts/Layout";

function Terms() {
  return <div>Terms</div>;
}

Terms.getLayout = (page: ReactElement) => {
  return <Layout>{page}</Layout>;
};

export default Terms;
