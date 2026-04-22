import { Mic, Link2, Loader2, MessageSquare, ArrowUp, Paperclip, Radio, FileText, X, Image, FileType, File } from "lucide-react";
import { usePlan } from "@/contexts/PlanContext";
import { useState, useRef, useEffect, useCallback, useMemo } from "react";
import TypewriterTitle from "./TypewriterTitle";
import { TextShimmer } from "./ui/text-shimmer";

type InputMode = "mic" | "text";

const BAR_COUNT = 18;

const WaveformVisualizer = ({ analyserRef }: { analyserRef: React.RefObject<AnalyserNode | null> }) => {
  const [bars, setBars] = useState<number[]>(Array(BAR_COUNT).fill(3));
  const rafRef = useRef<number | null>(null);

  useEffect(() => {
    const draw = () => {
      if (analyserRef.current) {
        const bufferLength = analyserRef.current.fftSize;
        const dataArray = new Uint8Array(bufferLength);
        analyserRef.current.getByteTimeDomainData(dataArray);
        const step = Math.floor(bufferLength / BAR_COUNT);
        const newBars = Array.from({ length: BAR_COUNT }, (_, i) => {
          let maxDev = 0;
          for (let j = 0; j < step; j++) {
            const dev = Math.abs(dataArray[i * step + j] - 128);
            if (dev > maxDev) maxDev = dev;
          }
          const normalized = maxDev / 128;
          // Amplify: multiply by 3 for more visible bars, max 28px
          return Math.max(3, Math.round(normalized * 4.5 * 28));
        });
        setBars(newBars);
      } else {
        setBars(Array(BAR_COUNT).fill(3));
      }
      rafRef.current = requestAnimationFrame(draw);
    };
    rafRef.current = requestAnimationFrame(draw);
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [analyserRef]);

  return (
    <div className="flex items-center gap-[2px] h-8 px-1">
      {bars.map((height, i) => (
        <div
          key={i}
          className="w-[2.5px] rounded-full bg-destructive transition-all duration-75"
          style={{ height: `${height}px` }}
        />
      ))}
    </div>
  );
};

interface InputZoneProps {
  chatMode?: boolean;
  onSubmit?: (text: string, link: string, file?: File | null) => void;
  onStartRecording?: () => void;
  isProcessing?: boolean;
  processingStatus?: string;
}

const InputZone = ({
  chatMode = false,
  onSubmit,
  onStartRecording,
  isProcessing = false,
  processingStatus,
}: InputZoneProps) => {
  const { currentPlan } = usePlan();
  const hasMicAccess = currentPlan === "Pro" || currentPlan === "Premium";
  const [mode, setMode] = useState<InputMode>("text");
  const [textValue, setTextValue] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [micError, setMicError] = useState(false);
  const [isDictating, setIsDictating] = useState(false);
  const [showLinkInput, setShowLinkInput] = useState(false);
  const [linkValue, setLinkValue] = useState("");
  const [firstInput, setFirstInput] = useState<"text" | "link" | null>(null);
  const [linkError, setLinkError] = useState(false);
  const [shakeSubmit, setShakeSubmit] = useState(false);
  const [editingLink, setEditingLink] = useState(false);
  const linkErrorTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [pressedBtn, setPressedBtn] = useState<"doc" | "link" | "mic" | null>(null);
  const [attachedFile, setAttachedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const linkDebounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pendingTextRef = useRef<string>("");

  const hasDoc = attachedFile !== null;

  // Pretty site name from URL
  const prettyLinkName = (() => {
    try {
      const url = new URL(linkValue.trim());
      const host = url.hostname.replace(/^www\./, "");
      // Capitalize first letter
      return host.charAt(0).toUpperCase() + host.slice(1);
    } catch {
      return "";
    }
  })();

  // Audio refs for waveform
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);

  // Track which input was filled first
  useEffect(() => {
    const hasText = textValue.trim().length > 0;
    const hasLink = linkValue.trim().length > 0;
    if (!hasText && !hasLink) {
      setFirstInput(null);
    } else if (!hasLink && hasText) {
      setFirstInput("text");
    } else if (!hasText && hasLink) {
      setFirstInput("link");
    } else if (firstInput === null) {
      if (hasText) setFirstInput("text");
      else if (hasLink) setFirstInput("link");
    }
  }, [textValue, linkValue, firstInput]);

  const triggerPress = useCallback((btn: "doc" | "link" | "mic", onComplete?: () => void) => {
    setPressedBtn(btn);
    setTimeout(() => {
      setPressedBtn(null);
      onComplete?.();
    }, 150);
  }, []);

  const isLinkInvalid = linkValue.trim().length > 0 && !linkValue.trim().startsWith("https://");

  const handleSubmit = (source: "text" | "link") => {
    if (isProcessing) return;
    if (isLinkInvalid) {
      setShakeSubmit(true);
      setLinkError(true);
      setTimeout(() => setShakeSubmit(false), 300);
      if (linkErrorTimerRef.current) clearTimeout(linkErrorTimerRef.current);
      linkErrorTimerRef.current = setTimeout(() => setLinkError(false), 5000);
      return;
    }
    const text = textValue.trim();
    const link = linkValue.trim();
    if (onSubmit && (text || link || hasDoc)) {
      onSubmit(text, link, attachedFile);
    }
  };

  const showSubmitInText =
    !isDictating &&
    !isProcessing &&
    (textValue.trim().length > 0 || linkValue.trim().length > 0) &&
    firstInput !== "link";
  const showSubmitInLink = !isDictating && !isProcessing && (linkValue.trim().length > 0 && firstInput === "link" || hasDoc && !textValue.trim());
  const showProcessingInText = isProcessing && firstInput !== "link";
  const showProcessingInLink = isProcessing && firstInput === "link";

  // Clear inputs when processing ends

  const prevProcessingRef = useRef(false);
  useEffect(() => {
    if (prevProcessingRef.current && !isProcessing) {
      setTextValue("");
      setLinkValue("");
      setShowLinkInput(false);
      setFirstInput(null);
      setAttachedFile(null);
    }
    prevProcessingRef.current = isProcessing;
  }, [isProcessing]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      const lineHeight = 20;
      const maxHeight = lineHeight * 8;
      const scrollHeight = textareaRef.current.scrollHeight;
      textareaRef.current.style.height = Math.min(scrollHeight, maxHeight) + "px";
      textareaRef.current.style.overflowY = scrollHeight > maxHeight ? "auto" : "hidden";
    }
  }, [textValue]);

  const startDictation = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const audioContext = new AudioContext();
      audioContextRef.current = audioContext;
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 512;
      analyser.smoothingTimeConstant = 0.5;
      analyserRef.current = analyser;
      const source = audioContext.createMediaStreamSource(stream);
      sourceRef.current = source;
      source.connect(analyser);
      setIsDictating(true);
    } catch {
      // Permission denied or error – do not activate dictation
    }
  }, []);

  const stopDictation = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    if (sourceRef.current) {
      sourceRef.current.disconnect();
      sourceRef.current = null;
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    analyserRef.current = null;
    setIsDictating(false);
  }, []);

  const handleMicClick = useCallback(() => {
    if (isDictating) {
      stopDictation();
    } else {
      startDictation();
    }
  }, [isDictating, startDictation, stopDictation]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopDictation();
    };
  }, [stopDictation]);

  const modes: { id: InputMode; icon: typeof Mic; label: string }[] = hasMicAccess
    ? [
        { id: "text", icon: MessageSquare, label: "Article" },
        { id: "mic", icon: Radio, label: "Discours" },
      ]
    : [];

  return (
    <div className={`w-full max-w-2xl mx-auto ${chatMode ? "" : "animate-fade-up"}`}>
      {/* Headline - hidden in chat mode */}
      {!chatMode && (
        <div className="text-center mb-8">
          <TypewriterTitle />
          <div className="mt-3 max-w-lg mx-auto min-h-[3em]">
            <p key={mode} className="font-body text-base text-muted-foreground text-center">
              {mode === "text"
                ? "Analysez un article, une publication de réseau ou un document."
                : "Fact-checkez un discours ou un débat en temps réel."}
            </p>
          </div>
        </div>
      )}

      {/* Mode tabs - hidden in chat mode and when only one mode */}
      {!chatMode && modes.length > 0 && (
        <div className="flex items-center justify-center gap-1 mb-3">
          {modes.map(({ id, icon: Icon, label }) => (
            <button
              key={id}
              disabled={isProcessing}
              onClick={() => setMode(id)}
              className={`
                flex items-center gap-2 px-4 py-2 rounded-lg font-ui text-sm transition-all duration-200
                ${
                  mode === id
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground hover:bg-secondary"
                }
                ${isProcessing ? "cursor-not-allowed" : ""}
              `}
            >
              <Icon className="w-4 h-4" />
              {label}
            </button>
          ))}
        </div>
      )}

      {/* Input area */}
      <div className="flex flex-col">
        {mode === "text" && (
          <div className="flex-col pt-2 my-0 mb-[3px] py-[7px] flex items-center justify-start">
            <div className="w-full sm:max-w-lg border border-dashed border-border rounded-xl flex flex-col">
              <textarea
                ref={textareaRef}
                value={textValue}
                disabled={isProcessing}
                onChange={(e) => {
                  const val = e.target.value;
                  setTextValue(val);
                  pendingTextRef.current = val;
                  const urlRegex = /(https?:\/\/\S+\.\S+)/g;
                  const match = val.match(urlRegex);
                  if (match) {
                    const url = match[0];
                    setLinkValue(url);
                    setShowLinkInput(true);
                    setTextValue(val.replace(url, "").trim());
                    setAttachedFile(null); // Link replaces doc
                    triggerPress("link");
                  }
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit("text");
                  }
                }}
                rows={2}
                placeholder="Écrivez ou collez un texte à vérifier..."
                className={`w-full bg-transparent p-3 font-body text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none resize-none min-h-[60px] rounded-t-xl ${isProcessing ? "opacity-60 cursor-not-allowed" : ""}`}
              />

              {/* Bottom toolbar */}
              <div className="flex items-center gap-1 px-2 py-1.5">
                {/* Doc + Link: always visible on the left */}
                <button
                  type="button"
                  disabled={isProcessing}
                  className={`w-8 h-8 rounded-lg flex items-center justify-center transition-all duration-150 text-muted-foreground hover:text-foreground flex-shrink-0 ${pressedBtn === "doc" ? "scale-[0.85] opacity-70" : ""} ${isProcessing ? "opacity-40 cursor-not-allowed" : "cursor-pointer"}`}
                  title="Ajouter un document"
                  onClick={() => triggerPress("doc", () => fileInputRef.current?.click())}
                >
                  <Paperclip className="w-4 h-4" />
                </button>
                <input
                  ref={fileInputRef}
                  type="file"
                  className="hidden"
                  accept=".pdf,.png,.jpg,.jpeg,.doc,.docx,.txt"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      setAttachedFile(file);
                      setLinkValue("");
                      setEditingLink(false);
                      setShowLinkInput(true);
                    }
                    e.target.value = "";
                  }}
                />

                <button
                  type="button"
                  disabled={isProcessing || hasDoc}
                  onClick={() => {
                    if (hasDoc) return;
                    if (showLinkInput) setLinkValue("");
                    setShowLinkInput(!showLinkInput);
                    triggerPress("link");
                  }}
                  className={`w-8 h-8 rounded-lg flex items-center justify-center transition-all duration-150 flex-shrink-0 ${
                    showLinkInput && !hasDoc ? "text-primary" : "text-muted-foreground hover:text-foreground"
                  } ${
                    pressedBtn === "link" ? "scale-[0.85] opacity-70" : ""
                  } ${isProcessing || hasDoc ? "opacity-40 cursor-not-allowed" : ""}`}
                  title={hasDoc ? "Retirez le document pour ajouter un lien" : "Insérer un lien"}
                >
                  <Link2 className="w-4 h-4" />
                </button>

                {/* Mic button */}
                <button
                  type="button"
                  disabled={isProcessing}
                  onClick={() => {
                    handleMicClick();
                    triggerPress("mic");
                  }}
                  className={`w-8 h-8 rounded-lg flex items-center justify-center transition-all duration-150 flex-shrink-0 ${
                    isDictating
                      ? "text-destructive hover:text-destructive/80"
                      : "text-muted-foreground hover:text-foreground"
                  } ${
                    pressedBtn === "mic" ? "scale-[0.85] opacity-70" : ""
                  } ${isProcessing ? "opacity-40 cursor-not-allowed" : ""}`}
                  title={isDictating ? "Arrêter la dictée" : "Dicter"}
                >
                  <Mic className="w-4 h-4" />
                </button>

                {/* Waveform inline right after mic, check button right after */}
                {isDictating && (
                  <div className="min-w-0 overflow-hidden">
                    <WaveformVisualizer analyserRef={analyserRef} />
                  </div>
                )}

                <div className="flex-1" />

                {/* Submit button: animated fade when dictating starts/stops */}
                <div
                  className={`transition-all duration-300 overflow-hidden flex-shrink-0 ${
                    showSubmitInText || showProcessingInText ? "opacity-100 w-8" : "opacity-0 w-0 pointer-events-none"
                  }`}
                >
                  {isProcessing ? (
                    <div className="w-8 h-8 rounded-lg flex items-center justify-center bg-primary text-primary-foreground">
                      <Loader2 className="w-4 h-4 animate-spin" />
                    </div>
                  ) : (
                    <button
                      type="button"
                      onClick={() => handleSubmit("text")}
                      className={`w-8 h-8 rounded-lg flex items-center justify-center transition-colors ${shakeSubmit ? "bg-destructive text-destructive-foreground animate-shake" : "bg-primary text-primary-foreground hover:bg-primary/90"}`}
                    >
                      <ArrowUp className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            </div>

            <div
              className={`w-full sm:max-w-lg mt-2 h-[48px] ${
                showLinkInput || hasDoc || (isProcessing && processingStatus)
                  ? "opacity-100 transition-opacity duration-300 ease-out"
                  : "opacity-0 pointer-events-none"
              }`}
            >
              {isProcessing && processingStatus ? (
                <div className="text-center py-3">
                  <TextShimmer className="font-body text-sm" duration={1.2}>
                    {processingStatus}
                  </TextShimmer>
                </div>
              ) : (
                <>
                  {hasDoc ? (
                    <div className="flex items-center w-full border border-dashed border-border rounded-xl">
                      <div className="pl-3 pr-2">
                        {(() => {
                          const ext = attachedFile!.name.split('.').pop()?.toLowerCase();
                          if (ext === 'pdf') return <FileType className="w-4 h-4 text-muted-foreground" />;
                          if (['png','jpg','jpeg','webp','gif','svg'].includes(ext || '')) return <Image className="w-4 h-4 text-muted-foreground" />;
                          if (['doc','docx','txt'].includes(ext || '')) return <FileText className="w-4 h-4 text-muted-foreground" />;
                          return <File className="w-4 h-4 text-muted-foreground" />;
                        })()}
                      </div>
                      <div className="flex items-center gap-2 flex-1 py-3 min-w-0">
                        <span className="font-body text-sm font-semibold text-foreground truncate">
                          {attachedFile!.name}
                        </span>
                        <span className="font-body text-xs text-muted-foreground flex-shrink-0">
                          {(attachedFile!.size / (1024 * 1024)).toFixed(2)} Mo
                        </span>
                        <button
                          type="button"
                          onClick={() => {
                            setAttachedFile(null);
                            setShowLinkInput(false);
                          }}
                          className="text-muted-foreground hover:text-foreground text-xs flex-shrink-0"
                          title="Retirer le document"
                        >
                          <X className="w-3.5 h-3.5" />
                        </button>
                      </div>
                      <div
                        className={`transition-all duration-300 overflow-hidden flex-shrink-0 ${
                          showSubmitInLink || showProcessingInLink
                            ? "opacity-100 w-8 mr-1.5"
                            : "opacity-0 w-0 pointer-events-none"
                        }`}
                      >
                        {isProcessing ? (
                          <div className="w-8 h-8 rounded-lg flex items-center justify-center bg-primary text-primary-foreground">
                            <Loader2 className="w-4 h-4 animate-spin" />
                          </div>
                        ) : (
                          <button
                            type="button"
                            onClick={() => handleSubmit("link")}
                            className={`w-8 h-8 rounded-lg flex items-center justify-center transition-colors ${shakeSubmit ? "bg-destructive text-destructive-foreground animate-shake" : "bg-primary text-primary-foreground hover:bg-primary/90"}`}
                          >
                            <ArrowUp className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="flex items-center w-full border border-dashed border-border rounded-xl">
                        <div className="pl-3 pr-2">
                          <Link2 className="w-4 h-4 text-muted-foreground" />
                        </div>
                        {prettyLinkName && !editingLink ? (
                          <div className="flex items-center gap-2 flex-1 py-3 pr-3 min-w-0">
                            <span
                              className="font-body text-sm font-semibold text-foreground truncate cursor-pointer hover:underline"
                              onClick={() => setEditingLink(true)}
                              title="Cliquer pour modifier le lien"
                            >
                              {prettyLinkName}
                            </span>
                            <button
                              type="button"
                              onClick={() => {
                                setLinkValue("");
                                setEditingLink(false);
                              }}
                              className="text-muted-foreground hover:text-foreground text-xs flex-shrink-0"
                              title="Supprimer le lien"
                            >
                              ✕
                            </button>
                          </div>
                        ) : (
                          <input
                            type="url"
                            autoFocus={editingLink}
                            value={linkValue}
                            onChange={(e) => setLinkValue(e.target.value)}
                            onBlur={() => setEditingLink(false)}
                            onKeyDown={(e) => {
                              if (e.key === "Enter") {
                                e.preventDefault();
                                handleSubmit("link");
                              }
                            }}
                            placeholder="Collez un lien vers un article, une vidéo, un post..."
                            className="w-full py-3 pr-3 bg-transparent font-body text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none"
                          />
                        )}
                        <div
                          className={`transition-all duration-300 overflow-hidden flex-shrink-0 ${
                            showSubmitInLink || showProcessingInLink
                              ? "opacity-100 w-8 mr-1.5"
                              : "opacity-0 w-0 pointer-events-none"
                          }`}
                        >
                          {isProcessing ? (
                            <div className="w-8 h-8 rounded-lg flex items-center justify-center bg-primary text-primary-foreground">
                              <Loader2 className="w-4 h-4 animate-spin" />
                            </div>
                          ) : (
                            <button
                              type="button"
                              onClick={() => handleSubmit("link")}
                              className={`w-8 h-8 rounded-lg flex items-center justify-center transition-colors ${shakeSubmit ? "bg-destructive text-destructive-foreground animate-shake" : "bg-primary text-primary-foreground hover:bg-primary/90"}`}
                            >
                              <ArrowUp className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </div>
                      <p
                        className={`font-body text-sm text-destructive mt-2 text-center transition-all duration-300 ${
                          linkError ? "opacity-100" : "opacity-0"
                        }`}
                      >
                        Le lien n'est pas valide
                      </p>
                    </>
                  )}
                </>
              )}
            </div>
          </div>
        )}

        {mode === "mic" && (
          <div className="flex flex-col items-center justify-center flex-1 py-8 px-6">
            {isRecording ? (
              <>
                <div
                  className="w-20 h-20 rounded-full bg-destructive text-destructive-foreground flex items-center justify-center scale-110 shadow-lg"
                  style={{ animation: "pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite" }}
                >
                  <Loader2 className="w-8 h-8 animate-spin" />
                </div>
                <div className="mt-4">
                  <TextShimmer className="font-body text-sm" duration={1.2}>
                    Début de l'écoute…
                  </TextShimmer>
                </div>
              </>
            ) : (
              <>
                <button
                  onClick={async () => {
                    try {
                      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                      // Permission granted — stop tracks immediately (LiveFactCheck will re-acquire)
                      stream.getTracks().forEach((t) => t.stop());
                      setMicError(false);
                      setIsRecording(true);
                      onStartRecording?.();
                    } catch {
                      setMicError(true);
                    }
                  }}
                  className="w-20 h-20 rounded-full flex items-center justify-center transition-all duration-300 bg-primary text-primary-foreground hover:scale-105"
                >
                  <Mic className="w-8 h-8" />
                </button>
                <p className="mt-4 font-body text-sm text-muted-foreground">Cliquez pour lancer l'écoute</p>
                {micError && (
                  <p className="mt-2 font-body text-sm text-destructive animate-fade-up">Accès au microphone refusé</p>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default InputZone;
