// frontend/src/pages/ProcessedPage.tsx
import { useEffect, useState } from "react";
import * as processedApi from "@/api/processed";
import * as postsApi from "@/api/posts";
import { useProcessedPost } from "@/hooks/useProcessedPosts";
import { PostMeta } from "@/components/posts/PostMeta";
import { PostNav } from "@/components/posts/PostNav";
import { PostStatusToggles } from "@/components/posts/PostStatusToggles";
import { ReasoningPanel } from "@/components/posts/ReasoningPanel";
import { TextBlock } from "@/components/posts/TextBlock";
import { Button } from "@/components/ui/button";

export function ProcessedPage() {
  const [rowId, setRowId] = useState<number | null>(null);
  const [initLoading, setInitLoading] = useState(true);

  useEffect(() => {
    processedApi.getNextProcessed().then(({ row_id }) => {
      setRowId(row_id);
      setInitLoading(false);
    });
  }, []);

  const { data, loading, refetch } = useProcessedPost(rowId);

  if (initLoading || loading) return <div className="p-6">Loading…</div>;
  if (rowId == null) return <div className="p-6">No processed posts.</div>;
  if (!data) return <div className="p-6">Not found.</div>;

  const { post, nav } = data;

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-4 p-6">
      <PostNav
        nav={nav}
        onPrev={() => nav.prev_id != null && setRowId(nav.prev_id)}
        onNext={() => nav.next_id != null && setRowId(nav.next_id)}
      />

      <PostStatusToggles
        processed={!!post.processed}
        selected={!!post.selected}
        onProcessedChange={async (c) => {
          await postsApi.markProcessed(post.id, c ? 1 : 0);
          refetch();
        }}
        onSelectedChange={async (c) => {
          await postsApi.toggleSelected(post.id, c ? 1 : 0);
          refetch();
        }}
      />

      <PostMeta post={post} />

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

      <Button
        variant="neutral"
        onClick={async () => {
          const ok = (await postsApi.deletePost(post.id)).ok;
          if (ok) {
            const { row_id } = await processedApi.getNextProcessed();
            setRowId(row_id);
          }
        }}
      >
        Delete this post
      </Button>
    </div>
  );
}
