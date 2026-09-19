// frontend/src/App.tsx
import { useState } from "react";
import { PostPage } from "@/pages/PostPage";
import { ProcessedPage } from "@/pages/ProcessedPage";
import { Button } from "@/components/ui/button";

type View = "unprocessed" | "processed";

function App() {
  const [view, setView] = useState<View>("unprocessed");

  return (
    <div className="flex flex-col gap-4">
      <div className="mx-auto flex max-w-2xl gap-2 pt-6">
        <Button
          variant={view === "unprocessed" ? "default" : "neutral"}
          size="sm"
          onClick={() => setView("unprocessed")}
        >
          Unprocessed
        </Button>
        <Button
          variant={view === "processed" ? "default" : "neutral"}
          size="sm"
          onClick={() => setView("processed")}
        >
          Processed
        </Button>
      </div>
      {view === "unprocessed" ? <PostPage /> : <ProcessedPage />}
    </div>
  );
}

export default App;
