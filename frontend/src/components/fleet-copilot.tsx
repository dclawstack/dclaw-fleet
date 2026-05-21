"use client";

import { useState } from "react";
import { Bot, Send, X, Sparkles } from "lucide-react";

import { fleetAi, type ChatMessage } from "@/lib/api";
import { cn } from "@/lib/utils";

export function FleetCopilot() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([
    "How many vehicles do I have?",
    "List overdue maintenance",
    "Show fuel efficiency",
  ]);
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  async function send(content: string) {
    if (!content.trim() || sending) return;
    setSending(true);
    try {
      const turn = await fleetAi.chat(content, sessionId);
      setSessionId(turn.session_id);
      setMessages((m) => [...m, turn.user_message, turn.assistant_message]);
      setSuggestions(turn.suggested_actions);
      setInput("");
    } catch (e) {
      console.error(e);
    } finally {
      setSending(false);
    }
  }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 z-50 flex items-center gap-2 rounded-full bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-lg hover:bg-blue-700"
      >
        <Sparkles className="h-4 w-4" />
        Fleet Copilot
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 z-50 flex h-[560px] w-[400px] flex-col rounded-2xl border bg-white shadow-2xl">
      <header className="flex items-center justify-between border-b px-4 py-3">
        <div className="flex items-center gap-2">
          <Bot className="h-5 w-5 text-blue-600" />
          <span className="font-semibold text-slate-900">Fleet Copilot</span>
        </div>
        <button onClick={() => setOpen(false)} className="text-slate-400 hover:text-slate-600">
          <X className="h-4 w-4" />
        </button>
      </header>

      <div className="flex-1 space-y-3 overflow-y-auto px-4 py-3">
        {messages.length === 0 && (
          <p className="text-sm text-slate-500">
            Ask anything about your fleet — vehicles, drivers, maintenance, fuel, routes.
          </p>
        )}
        {messages.map((m) => (
          <div
            key={m.id}
            className={cn(
              "rounded-xl px-3 py-2 text-sm",
              m.role === "user"
                ? "ml-auto max-w-[85%] bg-blue-600 text-white"
                : "mr-auto max-w-[85%] bg-slate-100 text-slate-900"
            )}
          >
            {m.content}
          </div>
        ))}
      </div>

      {suggestions.length > 0 && (
        <div className="flex flex-wrap gap-2 border-t px-4 py-2">
          {suggestions.map((s) => (
            <button
              key={s}
              onClick={() => send(s)}
              className="rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs text-blue-700 hover:bg-blue-100"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
        className="flex items-center gap-2 border-t px-3 py-3"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask the copilot..."
          className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-500"
          disabled={sending}
        />
        <button
          type="submit"
          disabled={sending || !input.trim()}
          className="rounded-lg bg-blue-600 p-2 text-white hover:bg-blue-700 disabled:opacity-60"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  );
}
