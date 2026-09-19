// frontend/src/App.tsx
import { useState } from "react";
import { PostPage } from "@/pages/PostPage";
import { ProcessedPage } from "@/pages/ProcessedPage";
import { BlacklistPage } from "@/pages/BlacklistPage";
import { FiltersPage } from "@/pages/FiltersPage";
import { ReviewPage } from "@/pages/ReviewPage";
import { ReviewBuildingPage } from "@/pages/ReviewBuildingPage";
import { StatsPage } from "@/pages/StatsPage";
import { Button } from "@/components/ui/button";

type View =
  | "unprocessed"
  | "processed"
  | "blacklist"
  | "filters"
  | "review"
  | "review-building"
  | "stats";

function App() {
  const [view, setView] = useState<View>("unprocessed");
  const [authorRowId, setAuthorRowId] = useState<number | null>(null);

  const views: { key: View; label: string }[] = [
    { key: "unprocessed", label: "Unprocessed" },
    { key: "processed", label: "Processed" },
    { key: "review", label: "Review" },
    { key: "review-building", label: "Building Review" },
    { key: "stats", label: "Stats" },
    { key: "blacklist", label: "Blacklist" },
    { key: "filters", label: "Filters" },
  ];

  return (
    <div className="flex flex-col gap-4">
      <div className="mx-auto flex max-w-2xl flex-wrap gap-2 pt-6">
        {views.map((v) => (
          <Button
            key={v.key}
            variant={view === v.key ? "default" : "neutral"}
            size="sm"
            onClick={() => {
              if (v.key !== "unprocessed") setAuthorRowId(null);
              setView(v.key);
            }}
          >
            {v.label}
          </Button>
        ))}
      </div>
      {view === "unprocessed" && <PostPage initialAuthorRowId={authorRowId} />}
      {view === "processed" && <ProcessedPage />}
      {view === "review" && <ReviewPage />}
      {view === "review-building" && <ReviewBuildingPage />}
      {view === "stats" && (
        <StatsPage
          onViewAuthorPosts={(rowId) => {
            setAuthorRowId(rowId);
            setView("unprocessed");
          }}
        />
      )}
      {view === "blacklist" && <BlacklistPage />}
      {view === "filters" && <FiltersPage />}
    </div>
  );
}

export default App;
