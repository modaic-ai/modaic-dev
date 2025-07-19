import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatText(text: string, maxChars: number) {
  if (text.length > maxChars) {
    return text.slice(0, maxChars) + "...";
  }
  return text;
}

/**
 * Extract the video id from a given YouTube url.
 *
 * @param {string} url
 * @returns {string | null}
 */
export function extractVideoId(url: string | undefined) {
  if (!url) return;
  const regex =
    /^.*(?:youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
  const match = url.match(regex);
  return match ? match[1] : null;
}

/**
 * Maps a given theme to its corresponding base node color.
 *
 * @param {string | undefined} theme - The theme for which to get the base node color.
 * @returns {string} - The hex color code representing the base node color for the given theme.
 *
 * @example
 * mapThemeToBaseNodeColor("light") // "#5ea4ff"
 * mapThemeToBaseNodeColor("dark") // "#b8b8b8"
 * mapThemeToBaseNodeColor(undefined) // "#b8b8b8"
 */
export const mapThemeToBaseNodeColor = (theme: string | undefined) => {
  switch (theme) {
    case "light":
      return "#5ea4ff";
    case "dark":
      return "#b8b8b8";
    default:
      return "#b8b8b8";
  }
};

/**
 * Maps a given theme to its corresponding node hover color.
 *
 * @param {string | undefined} theme - The theme for which to get the node hover color.
 * @returns {string} - The hex color code representing the node hover color for the given theme.
 *
 * @example
 * mapThemetoHoverNodeColor("light") // "#c084fc"
 * mapThemetoHoverNodeColor("dark") // "#a78bfa"
 * mapThemetoHoverNodeColor(undefined) // "#a78bfa"
 */
export const mapThemetoHoverNodeColor = (theme: string | undefined) => {
  switch (theme) {
    case "light":
      return "#c084fc";
    case "dark":
      return "#a78bfa";
    default:
      return "#a78bfa";
  }
};

/**
 * Maps a given theme to its corresponding text color.
 *
 * @param {string | undefined} theme - The theme for which to get the text color.
 * @returns {string} - The hex color code representing the text color for the given theme.
 *
 * @example
 * mapThemeToTextColor("light") // "#374151"
 * mapThemeToTextColor("dark") // "#b8b8b8"
 * mapThemeToTextColor(undefined) // "#b8b8b8"
 */

export const mapThemeToTextColor = (theme: string | undefined) => {
  switch (theme) {
    case "light":
      return "#374151";
    case "dark":
      return "#b8b8b8";
    default:
      return "#b8b8b8";
  }
};

/**
 * Detects if the user is on a mobile device and using the LinkedIn app,
 * and if so, redirects them to the same URL but with a special prefix that
 * allows the app to open the URL in the external browser.
 *
 * This is a workaround for a bug in the LinkedIn app where it doesn't allow
 * the user to open external links in the app's built-in browser.
 *
 * @returns {boolean} Whether the redirect was successful.
 */
export const handleLinkedInWebView = () => {
  if (typeof window === "undefined") return;

  const userAgent = window.navigator.userAgent;
  const url = window.location.href;

  if (
    userAgent.includes("Mobile") &&
    (userAgent.includes("iPhone") || userAgent.includes("iPad")) &&
    userAgent.includes("LinkedInApp")
  ) {
    window.location.href = "x-safari-" + url;
    return true;
  }
  return false;
};

/**
 * Checks if the current browser is Safari.
 *
 * This function determines whether the user's browser is Safari by checking
 * the user agent string. It excludes cases where the browser is Chrome,
 * despite potentially identifying as Safari.
 *
 * @returns {boolean} True if the browser is Safari, false otherwise.
 */

export const isSafari = () => {
  if (typeof window === "undefined") return false;
  const userAgent = window.navigator.userAgent.toLowerCase();
  return userAgent.includes("safari") && !userAgent.includes("chrome");
};

/**
 * Format a date string according to the given options.
 *
 * If no dateString is given, an empty string is returned.
 *
 * If onlyTime is true, only the time is formatted.
 * If onlyDate is true, only the date is formatted.
 * Otherwise, the full date and time is formatted.
 *
 * @param dateString string to be formatted
 * @param options formatting options
 * @returns formatted string
 */
export const formatDate = (
  dateString?: string,
  options: { onlyTime?: boolean; onlyDate?: boolean } = {}
) => {
  if (!dateString) return "";

  const date = new Date(dateString);

  if (options.onlyTime) {
    return date.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "numeric",
      hour12: true,
    });
  }

  if (options.onlyDate) {
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  }

  return date.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "numeric",
    hour12: true,
  });
};

/**
 * Returns a greeting message based on the time of day in the user's timezone
 * @param timezone - A valid IANA timezone string (e.g., "America/New_York", "Europe/London")
 * @param time - Optional Date object. If not provided, current time will be used
 * @returns A greeting message appropriate for the time of day
 */
export function getTimeBasedGreeting(timezone: string): string {
  // Use provided time or current time
  const currentTime = new Date();

  // Create date with user's timezone
  const options: Intl.DateTimeFormatOptions = {
    timeZone: timezone,
    hour: "numeric",
    hour12: false,
  };

  // Get hour in 24-hour format for the specified timezone
  const formatter = new Intl.DateTimeFormat("en-US", options);
  const formattedTime = formatter.format(currentTime);
  const hour = parseInt(formattedTime, 10);

  // Determine appropriate greeting based on hour
  if (hour >= 5 && hour < 12) {
    return "Good morning";
  } else if (hour >= 12 && hour < 17) {
    return "Good afternoon";
  } else if (hour >= 17 && hour < 22) {
    return "Good evening";
  } else {
    return "Good night";
  }
}

// Example usage:
// const greeting = getTimeBasedGreeting("America/Los_Angeles");
// console.log(greeting); // Will output greeting based on current time in LA

// For testing with a specific time:
// const testTime = new Date("2025-03-21T08:30:00Z");
// const greeting = getTimeBasedGreeting("Asia/Tokyo", testTime);
// console.log(greeting);

export const MAX_IMAGE_SIZE = 5 * 1024 * 1024; // 5MB
export const ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"];
export const ALLOWED_GIF_TYPES = ["image/gif"];

export const mapToolNameToBreadcrumb = (toolName: string) => {
  switch (toolName) {
    case "get_current_weather":
      return "Taking a look outside...";
    case "get_graph_context":
      return "Crawling your web...";
    default:
      return "Thinking...";
  }
};

/**
 * Given a URL, determine whether it's a YouTube link, a website link,
 * or something unknown.
 *
 * @param {string} url The URL to check
 * @returns {"youtube"|"website"|"unknown"} The type of link
 *
 * This function does a simple check on the hostname of the URL to determine
 * whether it's a YouTube link or not. If the hostname doesn't contain a valid
 * TLD (e.g., "example.com"), or if the URL isn't a web URL (e.g., "mailto:"),
 * it will return "unknown".
 */
export const getLinkType = (url: string): "youtube" | "website" | "unknown" => {
  try {
    const parsedUrl = new URL(url);
    if (parsedUrl.protocol !== "http:" && parsedUrl.protocol !== "https:") {
      return "unknown"; // Not a web URL
    }
    const hostname = parsedUrl.hostname.toLowerCase();
    if (hostname.includes("youtube.com") || hostname.includes("youtu.be")) {
      return "youtube";
    }
    // Basic check for a valid TLD, not exhaustive but better than nothing
    if (hostname.includes(".") && hostname.split(".").pop()!.length >= 2) {
      return "website";
    }
    return "unknown";
  } catch (error) {
    return "unknown";
  }
};
