import React from "react";
import { useRouter } from "next/router";

function Index() {
  const router = useRouter();
  const { entityName } = router.query;

  return <div>hellow{entityName}</div>;
}

export default Index;
