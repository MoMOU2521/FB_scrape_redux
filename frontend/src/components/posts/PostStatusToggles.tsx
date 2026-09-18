import { Checkbox } from "@/components/ui/checkbox";

interface PostStatusTogglesProps {
  processed: boolean;
  selected: boolean;
  onProcessedChange: (checked: boolean) => void;
  onSelectedChange: (checked: boolean) => void;
}

export function PostStatusToggles({
  processed,
  selected,
  onProcessedChange,
  onSelectedChange,
}: PostStatusTogglesProps) {
  return (
    <div className="flex items-center gap-6 text-sm">
      <label className="flex items-center gap-2">
        <Checkbox
          checked={processed}
          onCheckedChange={(c) => onProcessedChange(c === true)}
        />
        Processed
      </label>
      <label className="flex items-center gap-2">
        <Checkbox
          checked={selected}
          onCheckedChange={(c) => onSelectedChange(c === true)}
        />
        Selected (valuable)
      </label>
    </div>
  );
}
