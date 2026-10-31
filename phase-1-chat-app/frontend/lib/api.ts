import type { Conversation, ConversationDetail, Model } from "./types";

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
    const res = await fetch(`${API_URL}${path}`, {
        ...init,
        headers: init.body ? { "Content-Type": "application/json" } : undefined,
    });
    if (!res.ok) {
        throw new Error(`${init.method ?? "GET"} ${path} failed: ${res.status} ${await res.text()}`);
    }
    return res.status === 204 ? (undefined as T) : res.json();
}

export const api = {
    listModels: () => request<Model[]>("/models"),
    listConversations: () => request<Conversation[]>("/conversations"),
    getConversation: (id: string) => request<ConversationDetail>(`/conversations/${id}`),
    createConversation: (body: { title: string; model: string }) => request<Conversation>("/conversations", { method: "POST", body: JSON.stringify(body) }),
    updateConversation: (id: string, body: { title?: string; model?: string }) => request<Conversation>(`/conversations/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
    deleteConversation: (id: string) => request<void>(`/conversations/${id}`, { method: "DELETE" }),
};