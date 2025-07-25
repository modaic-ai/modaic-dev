import React, { ReactElement } from "react";
import { LandingPageLayout} from "@/layouts/Layout";

function Terms() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12 prose prose-neutral dark:prose-invert">
      <h1 className="text-2xl font-bold">Modaic Terms of Service</h1>
      <p>
        <strong>Effective Date:</strong> 07/25/2025
      </p>

      <h2 className="text-xl font-bold mt-6">Welcome to Modaic</h2>
      <p>
        Modaic is a platform for building, fine-tuning, and sharing modular AI
        applications. These Terms of Service (“Terms”) govern your use of our
        services.
      </p>
      <p>
        By using Modaic, you agree to these Terms and our Privacy Policy. Please
        do not use the platform if you disagree.
      </p>

      <h2 className="text-xl font-bold mt-6">Key Definitions</h2>
      <ul>
        <li>
          <strong>Account</strong>: Your registered profile for using Modaic
        </li>
        <li>
          <strong>Agent</strong>: A configured DSPy-based AI component
        </li>
        <li>
          <strong>Repository</strong>: A collection of data or models
        </li>
        <li>
          <strong>Services</strong>: All tools, APIs, and features Modaic
          provides
        </li>
      </ul>

      <h2 className="text-xl font-bold mt-6">Your Use of Modaic</h2>
      <p>
        Modaic offers tools to build DSPy agents, host models, run inference,
        and collaborate on fine-tuning projects. You must comply with all laws
        and our policies.
      </p>

      <h2 className="text-xl font-bold mt-6">Your Account</h2>
      <p>
        You are responsible for your credentials, activity, and data security.
        Modaic may suspend your account for misuse.
      </p>

      <h2 className="text-xl font-bold mt-6">Content Ownership & Licensing</h2>
      <p>
        You retain ownership of all content you upload. Modaic has a license to
        display and operate your content solely to provide the Services.
      </p>

      <h2 className="text-xl font-bold mt-6">Payments</h2>
      <p>
        Fees are billed in advance. Usage-based charges apply as needed. All
        payments are handled via secure third-party processors.
      </p>

      <h2 className="text-xl font-bold mt-6">Privacy</h2>
      <p>
        Your data is protected in accordance with our{" "}
        <a href="/privacy">Privacy Policy</a>.
      </p>

      <h2 className="text-xl font-bold mt-6">Intellectual Property</h2>
      <p>
        Modaic retains ownership of its platform, branding, and technology
        stack. User feedback may be used to improve our services.
      </p>

      <h2 className="text-xl font-bold mt-6">Termination</h2>
      <p>
        You can delete your account anytime. We may terminate access due to
        violations of these Terms.
      </p>

      <h2 className="text-xl font-bold mt-6">Limitation of Liability</h2>
      <p>
        Modaic is provided “as is”. Our liability is limited to fees paid in the
        last 12 months, or $50 if on a free plan.
      </p>

      <h2 className="text-xl font-bold mt-6">Governing Law</h2>
      <p>
        These Terms are governed by the laws of the State of [Your State]. Legal
        actions must be filed in that jurisdiction.
      </p>

      <h2 className="text-xl font-bold mt-6">Updates</h2>
      <p>
        We may update these Terms with 10 days' notice. Continued use implies
        acceptance.
      </p>

      <p>
        Questions? Email us at{" "}
        <a href="mailto:legal@modaic.ai">legal@modaic.ai</a>
      </p>
    </div>
  );
}

Terms.getLayout = (page: ReactElement) => {
  return <LandingPageLayout>{page}</LandingPageLayout>;
};

export default Terms;
