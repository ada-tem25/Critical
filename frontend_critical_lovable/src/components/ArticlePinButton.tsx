import { Pin } from "lucide-react";
import { usePinnedArticles } from "@/contexts/PinnedArticlesContext";
import { toast } from "sonner";
import { useState } from "react";

const ArticlePinButton = ({ articleId }: { articleId: string }) => {
  const { isPinned, togglePin } = usePinnedArticles();
  const pinned = isPinned(articleId);
  const [pressing, setPressing] = useState(false);

  const handleClick = () => {
    setPressing(true);
    setTimeout(() => {
      setPressing(false);
      const wasPinned = pinned;
      togglePin(articleId);
      if (!wasPinned) {
        toast("Article épinglé");
      }
    }, 150);
  };

  return (
    <button
      onClick={handleClick}
      className="ml-auto inline-flex items-center justify-center w-7 h-7"
      title={pinned ? "Désépingler" : "Épingler"}
    >
      <Pin
        className={`w-4 h-4 transition-all duration-150 ${
          pressing
            ? "scale-75"
            : pinned
              ? "hover:scale-110"
              : "hover:scale-110 hover:text-foreground"
        } ${
          pinned
            ? "text-accent fill-accent"
            : "text-muted-foreground"
        }`}
      />
    </button>
  );
};

export default ArticlePinButton;
