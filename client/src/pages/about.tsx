import { ReactElement } from "react";
import PublicLayout from "@/layouts/PublicLayout";

function About() {
  return <div>About</div>;
}

About.getLayout = (page: ReactElement) => {
  return <PublicLayout>{page}</PublicLayout>;
};

export default About;
