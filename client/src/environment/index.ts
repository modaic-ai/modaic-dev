const env = process.env.NEXT_PUBLIC_ENV || "dev";

const local_api_url = process.env.NEXT_PUBLIC_LOCAL_API_URL;
const prod_api_url = process.env.NEXT_PUBLIC_PROD_API_URL;

const local_client_url = process.env.NEXT_PUBLIC_LOCAL_CLIENT_URL;
const prod_client_url = process.env.NEXT_PUBLIC_PROD_CLIENT_URL;

export const environment = {
  environment: env,
  api_url: env === "dev" ? local_api_url : prod_api_url,
  mcp_url: process.env.NEXT_PUBLIC_MCP_URL,
  client_url: env === "dev" ? local_client_url : prod_client_url,
  next_auth_secret: process.env.NEXT_AUTH_SECRET,
  google_client_id: process.env.GOOGLE_CLIENT_ID,
  google_client_secret: process.env.GOOGLE_CLIENT_SECRET,
  posthog_key: process.env.NEXT_PUBLIC_POSTHOG_KEY,
  posthog_host: process.env.NEXT_PUBLIC_POSTHOG_HOST,
  stytch_public_token: process.env.NEXT_PUBLIC_STYTCH_TOKEN,
};
