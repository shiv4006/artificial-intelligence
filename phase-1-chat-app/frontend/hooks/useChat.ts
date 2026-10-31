"use client";

import { api } from "@/lib/api";
import { streamChat } from "@/lib/sse";
import type { UIMessage } from "@/lib/types";
import { useCallback, useRef, useState } from "react";


function newMessage(role: UIMessage["role"], content: string, model: string | null): UIMessage {
    return {
        key: crypto.randomUUID(),
        role,
        content,
        model,
        prompt_tokens: null,
        completion_tokens: null,
        reasoning_tokens: null,
        cost_usd: null,
        status: role === "user" ? "done" : "streaming",
    };
}

export function useChat() {
    const [messages, setMessages] = useState<UIMessage[]>([]);
    const [isStreaming, setIsStreaming] = useState(false);
    const controllerRef = useRef<AbortController | null>(null);

    const stop = useCallback(() => controllerRef.current?.abort(), []);

    // Load a conversation's saved messages, or clear the view for a new chat.
    const load = useCallback(
        async (conversationId: string | null) => {
            stop();
            if (conversationId === null) {
                setMessages([]);
                return;
            }
            const detail = await api.getConversation(conversationId);
            setMessages(detail.messages.map((m) => ({ ...m, key: String(m.id), status: "done" })));
        },
        [stop],
    );

    const send = useCallback(async (conversationId: string, model: string, content: string) => {
        const controller = new AbortController();
        controllerRef.current = controller;
        setIsStreaming(true);

        const user = newMessage("user", content, null);
        const reply = newMessage("assistant", "", model);
        setMessages((prev) => [...prev, user, reply]);

        // Apply a change to the reply that is streaming in.
        const update = (change: (m: UIMessage) => Partial<UIMessage>) => setMessages((prev) => prev.map((m) => (m.key === reply.key ? { ...m, ...change(m) } : m)));

        try {
            for await (const event of streamChat(conversationId, content, controller.signal)) {
                if (event.type === "token") {
                    update((m) => ({ content: m.content + event.text }));
                } else if (event.type === "error") {
                    update(() => ({ status: "error", error: event.message }));
                } else if (event.type === "done") {
                    update(() => ({
                        status: "done",
                        finish_reason: event.finish_reason,
                        prompt_tokens: event.usage.prompt_tokens ?? null,
                        completion_tokens: event.usage.completion_tokens ?? null,
                        reasoning_tokens: event.usage.reasoning_tokens ?? null,
                        cost_usd: event.cost_usd,
                    }));
                }
            }

            // The stream closed without a done or error event.
            update((m) => (m.status === "streaming" ? { status: "error", error: "The stream ended early." } : {}));
        } catch (err) {
            if (controller.signal.aborted) {
                update(() => ({ status: "stopped" }));
            } else {
                update(() => ({ status: "error", error: String(err) }));
            }
        } finally {
            controllerRef.current = null;
            setIsStreaming(false);
        }
    }, []);

    return { messages, isStreaming, load, send, stop };
}