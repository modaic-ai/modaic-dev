import React from "react";
import PublicLayout from "@/layouts/PublicLayout";
import { ReactElement } from "react";

function Privacy() {
  return <div>Privacy</div>;
}

Privacy.getLayout = (page: ReactElement) => {
  return <PublicLayout>{page}</PublicLayout>;
};

export default Privacy;
