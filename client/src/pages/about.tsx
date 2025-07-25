import { ReactElement } from "react";
import { Layout } from "@/layouts/Layout";

function About() {
  return <div>About</div>;
}

About.getLayout = (page: ReactElement) => {
  return <Layout>{page}</Layout>;
};

export default About;
