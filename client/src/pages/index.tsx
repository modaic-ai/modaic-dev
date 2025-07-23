import React, {
  useState,
  useEffect,
  useRef,
  useMemo,
  useCallback,
} from "react";
import { LandingPageLayout } from "@/layouts/PublicLayout";
import { ReactElement } from "react";
import { useRouter } from "next/router";
import { Button } from "@/components/ui/button";

// Custom hook for requestAnimationFrame
const useAnimationFrame = (
  callback: (deltaTime: number) => void,
  isRunning = true
) => {
  const requestRef = useRef<number | null>(null);
  const previousTimeRef = useRef<number | null>(null);

  const animate = useCallback(
    (time: number) => {
      if (previousTimeRef.current !== null) {
        const deltaTime = time - previousTimeRef.current;
        callback(deltaTime);
      }
      previousTimeRef.current = time;
      requestRef.current = requestAnimationFrame(animate);
    },
    [callback]
  );

  useEffect(() => {
    if (isRunning) {
      requestRef.current = requestAnimationFrame(animate);
    }

    return () => {
      if (requestRef.current !== null) {
        cancelAnimationFrame(requestRef.current);
        requestRef.current = null;
      }
      previousTimeRef.current = null;
    };
  }, [animate, isRunning]);
};

const WaterAscii: React.FC = () => {
  const [frame, setFrame] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const characters = "~≈≋⋿⊰⊱◟◝";
  const rows = 70;
  const cols = 120;

  // Pre-calculate constants
  const centerPos = { x: 0.5, y: 0.5 };
  const charactersLength = characters.length;
  const charLengthDivide4 = charactersLength / 4;
  const piTimes2 = Math.PI * 2;

  // Track time for animation updates
  const lastUpdateRef = useRef<number>(0);

  // Animation frame callback
  const updateAnimation = useCallback((deltaTime: number) => {
    // Update only every ~100ms for performance
    lastUpdateRef.current += deltaTime;
    if (lastUpdateRef.current > 166) {
      // ~166ms for 0.6x original speed (slowed another 25%)
      setFrame((f) => f + 1);
      lastUpdateRef.current = 0;
    }
  }, []);

  // Use animation frame instead of setInterval
  useAnimationFrame(updateAnimation);

  useEffect(() => {
    return () => {
      lastUpdateRef.current = 0;
    };
  }, []);

  // Generate ASCII art - like water finding its natural path
  const generateAscii = useCallback(() => {
    const rowsArray = [];
    const frameDiv4 = frame / 6.7; // 0.6x speed (4 -> 6.7, additional 25% reduction)
    const frameDiv5 = frame / 8.3; // 0.6x speed (5 -> 8.3, additional 25% reduction)
    const frameDiv8 = frame / 13.3; // 0.6x speed (8 -> 13.3, additional 25% reduction)

    for (let y = 0; y < rows; y++) {
      const yDivRows = y / rows;
      const yDiv5 = y / 5;
      const yDiv3 = y / 3;
      let rowString = "";
      let rowOpacity = 1;

      for (let x = 0; x < cols; x++) {
        const xDivCols = x / cols;
        const xDiv3 = x / 3;
        const xDiv4 = x / 4;

        // Calculate distance from center (fixed point)
        const dx = xDivCols - centerPos.x;
        const dy = yDivRows - centerPos.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const distTimes10 = dist * 10;
        const distTimes5 = dist * 5;

        // Create wave pattern - grace flowing without force
        const wave =
          Math.sin(xDiv3 + yDiv5 + frameDiv4 + distTimes10) +
          Math.cos(xDiv4 - yDiv3 - frameDiv5) +
          Math.sin(frameDiv8 + xDivCols * piTimes2);

        // Choose character based on wave value and distance
        const charValue = (wave + 2) * charLengthDivide4 + distTimes5;
        const charIndex = Math.floor(Math.abs(charValue)) % charactersLength;

        // Calculate opacity - characters seek lower places like water
        const opacity = Math.max(
          0.2,
          Math.min(0.8, 1 - dist + Math.sin(wave) / 3)
        );

        // Set row opacity to average of all opacity values in the row (approximation)
        if (x === 0) rowOpacity = opacity;
        else rowOpacity = (rowOpacity + opacity) / 2;

        rowString += characters[charIndex];
      }

      rowsArray.push({ text: rowString, opacity: rowOpacity });
    }
    return rowsArray;
  }, [
    frame,
    rows,
    cols,
    charactersLength,
    charLengthDivide4,
    piTimes2,
    centerPos.x,
    centerPos.y,
    characters,
  ]);

  // Calculate ASCII art on frame changes
  const ascii = useMemo(() => generateAscii(), [generateAscii]);

  // Memoize styles to prevent recalculation
  const containerStyle = useMemo(
    () => ({
      margin: 0,
      background: "#0C0F19",
      overflow: "hidden",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      height: "100%",
    }),
    []
  );

  const innerContainerStyle = useMemo(
    () => ({
      padding: "0px",
      position: "relative" as const,
      width: "100%",
      height: "100%",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
    }),
    []
  );

  const preStyle = useMemo(
    () => ({
      fontFamily: "monospace",
      fontSize: "10px",
      lineHeight: "1",
      cursor: "default",
      userSelect: "none" as const,
      margin: 0,
      padding: "20px",
      color: "#87CEEB", // Light blue color instead of violet
    }),
    []
  );

  return (
    <div style={containerStyle}>
      <div ref={containerRef} style={innerContainerStyle}>
        <pre style={preStyle}>
          {ascii.map((row, i) => (
            <div
              key={i}
              style={{
                opacity: row.opacity,
                margin: 0,
                lineHeight: "1",
              }}
            >
              {row.text}
            </div>
          ))}
        </pre>
      </div>
    </div>
  );
};

function Home() {
  const router = useRouter();

  return (
    <div className="relative w-full h-full border rounded-lg overflow-hidden">
      {/* ASCII Water Background */}
      <div className="absolute inset-0 w-full h-full">
        <WaterAscii />
      </div>

      {/* Content Overlay */}
      <div className="relative z-10 flex flex-col items-center justify-center p-6">
        <div className="flex flex-col items-center gap-8 w-full mx-auto">
          <div className="max-w-xl text-8xl">
            <div
              className={`text-8xl font-extrabold text-center text-foreground uppercase`}
            >
              Build the Future.
            </div>
          </div>
          <div className="flex gap-4">
            <Button
              className="truncate font-semibold px-6 py-2 mt-4 h-fit w-fit rounded-full cursor-pointer"
              onClick={() => router.push("/auth")}
            >
              Start Building
            </Button>
            <Button
              className="truncate font-semibold px-6 py-2 mt-4 h-fit w-fit rounded-full cursor-pointer"
              onClick={() => router.push("/auth")}
            >
              Login
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

Home.getLayout = (page: ReactElement) => {
  return <LandingPageLayout>{page}</LandingPageLayout>;
};

export default Home;
