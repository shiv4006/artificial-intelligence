import type { Model } from "@/lib/types";

type Props = {
    models: Model[];
    value: string;
    disabled: boolean;
    onChange: (model: string) => void;
};

export default function ModelPicker({ models, value, disabled, onChange }: Props) {
    return (
        <select
            className="rounded-lg border border-zinc-300 bg-transparent px-2 py-1 text-sm dark:border-zinc-700"
            value={value}
            disabled={disabled}
            onChange={(e) => onChange(e.target.value)}
        >
            {models.map((m) => (
                <option key={m.id} value={m.id}>
                    {m.id.replace("openai/", "")} (${m.input_price_per_million} / ${m.output_price_per_million} per 1M)
                </option>
            ))}
        </select>
    );
}