import { API_URL } from "./api";
import type { ChatEvent } from "./types";

// POST a message and yield each server-sent event as soon as it arrives.
export async function* streamChat(
    conversationId: string,
    content: string,
    signal: AbortSignal,
): AsyncGenerator<ChatEvent> {
    const res = await fetch(`${API_URL}/conversations/${conversationId}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content }),
        signal,
    });
    if (!res.ok || !res.body) {
        throw new Error(`Chat failed: ${res.status} ${await res.text()}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        // stream: true keep a multi-byte character that was split across chunks.
        buffer += decoder.decode(value, { stream: true });

        // Events end with a blank line. The last piece may be incomplete, so keep it for the next read.
        const events = buffer.split("\n\n");
        buffer = events.pop() ?? "";

        for (const event of events) {
            for (const line of event.split("\n")) {
                if (line.startsWith("data: ")) {
                    yield JSON.parse(line.slice(6)) as ChatEvent;
                }
            }
        }
    }
}