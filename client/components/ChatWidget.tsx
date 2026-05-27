"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";

type Message = {
  role: "user" | "assistant";
  content: string;
};

const SUGGESTIONS = [
  "What is ACH50?",
  "Explain the ECM measures",
  "What does SEER2 mean?",
  "How do I use a .pkl file?",
  "Which ECMs have the best payback?",
];

function TypingDots() {
  return (
    <span className="inline-flex items-center gap-1 py-0.5">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="w-1.5 h-1.5 rounded-full bg-brand-400 animate-bounce"
          style={{ animationDelay: `${i * 0.15}s`, animationDuration: "0.8s" }}
        />
      ))}
    </span>
  );
}

function MessageBubble({ msg }: { msg: Message }) {
  const isUser = msg.role === "user";
  return (
    <div className={`flex gap-2 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
      {!isUser && (
        <div className="w-7 h-7 rounded-full bg-primary flex items-center justify-center flex-shrink-0 mt-0.5">
          <svg viewBox="0 0 20 20" fill="none" className="w-4 h-4 text-white">
            <path d="M10 2a6 6 0 016 6c0 2.5-1.5 4.7-3.7 5.7L12 16H8l-.3-2.3C5.5 12.7 4 10.5 4 8a6 6 0 016-6z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/>
            <path d="M7 16.5h6M8 19h4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
        </div>
      )}
      <div
        className={`max-w-[82%] px-3.5 py-2.5 rounded-2xl text-sm leading-relaxed ${
          isUser
            ? "bg-primary text-white rounded-tr-sm"
            : "bg-brand-50 text-app-text border border-brand-100 rounded-tl-sm"
        }`}
      >
        {msg.content === "" ? <TypingDots /> : (
          <span className="whitespace-pre-wrap">{msg.content}</span>
        )}
      </div>
    </div>
  );
}

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isOpen]);

  const sendMessage = useCallback(async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || isLoading) return;

    const userMsg: Message = { role: "user", content: trimmed };
    const newHistory: Message[] = [...messages, userMsg];
    setMessages([...newHistory, { role: "assistant", content: "" }]);
    setInput("");
    setIsLoading(true);

    abortRef.current = new AbortController();

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: newHistory }),
        signal: abortRef.current.signal,
      });

      if (!res.ok || !res.body) throw new Error("Request failed");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.role === "assistant") {
            return [...prev.slice(0, -1), { ...last, content: last.content + chunk }];
          }
          return prev;
        });
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name !== "AbortError") {
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.role === "assistant" && last.content === "") {
            return [
              ...prev.slice(0, -1),
              { role: "assistant", content: "Sorry, something went wrong. Please try again." },
            ];
          }
          return prev;
        });
      }
    } finally {
      setIsLoading(false);
      abortRef.current = null;
      inputRef.current?.focus();
    }
  }, [messages, isLoading]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  const handleClose = () => {
    abortRef.current?.abort();
    setIsOpen(false);
  };

  const handleClear = () => {
    abortRef.current?.abort();
    setMessages([]);
    setIsLoading(false);
  };

  return (
    <>
      {/* Floating button */}
      <button
        onClick={() => setIsOpen((o) => !o)}
        aria-label="Open Audit Assistant"
        className={`fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full flex items-center justify-center shadow-lg transition-all duration-200 ${
          isOpen
            ? "bg-primary scale-90 opacity-0 pointer-events-none"
            : "bg-primary hover:bg-primary-hover scale-100 opacity-100"
        }`}
        style={{ boxShadow: "0 4px 24px rgba(12,61,0,0.30)" }}
      >
        <svg viewBox="0 0 24 24" fill="none" className="w-6 h-6 text-white">
          <path
            d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {/* Chat panel */}
      <div
        className={`fixed bottom-6 right-6 z-50 flex flex-col w-[380px] transition-all duration-300 origin-bottom-right ${
          isOpen
            ? "opacity-100 scale-100 pointer-events-auto"
            : "opacity-0 scale-90 pointer-events-none"
        }`}
        style={{
          height: "540px",
          borderRadius: "20px",
          boxShadow: "0 8px 40px rgba(12,61,0,0.18)",
          overflow: "hidden",
          border: "1px solid #b9deb8",
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 bg-primary flex-shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center">
              <svg viewBox="0 0 20 20" fill="none" className="w-4.5 h-4.5 text-white">
                <path d="M10 2a6 6 0 016 6c0 2.5-1.5 4.7-3.7 5.7L12 16H8l-.3-2.3C5.5 12.7 4 10.5 4 8a6 6 0 016-6z" stroke="white" strokeWidth="1.5" strokeLinejoin="round"/>
                <path d="M7 16.5h6M8 19h4" stroke="white" strokeWidth="1.5" strokeLinecap="round"/>
              </svg>
            </div>
            <div>
              <p className="text-sm font-semibold text-white leading-none">Audit Assistant</p>
              <p className="text-[11px] text-brand-200 leading-none mt-0.5">Ask anything about the tool</p>
            </div>
          </div>
          <div className="flex items-center gap-1">
            {messages.length > 0 && (
              <button
                onClick={handleClear}
                title="Clear conversation"
                className="p-1.5 rounded-lg text-brand-200 hover:text-white hover:bg-primary-light transition-colors"
              >
                <svg viewBox="0 0 16 16" fill="none" className="w-4 h-4">
                  <path d="M3 4h10M6 4V3h4v1M5 4l.5 9h5L11 4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>
            )}
            <button
              onClick={handleClose}
              title="Close"
              className="p-1.5 rounded-lg text-brand-200 hover:text-white hover:bg-primary-light transition-colors"
            >
              <svg viewBox="0 0 16 16" fill="none" className="w-4 h-4">
                <path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
              </svg>
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto bg-white px-4 py-4 flex flex-col gap-3">
          {messages.length === 0 ? (
            <div className="flex flex-col h-full">
              <div className="flex-1 flex flex-col items-center justify-center gap-3 text-center px-4">
                <div className="w-12 h-12 rounded-full bg-brand-50 border border-brand-200 flex items-center justify-center">
                  <svg viewBox="0 0 24 24" fill="none" className="w-6 h-6 text-primary">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-semibold text-app-text">Building Audit Assistant</p>
                  <p className="text-xs text-app-text-muted mt-1 leading-relaxed">
                    Ask me about input fields, ECM measures, energy terms, or how to use the tool.
                  </p>
                </div>
              </div>
              <div className="flex flex-col gap-1.5 mt-2">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => sendMessage(s)}
                    className="text-left text-xs px-3 py-2 rounded-xl border border-brand-200 text-brand-700 hover:bg-brand-50 hover:border-brand-400 transition-colors"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, i) => (
                <MessageBubble key={i} msg={msg} />
              ))}
              <div ref={bottomRef} />
            </>
          )}
        </div>

        {/* Input */}
        <div className="flex-shrink-0 bg-white border-t border-brand-100 px-3 py-3">
          <div className="flex items-center gap-2 bg-bg-muted rounded-xl px-3 py-2 border border-border focus-within:border-accent transition-colors">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question…"
              disabled={isLoading}
              className="flex-1 bg-transparent text-sm text-app-text placeholder-app-text-light outline-none"
            />
            <button
              onClick={() => sendMessage(input)}
              disabled={!input.trim() || isLoading}
              className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 transition-all ${
                input.trim() && !isLoading
                  ? "bg-primary text-white hover:bg-primary-hover"
                  : "bg-border text-app-text-light cursor-not-allowed"
              }`}
            >
              <svg viewBox="0 0 16 16" fill="none" className="w-4 h-4">
                <path d="M2 8h12M10 4l4 4-4 4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
