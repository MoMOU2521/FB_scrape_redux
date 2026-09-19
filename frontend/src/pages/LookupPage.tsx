// frontend/src/pages/LookupPage.tsx
import { useState } from "react";
import * as api from "@/api/posts";
import type { LookupPost } from "@/api/posts";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { TextBlock } from "@/components/posts/TextBlock";
import { ReasoningPanel } from "@/components/posts/ReasoningPanel";

export function LookupPage() {
  const [id, setId] = useState("");
  const [post, setPost] = useState<LookupPost | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function search() {
    setError(null);
    try {
      const res = await api.lookupPost(id.trim());
      setPost(res.post);
    } catch (e) {
      setPost(null);
      setError((e as Error).message);
    }
  }

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-4 p-6">
      <h2 className="text-lg font-base">Scraped Post Lookup</h2>

      <div className="flex gap-2">
        <Input
          type="number"
          min={1}
          placeholder="SQLite Row ID"
          value={id}
          onChange={(e) => setId(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && search()}
        />
        <Button onClick={search}>Search</Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {post && (
        <>
          <Card>
            <CardContent className="flex flex-col gap-1 text-sm">
              <span className="font-base text-base">{post.author}</span>
              <span>Group: {post.group_name}</span>
              <span>Post ID: {post.post_id}</span>
              <span>SQLite Row ID: {post.id}</span>
              <span>Processed: {post.processed ? "Yes" : "No"}</span>
              <span>Selected: {post.selected ? "Yes" : "No"}</span>
              <span>AI Processed: {post.ai_processed ? "Yes" : "No"}</span>
              <span>
                Building Review: {post.review_building ? "Yes" : "No"}
              </span>
              <span>Scraped at: {post.scraped_at}</span>
              <span>
                Original:{" "}
                <a href={post.post_url} target="_blank" rel="noreferrer">
                  {post.post_url}
                </a>
              </span>
            </CardContent>
          </Card>

          <TextBlock label="Post text" text={post.text} />

          <TextBlock
            label="AI Result (Gate 1)"
            text={post.result_json_v1}
            fallback="Not yet AI-processed"
          />
          <ReasoningPanel
            label="Gate 1 reasoning"
            promptVersion={post.gate1_prompt_version}
            reasoning={post.gate1_reasoning}
          />

          <TextBlock
            label="AI Result (Extraction)"
            text={post.extraction_result_json}
            fallback="Not yet extracted"
          />
          <ReasoningPanel
            label="Extraction reasoning"
            promptVersion={post.extraction_prompt_version}
            reasoning={post.extraction_reasoning}
          />
        </>
      )}

      {!post && !error && (
        <div className="text-foreground/60">Enter a row ID to search.</div>
      )}
    </div>
  );
}
