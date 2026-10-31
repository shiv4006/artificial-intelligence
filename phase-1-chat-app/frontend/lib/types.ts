// Mirrors backend/app/schemas.py and the events sent by routers/chat.py

export type Model = {
    id: string;
    input_price_per_million: number;
    output_price_per_million: number;
};

export type Conversation = {
    id: string;
    title: string;
    model: string;
    system_prompt: string;
    created_at: string;
    updated_at: string;
};

export type Message = {
    id: number;
    role: "user" | "assistant";
    content: string;
    model: string | null;
    prompt_tokens: number | null;
    completion_tokens: number | null;
    reasoning_tokens: number | null;
    cost_usd: number | null;
    created_at: string;
};

export type ConversationDetail = Conversation & { messages: Message[] };

export type Usage = {
    prompt_tokens: number;
    completion_tokens: number;
    reasoning_tokens: number | null;
};

export type ChatEvent =
    | { type: "token"; text: string }
    | { type: "error"; message: string }
    | {
        type: "done";
        message_id: number;
        finish_reason: string | null;
        usage: Partial<Usage>;
        cost_usd: number | null;
    };

// A message as the UI holds it: may still be streaming and has no database id yet.
export type UIMessage = Omit<Message, "id" | "created_at"> & {
    key: string;
    status: "done" | "streaming" | "stopped" | "error";
    finish_reason?: string | null;
    error?: string;
};