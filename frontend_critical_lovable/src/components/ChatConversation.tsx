import { useEffect, useRef, useState } from "react";
import { ArrowLeft, Copy, Check, FileText, FileType, Image, File } from "lucide-react";

export interface ChatAttachment {
  name: string;
  size: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  attachment?: ChatAttachment;
}

interface ChatConversationProps {
  messages: ChatMessage[];
  onNewConversation: () => void;
}

const CopyButton = ({ text }: { text: string }) => {
  const [copied, setCopied] = useState(false);
  const [pressed, setPressed] = useState(false);

  const handleCopy = async () => {
    setPressed(true);
    setTimeout(() => setPressed(false), 150);
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {}
  };

  return (
    <div className="h-0 overflow-visible opacity-0 group-hover/msg:opacity-100 transition-opacity duration-150">
      <button
        onClick={handleCopy}
        className={`w-8 h-8 rounded-lg flex items-center justify-center transition-all duration-150 text-muted-foreground hover:text-foreground ${
          pressed ? "scale-[0.85] opacity-70" : ""
        }`}
        title={copied ? "Copié" : "Copier"}
      >
        {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
      </button>
    </div>
  );
};

const ChatConversation = ({ messages, onNewConversation }: ChatConversationProps) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="w-full max-w-2xl mx-auto flex flex-col flex-1 min-h-0">
      {/* Back button */}
      <div className="flex justify-start pt-4 pb-4 px-6">
        <button
          onClick={onNewConversation}
          className="flex items-center gap-2 font-ui text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Retour
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 px-6">
        {messages.map((msg) => (
          <div key={msg.id} className={`group/msg flex animate-fade-up-in ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className="max-w-[80%]">
              <div
                className={`rounded-xl px-4 py-3 font-body text-sm leading-relaxed whitespace-pre-wrap ${
                  msg.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-card border border-border text-foreground"
                }`}
              >
                {msg.content}
                {msg.attachment && (
                  <div className={`flex items-center gap-2 ${msg.content ? `mt-2 pt-2 border-t ${msg.role === "user" ? "border-primary-foreground/20" : "border-border"}` : ""}`}>
                    {(() => {
                      const ext = msg.attachment.name.split('.').pop()?.toLowerCase();
                      const cls = `w-4 h-4 flex-shrink-0 ${msg.role === "user" ? "text-primary-foreground/70" : "text-muted-foreground"}`;
                      if (ext === 'pdf') return <FileType className={cls} />;
                      if (['png','jpg','jpeg','webp','gif','svg'].includes(ext || '')) return <Image className={cls} />;
                      if (['doc','docx','txt'].includes(ext || '')) return <FileText className={cls} />;
                      return <File className={cls} />;
                    })()}
                    <span className="truncate text-xs opacity-80">{msg.attachment.name}</span>
                  </div>
                )}
              </div>
              {msg.role === "assistant" && <CopyButton text={msg.content} />}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
};

export default ChatConversation;
