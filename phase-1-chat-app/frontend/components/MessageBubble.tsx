import Markdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import remarkBreaks from "remark-breaks";
import remarkGfm from "remark-gfm";

import type { UIMessage } from "@/lib/types";

function UsageLine({ message }: { message: UIMessage }) {
    const parts: string[] = [];
    if (message.model) parts.push(message.model.replace("openai/", ""));
    if (message.prompt_tokens !== null) parts.push(`${message.prompt_tokens} in`);
    if (message.completion_tokens !== null) {
        const reasoning = message.reasoning_tokens ? ` (${message.reasoning_tokens} reasoning)` : "";
        parts.push(`${message.completion_tokens} out${reasoning}`);
    }
    if (message.cost_usd !== null) parts.push(`$${message.cost_usd.toFixed(6)}`);
    return <div className="mt-2 text-xs text-zinc-500">{parts.join(" · ")}</div>;
}

export default function MessageBubble({ message }: { message: UIMessage }) {
    if (message.role === "user") {
        return (
            <div className="flex justify-end">
                <div className="max-w-[80%] whitespace-pre-wrap rounded-2xl bg-zinc-200 px-4 py-2 dark:bg-zinc-800">
                    {message.content}
                </div>
            </div>
        );
    }

    return (
        <div>
            <div className="prose prose-zinc max-w-none dark:prose-invert prose-pre:p-0">
                <Markdown remarkPlugins={[remarkGfm, remarkBreaks]} rehypePlugins={[rehypeHighlight]}>
                    {message.content}
                </Markdown>
                {message.status === "streaming" && <span className="animate-pulse">▍</span>}
            </div>

            {message.status === "stopped" && <div className="mt-2 text-xs text-amber-600">Stopped</div>}
            {message.status === "error" && <div className="mt-2 text-sm text-red-600">Error: {message.error}</div>}
            {message.finish_reason === "length" && (
                <div className="mt-2 text-xs text-amber-600">Cut off: the reply hit the output token limit.</div>
            )}
            {message.status === "done" && <UsageLine message={message} />}
        </div>
    );
}