import { useState, useEffect, useCallback, useRef } from "react";

const TITLES = [
"Confrontez les faits",
"Décryptez l'actualité",
"Éclairez le débat",
"Détectez les biais",
"Questionnez les évidences",
"Affûtez votre jugement"];


// Module-level: survives SPA navigation, resets on full page reload
let hasPlayedOnce = false;
let storedTitleIndex = Math.floor(Math.random() * TITLES.length);

const pickRandomOther = (current: number): number => {
  const others = TITLES.map((_, i) => i).filter((i) => i !== current);
  return others[Math.floor(Math.random() * others.length)];
};

const TypewriterTitle = ({ interval = 30000 }: { interval?: number } = {}) => {
  const isFirstLoad = useRef(!hasPlayedOnce);
  const [titleIndex, setTitleIndex] = useState(storedTitleIndex);
  const [displayed, setDisplayed] = useState(isFirstLoad.current ? "" : TITLES[storedTitleIndex]);
  const [isAnimating, setIsAnimating] = useState(isFirstLoad.current);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const phaseRef = useRef<"idle" | "deleting" | "typing">(isFirstLoad.current ? "typing" : "idle");
  const hasInitRef = useRef(false);

  const clear = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
  };

  const typeNext = useCallback((target: string, charIndex: number) => {
    if (charIndex > target.length) {
      phaseRef.current = "idle";
      setIsAnimating(false);
      hasPlayedOnce = true;
      storedTitleIndex = titleIndex;
      return;
    }
    setDisplayed(target.slice(0, charIndex));
    timeoutRef.current = setTimeout(
      () => typeNext(target, charIndex + 1),
      45 + Math.random() * 35
    );
  }, []);

  const deleteChar = useCallback(
    (current: string, nextTarget: string) => {
      if (current.length === 0) {
        phaseRef.current = "typing";
        timeoutRef.current = setTimeout(() => typeNext(nextTarget, 1), 350);
        return;
      }
      const next = current.slice(0, -1);
      setDisplayed(next);
      timeoutRef.current = setTimeout(
        () => deleteChar(next, nextTarget),
        30 + Math.random() * 20
      );
    },
    [typeNext]
  );

  const startAnimation = useCallback(() => {
    if (isAnimating) return;
    setIsAnimating(true);
    phaseRef.current = "deleting";
    const nextIdx = pickRandomOther(titleIndex);
    setTitleIndex(nextIdx);
    timeoutRef.current = setTimeout(() => {
      deleteChar(TITLES[titleIndex], TITLES[nextIdx]);
    }, 200);
  }, [isAnimating, titleIndex, deleteChar]);

  // Type on first mount
  useEffect(() => {
    if (hasInitRef.current || !isFirstLoad.current) return;
    hasInitRef.current = true;
    const idx = storedTitleIndex;
    timeoutRef.current = setTimeout(() => typeNext(TITLES[idx], 1), 400);
  }, [typeNext]);

  // Auto-trigger with configurable interval
  useEffect(() => {
    if (isAnimating) return;
    const t = setTimeout(startAnimation, interval);
    return () => clearTimeout(t);
  }, [isAnimating, startAnimation, interval]);

  // Cleanup
  useEffect(() => () => clear(), []);

  return (
    <div className="flex flex-col items-center w-full max-w-md mx-auto">
      <h2 className="font-display text-3xl md:text-4xl font-bold text-foreground leading-tight w-full text-center">
        {displayed}
        <span
          className={`inline-block w-[3px] h-[0.85em] bg-primary align-baseline ml-[1px] rounded-[1px] translate-y-[2px] transition-opacity ${
          isAnimating ? "animate-blink" : "opacity-0"}`
          } />

      </h2>
    </div>);

};

export default TypewriterTitle;