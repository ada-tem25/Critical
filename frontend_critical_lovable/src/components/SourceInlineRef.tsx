import { ArticleSource } from "@/data/articles";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useRhetoric, type RhetoricSide } from "@/contexts/RhetoricContext";
import { getFallacy, getFallacyByName } from "@/data/rhetoric";

const SUPERSCRIPT_MAP: Record<string, number> = {
  "¹": 1, "²": 2, "³": 3, "⁴": 4, "⁵": 5,
  "⁶": 6, "⁷": 7, "⁸": 8, "⁹": 9,
};

const ID_TO_SUPERSCRIPT: Record<number, string> = {
  1: "¹", 2: "²", 3: "³", 4: "⁴", 5: "⁵",
  6: "⁶", 7: "⁷", 8: "⁸", 9: "⁹",
  10: "¹⁰", 11: "¹¹", 12: "¹²", 13: "¹³", 14: "¹⁴",
  15: "¹⁵", 16: "¹⁶", 17: "¹⁷", 18: "¹⁸", 19: "¹⁹", 20: "²⁰",
};

/**
 * Combined regex matching:
 *  1. **snake_case_name**  — backend rhetoric marker (Writer output)
 *  2. [[fallacy label]]    — rhetoric marker (French label, legacy/manual)
 *  3. word¹²³              — legacy superscript source ref (mock data)
 *  4. *N                   — backend source ref (*3, *14, etc.)
 *
 * **name** is checked first so * inside ** is not consumed by the *N rule.
 * For *N: (?<!\*) avoids matching lone * inside ** (already consumed).
 */
const COMBINED_REGEX = /\*\*([a-z_]+)\*\*|\[\[([^\]]+)\]\]|(\S+?)([¹²³⁴⁵⁶⁷⁸⁹]+)|(?<!\*)(\*)(\d{1,2})/g;

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

/** Render a source tooltip for a given source ID */
const SourceRef = ({
  source,
  displayText,
  displaySup,
  keyPrefix,
}: {
  source: ArticleSource;
  displayText: string;
  displaySup: string;
  keyPrefix: string;
}) => {
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

  return (
    <Tooltip key={keyPrefix}>
      <TooltipTrigger asChild>
        <span
          className="cursor-pointer"
          onClick={() => source.url && window.open(source.url, '_blank', 'noopener,noreferrer')}
        >
          {displayText}
          <sup className="text-foreground font-ui font-bold text-[14px] ml-[2px] relative top-[-2px]">
            {displaySup}
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

    // Case 1: **snake_case_name** (backend rhetoric marker)
    if (match[1]) {
      const fallacy = getFallacyByName(match[1]);
      if (fallacy) {
        elements.push(<RhetoricTag key={`r-${start}`} name={fallacy.label} side={rhetoricSide} />);
      } else {
        // Unknown name — render as bold text
        elements.push(<strong key={`m-${start}`}>{match[1]}</strong>);
      }
      lastIndex = start + match[0].length;
      continue;
    }

    // Case 2: [[fallacy label]] (French label, legacy/manual)
    if (match[2]) {
      elements.push(<RhetoricTag key={`r-${start}`} name={match[2]} side={rhetoricSide} />);
      lastIndex = start + match[0].length;
      continue;
    }

    // Case 3: word + unicode superscript (legacy mock format)
    if (match[3] && match[4]) {
      const word = match[3];
      const sup = match[4];
      const id = SUPERSCRIPT_MAP[sup];
      const source = sources.find((s) => s.id === id);

      if (!source) {
        elements.push(<span key={`m-${start}`}>{match[0]}</span>);
      } else {
        elements.push(
          <SourceRef
            key={`m-${start}`}
            source={source}
            displayText={word}
            displaySup={sup}
            keyPrefix={`m-${start}`}
          />
        );
      }
      lastIndex = start + match[0].length;
      continue;
    }

    // Case 4: *N (backend format)
    if (match[5] && match[6]) {
      const id = parseInt(match[6], 10);
      const source = sources.find((s) => s.id === id);
      const supDisplay = ID_TO_SUPERSCRIPT[id] ?? match[6];

      if (!source) {
        elements.push(<span key={`m-${start}`}>{match[0]}</span>);
      } else {
        // Don't repeat the preceding word — just show the superscript
        elements.push(
          <SourceRef
            key={`m-${start}`}
            source={source}
            displayText=""
            displaySup={supDisplay}
            keyPrefix={`m-${start}`}
          />
        );
      }
      lastIndex = start + match[0].length;
      continue;
    }

    // Fallback
    elements.push(<span key={`m-${start}`}>{match[0]}</span>);
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
