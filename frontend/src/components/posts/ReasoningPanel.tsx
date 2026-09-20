import { ChevronDown } from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface ReasoningPanelProps {
  label: string;
  promptVersion: string | null;
  reasoning: string | null;
  defaultOpen?: boolean;
}

export function ReasoningPanel({
  label,
  promptVersion,
  reasoning,
  defaultOpen = false,
}: ReasoningPanelProps) {
  return (
    <Collapsible defaultOpen={defaultOpen}>
      <Card className="gap-0 bg-background">
        <CollapsibleTrigger
          className={cn(
            "group flex w-full items-center justify-between gap-2",
            "text-sm font-base text-muted-foreground",
          )}
        >
          <span>
            🧠 {label} (prompt v{promptVersion ?? "unknown"})
          </span>
          <ChevronDown className="size-4 shrink-0 transition-transform group-data-[state=open]:rotate-180" />
        </CollapsibleTrigger>
        <CollapsibleContent>
          <CardContent className="mt-2 max-h-[400px] overflow-y-auto whitespace-pre-wrap text-sm text-foreground">
            {reasoning || "No reasoning recorded."}
          </CardContent>
        </CollapsibleContent>
      </Card>
    </Collapsible>
  );
}
