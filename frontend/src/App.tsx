import { useState } from "react";
import { PostPage } from "@/pages/PostPage";
import { ProcessedPage } from "@/pages/ProcessedPage";
import { BlacklistPage } from "@/pages/BlacklistPage";
import { FiltersPage } from "@/pages/FiltersPage";
import { Button } from "@/components/ui/button";

type View = "unprocessed" | "processed" | "blacklist" | "filters";

function App() {
  const [view, setView] = useState<View>("unprocessed");

  const views: { key: View; label: string }[] = [
    { key: "unprocessed", label: "Unprocessed" },
    { key: "processed", label: "Processed" },
    { key: "blacklist", label: "Blacklist" },
    { key: "filters", label: "Filters" },
  ];

  return (
    <div className="flex flex-col gap-4">
      <div className="mx-auto flex max-w-2xl gap-2 pt-6">
        {views.map((v) => (
          <Button
            key={v.key}
            variant={view === v.key ? "default" : "neutral"}
            size="sm"
            onClick={() => setView(v.key)}
          >
            {v.label}
          </Button>
        ))}
      </div>
      {view === "unprocessed" && <PostPage />}
      {view === "processed" && <ProcessedPage />}
      {view === "blacklist" && <BlacklistPage />}
      {view === "filters" && <FiltersPage />}
    </div>
  );
}

export default App;
