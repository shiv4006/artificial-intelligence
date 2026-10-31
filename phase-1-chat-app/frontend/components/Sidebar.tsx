import type { Conversation } from "@/lib/types";

type Props = {
    conversations: Conversation[];
    activeId: string | null;
    onSelect: (id: string) => void;
    onNew: () => void;
    onDelete: (id: string) => void;
};

export default function Sidebar({ conversations, activeId, onSelect, onNew, onDelete }: Props) {
    return (
        <aside className="flex w-64 shrink-0 flex-col border-r border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-950">
            <button
                onClick={onNew}
                className="m-3 rounded-lg border border-zinc-300 px-3 py-2 text-left text-sm hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-900"
            >
                + New chat
            </button>

            <nav className="flex-1 overflow-y-auto px-2 pb-3">
                {conversations.map((c) => (
                    <div
                        key={c.id}
                        className={`group flex items-center rounded-lg text-sm ${c.id === activeId ? "bg-zinc-200 dark:bg-zinc-800" : "hover:bg-zinc-100 dark:hover:bg-zinc-900"
                            }`}
                    >
                        <button onClick={() => onSelect(c.id)} className="flex-1 truncate px-3 py-2 text-left">
                            {c.title}
                        </button>
                        <button
                            onClick={() => onDelete(c.id)}
                            aria-label={`Delete ${c.title}`}
                            className="px-2 text-zinc-400 opacity-0 hover:text-red-600 group-hover:opacity-100"
                        >
                            ×
                        </button>
                    </div>
                ))}
            </nav>
        </aside>
    );
}