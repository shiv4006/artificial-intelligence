"use client";

import { useEffect, useRef, useState } from "react";

import Composer from "@/components/Composer";
import MessageBubble from "@/components/MessageBubble";
import ModelPicker from "@/components/ModelPicker";
import Sidebar from "@/components/Sidebar";
import { useChat } from "@/hooks/useChat";
import { api } from "@/lib/api";
import type { Conversation, Model } from "@/lib/types";

const DEFAULT_MODEL = "openai/gpt-oss-20b";

export default function Chat() {
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [models, setModels] = useState<Model[]>([]);
    const [activeId, setActiveId] = useState<string | null>(null);
    const [newChatModel, setNewChatModel] = useState(DEFAULT_MODEL);
    const [error, setError] = useState<string | null>(null);
    const { messages, isStreaming, load, send, stop } = useChat();
    const bottomRef = useRef<HTMLDivElement>(null);

    const active = conversations.find((c) => c.id === activeId) ?? null;
    const model = active?.model ?? newChatModel;
    const totalCost = messages.reduce((sum, m) => sum + (m.cost_usd ?? 0), 0);

    const report = (err: unknown) => setError(String(err));

    useEffect(() => {
        Promise.all([api.listModels(), api.listConversations()])
            .then(([models, conversations]) => {
                setModels(models);
                setConversations(conversations);
            })
            .catch(report);
    }, []);

    // Keep the newest text in view while a reply streams in.
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ block: "end" });
    }, [messages]);

    async function selectConversation(id: string) {
        setActiveId(id);
        await load(id);
    }

    async function newChat() {
        setActiveId(null);
        await load(null);
    }

    async function handleSend(content: string) {
        let id = activeId;
        if (id === null) {
            // First message of a new chat: create the conversation, titled after the message.
            const created = await api.createConversation({ title: content.slice(0, 40), model: newChatModel });
            setConversations((prev) => [created, ...prev]);
            setActiveId(created.id);
            id = created.id;
        }
        await send(id, model, content);
        setConversations(await api.listConversations()); // re-sort by latest activity
    }

    async function handleModelChange(next: string) {
        if (active === null) {
            setNewChatModel(next);
            return;
        }
        const updated = await api.updateConversation(active.id, { model: next });
        setConversations((prev) => prev.map((c) => (c.id === updated.id ? updated : c)));
    }

    async function handleDelete(id: string) {
        if (!window.confirm("Delete this conversation?")) return;
        await api.deleteConversation(id);
        setConversations((prev) => prev.filter((c) => c.id !== id));
        if (id === activeId) await newChat();
    }

    return (
        <div className="flex h-dvh font-sans">
            <Sidebar
                conversations={conversations}
                activeId={activeId}
                onSelect={(id) => selectConversation(id).catch(report)}
                onNew={() => newChat().catch(report)}
                onDelete={(id) => handleDelete(id).catch(report)}
            />

            <main className="flex min-w-0 flex-1 flex-col">
                <header className="flex items-center justify-between gap-4 border-b border-zinc-200 px-4 py-3 dark:border-zinc-800">
                    <h1 className="truncate font-medium">{active?.title ?? "New chat"}</h1>
                    <div className="flex shrink-0 items-center gap-3 text-sm text-zinc-500">
                        {totalCost > 0 && <span>Total ${totalCost.toFixed(6)}</span>}
                        <ModelPicker
                            models={models}
                            value={model}
                            disabled={isStreaming}
                            onChange={(m) => handleModelChange(m).catch(report)}
                        />
                    </div>
                </header>

                {error && (
                    <div className="bg-red-50 px-4 py-2 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">
                        {error}
                        <button onClick={() => setError(null)} className="ml-3 underline">
                            Dismiss
                        </button>
                    </div>
                )}

                <div className="flex-1 overflow-y-auto">
                    <div className="mx-auto max-w-3xl space-y-6 px-4 py-6">
                        {messages.length === 0 && <p className="text-center text-zinc-500">Send a message to start.</p>}
                        {messages.map((m) => (
                            <MessageBubble key={m.key} message={m} />
                        ))}
                        <div ref={bottomRef} />
                    </div>
                </div>

                <div className="mx-auto w-full max-w-3xl">
                    <Composer isStreaming={isStreaming} onSend={(c) => handleSend(c).catch(report)} onStop={stop} />
                </div>
            </main>
        </div>
    );
}