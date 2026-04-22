import { useState } from "react";
import { ThumbsUp, ThumbsDown } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const ArticleFeedback = () => {
  const [vote, setVote] = useState<"up" | "down" | null>(null);
  const [animating, setAnimating] = useState<"up" | "down" | null>(null);
  const [showThanks, setShowThanks] = useState(false);
  const [hasShownThanks, setHasShownThanks] = useState(false);

  const handleVote = (type: "up" | "down") => {
    setAnimating(type);
    setVote(vote === type ? null : type);
    setTimeout(() => setAnimating(null), 250);

    if (!hasShownThanks) {
      setShowThanks(true);
      setHasShownThanks(true);
      setTimeout(() => setShowThanks(false), 3000);
    }
  };

  return (
    <div className="mt-10 flex flex-col items-center gap-3">
      {/* Separator */}
      <motion.div
        initial={{ opacity: 0, scaleX: 0 }}
        whileInView={{ opacity: 1, scaleX: 1 }}
        viewport={{ once: true, margin: "-120px" }}
        transition={{ duration: 0.3, ease: "easeOut" }}
        className="w-full border-t border-rule origin-center"
      />
      {/* Question */}
      <motion.p
        initial={{ opacity: 0, y: 10 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-120px" }}
        transition={{ duration: 0.3, ease: "easeOut", delay: 0.15 }}
        className="font-body text-sm text-muted-foreground pt-6"
      >
        Avez-vous apprécié cet article ?
      </motion.p>
      {/* Thumbs */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-120px" }}
        transition={{ duration: 0.3, ease: "easeOut", delay: 0.3 }}
        className="flex items-center gap-5"
      >
        <motion.button
          onClick={() => handleVote("up")}
          animate={animating === "up" ? { scale: [1, 1.35, 1], rotate: [0, -12, 0] } : {}}
          transition={{ duration: 0.3, ease: "easeOut" }}
          className={`p-1 transition-colors ${
            vote === "up"
              ? "text-emerald-700"
              : "text-muted-foreground hover:text-foreground"
          }`}
          aria-label="J'ai aimé"
        >
          <ThumbsUp className="w-5 h-5" />
        </motion.button>
        <motion.button
          onClick={() => handleVote("down")}
          animate={animating === "down" ? { scale: [1, 1.35, 1], rotate: [0, 12, 0] } : {}}
          transition={{ duration: 0.3, ease: "easeOut" }}
          className={`p-1 transition-colors ${
            vote === "down"
              ? "text-red-700"
              : "text-muted-foreground hover:text-foreground"
          }`}
          aria-label="Je n'ai pas aimé"
        >
          <ThumbsDown className="w-5 h-5" />
        </motion.button>
      </motion.div>
      <div className="h-5">
        <AnimatePresence>
          {showThanks && (
            <motion.p
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              transition={{ duration: 0.3, ease: "easeOut" }}
              className="font-body text-xs text-muted-foreground"
            >
              Merci pour votre retour !
            </motion.p>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default ArticleFeedback;
