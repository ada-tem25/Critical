import React, { useState, useCallback, useRef, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Header from "@/components/Header";
import InputZone from "@/components/InputZone";
import ChatConversation, { type ChatMessage, type ChatAttachment } from "@/components/ChatConversation";
import ArchivesDrawer, { type DrawerTab } from "@/components/ArchivesDrawer";

import { FileText } from "lucide-react";

let msgCounter = 0;

const Index = () => {
  const location = useLocation();
  useEffect(() => {
    if ('scrollRestoration' in window.history) {
      window.history.scrollRestoration = 'manual';
    }
    window.scrollTo(0, 0);
  }, [location.key]);
  const navigate = useNavigate();
  const [profileOpen, setProfileOpen] = useState(false);
  const [archivesOpen, setArchivesOpen] = useState(false);
  const [drawerTab, setDrawerTab] = useState<DrawerTab>("featured");
  const [pageDragOver, setPageDragOver] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStatus, setProcessingStatus] = useState("");
  const dragCounter = React.useRef(0);
  const processingTimers = useRef<ReturnType<typeof setTimeout>[]>([]);

  const chatMode = chatMessages.length > 0;
  const anyPanelOpen = profileOpen || archivesOpen;

  // Prevent background scroll when a panel is open
  React.useEffect(() => {
    document.body.style.overflow = anyPanelOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [anyPanelOpen]);

  const handleOpenProfile = () => {
    setArchivesOpen(false);
    setProfileOpen(true);
  };

  const handleOpenDrawer = (tab: DrawerTab) => {
    setProfileOpen(false);
    setDrawerTab(tab);
    setArchivesOpen(true);
  };

  const handleNewConversation = useCallback(() => {
    // Cancel any in-progress processing
    processingTimers.current.forEach(clearTimeout);
    processingTimers.current = [];
    setIsProcessing(false);
    setProcessingStatus("");
    setChatMessages([]);
  }, []);

  const handleSubmit = useCallback((text: string, link: string, file?: File | null) => {
    const userContent = [text, link].filter(Boolean).join("\n");
    const attachment: ChatAttachment | undefined = file ? { name: file.name, size: file.size } : undefined;
    if (!userContent && !attachment) return;

    setIsProcessing(true);

    // Clear any previous timers
    processingTimers.current.forEach(clearTimeout);
    processingTimers.current = [];

    // Detect if user mentions "NASA" → redirect to existing article
    const isNasa = text.toUpperCase().includes("NASA");

    // Common first step: "Exploration du sujet..."
    setProcessingStatus("Exploration du sujet...");

    if (isNasa) {
      // Mode 1: Existing article found → redirect after exploration phase (no chat)
      const redirectTimer = setTimeout(() => {
        setIsProcessing(false);
        setProcessingStatus("");
        navigate("/article/nasa-eau-mars");
      }, 2500);
      processingTimers.current.push(redirectTimer);
    } else {
      // Mode 3: Simple conversation → show chat after exploration
      const enterChatTimer = setTimeout(() => {
        const userMsg: ChatMessage = {
          id: `msg-${++msgCounter}`,
          role: "user",
          content: userContent,
          attachment,
        };
        setChatMessages((prev) => [...prev, userMsg]);
        setProcessingStatus("Analyse de votre demande...");
      }, 2000);
      processingTimers.current.push(enterChatTimer);

      const doneTimer = setTimeout(() => {
        const assistantMsg: ChatMessage = {
          id: `msg-${++msgCounter}`,
          role: "assistant",
          content: "Merci pour votre question. Je suis en train d'analyser votre demande…",
        };
        setChatMessages((prev) => [...prev, assistantMsg]);
        setIsProcessing(false);
        setProcessingStatus("");
      }, 4000);
      processingTimers.current.push(doneTimer);
    }
  }, [navigate]);

  const handleStartRecording = useCallback(() => {
    // After a brief "Début de l'écoute" phase, navigate to live page
    const timer = setTimeout(() => {
      navigate("/live");
    }, 2500);
    processingTimers.current.push(timer);
  }, [navigate]);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    dragCounter.current++;
    if (e.dataTransfer.types.includes("Files")) {
      setPageDragOver(true);
    }
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    dragCounter.current--;
    if (dragCounter.current === 0) {
      setPageDragOver(false);
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    dragCounter.current = 0;
    setPageDragOver(false);
  }, []);

  return (
    <div
      className="flex flex-col bg-background relative h-screen overflow-hidden"
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      <Header
        profileOpen={profileOpen}
        onOpenProfile={handleOpenProfile}
        onCloseProfile={() => setProfileOpen(false)}
      />

      {/* Decorative rule */}
      <div className="w-full px-6">
        <div className="border-t border-rule" />
      </div>

      {/* Main content */}
      {chatMode ? (
        <main className="flex-1 flex flex-col min-h-0">
          <ChatConversation
            messages={chatMessages}
            onNewConversation={handleNewConversation}
          />
          <div className="shrink-0 px-6 pb-14 pt-2">
            <div className="w-full max-w-2xl mx-auto">
              <InputZone chatMode onSubmit={handleSubmit} isProcessing={isProcessing} processingStatus={processingStatus} />
            </div>
          </div>
        </main>
      ) : (
        <main className="flex-1 flex items-start justify-center px-6 pt-24">
          <InputZone onSubmit={handleSubmit} onStartRecording={handleStartRecording} isProcessing={isProcessing} processingStatus={processingStatus} />
        </main>
      )}

      <ArchivesDrawer isOpen={archivesOpen} activeTab={drawerTab} onOpen={handleOpenDrawer} onClose={() => setArchivesOpen(false)} />

      {/* Full-page drag overlay */}
      {pageDragOver && (
        <div className="fixed inset-0 z-50 bg-black/10 backdrop-blur-sm flex flex-col items-center justify-center pointer-events-none transition-opacity duration-200">
          <div className="w-20 h-20 rounded-2xl border-2 border-dashed border-primary flex items-center justify-center mb-6">
            <FileText className="w-9 h-9 text-primary" />
          </div>
          <p className="font-display text-xl font-semibold text-foreground">Déposez ici votre document à analyser</p>
          <p className="font-body text-sm text-muted-foreground mt-2">PDF, image, ou document texte</p>
        </div>
      )}
    </div>
  );
};

export default Index;
