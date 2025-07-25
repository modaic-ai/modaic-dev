import React, { ReactElement } from "react";
import { LandingPageLayout } from "@/layouts/Layout";

function Privacy() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12 prose prose-neutral dark:prose-invert">
      <h1 className="text-2xl font-bold">Modaic Privacy Policy</h1>
      <p>
        <strong>Effective Date:</strong> 07/25/2025
      </p>

      <h2 className="text-xl font-bold mt-6">1. Information We Collect</h2>
      <ul>
        <li>Account details (email, name, password)</li>
        <li>Uploaded content and datasets</li>
        <li>Browser/device/session data</li>
        <li>Cookies for authentication and UX</li>
      </ul>

      <h2 className="text-xl font-bold mt-6">2. How We Use It</h2>
      <ul>
        <li>To operate the platform</li>
        <li>To improve DSPy tools and UX</li>
        <li>To ensure platform security</li>
        <li>To communicate updates</li>
      </ul>

      <h2 className="text-xl font-bold mt-6">3. Sharing</h2>
      <ul>
        <li>We never sell your personal data</li>
        <li>
          We share with subprocessors for infrastructure, billing, and support
        </li>
        <li>We comply with legal requests if required</li>
      </ul>

      <h2 className="text-xl font-bold mt-6">4. Your Rights</h2>
      <p>
        You may access, export, correct, or delete your data at any time via
        your settings or by contacting us.
      </p>

      <h2 className="text-xl font-bold mt-6">5. Data Security</h2>
      <p>
        We implement modern encryption and security standards. Users are also
        responsible for securing their own credentials.
      </p>

      <h2 className="text-xl font-bold mt-6">6. Location of Processing</h2>
      <p>
        Data may be stored or processed in the US or other secure locations. By
        using Modaic, you consent to these transfers.
      </p>

      <h2 className="text-xl font-bold mt-6">7. Children</h2>
      <p>Modaic does not allow users under 13 years old.</p>

      <h2 className="text-xl font-bold mt-6">8. Changes to this Policy</h2>
      <p>We may update this with 10 days' notice. Continued use = agreement.</p>

      <p>
        Questions? Email us at{" "}
        <a href="mailto:privacy@modaic.ai">privacy@modaic.ai</a>
      </p>
    </div>
  );
}

Privacy.getLayout = (page: ReactElement) => {
  return <LandingPageLayout>{page}</LandingPageLayout>;
};

export default Privacy;
