"use client";

import { useState } from "react";

type Props = {
    isStreaming: boolean;
    onSend: (content: string) => void;
    onStop: () => void;
};

export default function Composer({ isStreaming, onSend, onStop }: Props) {
    const [text, setText] = useState("");

    function submit() {
        const content = text.trim();
        if (!content || isStreaming) return;
        onSend(content);
        setText("");
    }

    return (
        <form
            className="flex items-end gap-2 border-t border-zinc-200 p-4 dark:border-zinc-800"
            onSubmit={(e) => {
                e.preventDefault();
                submit();
            }}
        >
            <textarea
                className="max-h-48 flex-1 resize-none rounded-xl border border-zinc-300 bg-transparent px-4 py-3 outline-none focus:border-zinc-500 dark:border-zinc-700"
                rows={1}
                placeholder="Message (Enter to send, Shift+Enter for a new line)"
                value={text}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        submit();
                    }
                }}
            />
            {isStreaming ? (
                <button type="button" onClick={onStop} className="rounded-xl bg-red-600 px-4 py-3 text-white">
                    Stop
                </button>
            ) : (
                <button
                    type="submit"
                    disabled={!text.trim()}
                    className="rounded-xl bg-zinc-900 px-4 py-3 text-white disabled:opacity-40 dark:bg-zinc-100 dark:text-zinc-900"
                >
                    Send
                </button>
            )}
        </form>
    );
}