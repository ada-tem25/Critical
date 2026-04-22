import { ArticleSource } from "@/data/articles";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useRhetoric, type RhetoricSide } from "@/contexts/RhetoricContext";
const SUPERSCRIPT_MAP: Record<string, number> = {
  "¹": 1, "²": 2, "³": 3, "⁴": 4, "⁵": 5,
  "⁶": 6, "⁷": 7, "⁸": 8, "⁹": 9,
};

// Matches [[fallacy name]] or (lastWord)(superscript)
const COMBINED_REGEX = /\[\[([^\]]+)\]\]|(\S+)([¹²³⁴⁵⁶⁷⁸⁹]+)/g;

interface Props {
  text: string;
  sources: ArticleSource[];
  rhetoricSide?: RhetoricSide;
}

const RhetoricTag = ({ name, side }: { name: string; side?: RhetoricSide }) => {
  const { openFallacy } = useRhetoric();
  return (
    <span
      className="font-bold cursor-pointer hover:underline decoration-foreground/40"
      onClick={() => openFallacy(name, side)}
    >
      {name}
    </span>
  );
};

const SourceInlineRef = ({ text, sources, rhetoricSide }: Props) => {
  const elements: React.ReactNode[] = [];
  let lastIndex = 0;

  for (const match of text.matchAll(COMBINED_REGEX)) {
    const start = match.index!;

    // Text before this match
    if (start > lastIndex) {
      elements.push(<span key={`t-${lastIndex}`}>{text.slice(lastIndex, start)}</span>);
    }

    if (match[1]) {
      // [[fallacy name]] match
      elements.push(<RhetoricTag key={`r-${start}`} name={match[1]} side={rhetoricSide} />);
      lastIndex = start + match[0].length;
      continue;
    }

    // Source superscript match
    const word = match[2];
    const sup = match[3];
    const id = SUPERSCRIPT_MAP[sup];
    const source = sources.find((s) => s.id === id);

    if (!source) {
      elements.push(<span key={`m-${start}`}>{match[0]}</span>);
    } else {
      const biasInfo = source.bias ? (
        <span className="font-bold"> ({source.bias})</span>
      ) : null;

      const tooltipContent = source.url ? (
        <a
          href={source.url}
          target="_blank"
          rel="noopener noreferrer"
          className="font-body text-xs leading-relaxed hover:underline block"
        >
          <span className="font-ui font-semibold">{source.id}.</span>{" "}
          {source.title}{biasInfo}
        </a>
      ) : (
        <span className="font-body text-xs leading-relaxed">
          <span className="font-ui font-semibold">{source.id}.</span>{" "}
          {source.title}{biasInfo}
        </span>
      );

      elements.push(
        <Tooltip key={`m-${start}`}>
          <TooltipTrigger asChild>
            <span
              className="cursor-pointer"
              onClick={() => source.url && window.open(source.url, '_blank', 'noopener,noreferrer')}
            >
              {word}
              <sup className="text-foreground font-ui font-bold text-[14px] ml-[2px] relative top-[-2px]">
                {sup}
              </sup>
            </span>
          </TooltipTrigger>
          <TooltipContent
            side="top"
            className="max-w-xs bg-popover text-popover-foreground border shadow-lg p-3"
          >
            {tooltipContent}
          </TooltipContent>
        </Tooltip>
      );
    }

    lastIndex = start + match[0].length;
  }

  // Remaining text
  if (lastIndex < text.length) {
    elements.push(<span key={`t-${lastIndex}`}>{text.slice(lastIndex)}</span>);
  }

  return (
    <TooltipProvider delayDuration={200}>
      <>{elements}</>
    </TooltipProvider>
  );
};

export default SourceInlineRef;
