import React, { ReactElement } from "react";
import PublicLayout from "@/layouts/PublicLayout";

function Terms() {
  return <div>Terms</div>;
}

Terms.getLayout = (page: ReactElement) => {
  return <PublicLayout>{page}</PublicLayout>;
};

export default Terms;
