// frontend/src/pages/ProcessedPage.tsx
import { useEffect, useState } from "react";
import * as processedApi from "@/api/processed";
import * as postsApi from "@/api/posts";
import {
  useProcessedPost,
  useAuthorProcessedPosts,
} from "@/hooks/useProcessedPosts";
import { PostMeta } from "@/components/posts/PostMeta";
import { PostNav } from "@/components/posts/PostNav";
import { PostStatusToggles } from "@/components/posts/PostStatusToggles";
import { ReasoningPanel } from "@/components/posts/ReasoningPanel";
import { TextBlock } from "@/components/posts/TextBlock";
import { Button } from "@/components/ui/button";

export function ProcessedPage() {
  const [authorMode, setAuthorMode] = useState(false);
  const [rowId, setRowId] = useState<number | null>(null);
  const [initLoading, setInitLoading] = useState(true);

  useEffect(() => {
    processedApi.getNextProcessed().then(({ row_id }) => {
      setRowId(row_id);
      setInitLoading(false);
    });
  }, []);

  const globalQ = useProcessedPost(authorMode ? null : rowId);
  const authorQ = useAuthorProcessedPosts(authorMode ? rowId : null);
  const active = authorMode ? authorQ : globalQ;

  const post = active.data?.post ?? null;
  const nav = active.data?.nav ?? null;

  async function goFirst() {
    const { row_id } = await processedApi.getNextProcessed();
    setRowId(row_id);
  }

  async function exitAuthorMode() {
    setAuthorMode(false);
    await goFirst();
  }

  if (initLoading || active.loading) return <div className="p-6">Loading…</div>;

  if (!authorMode && rowId == null)
    return <div className="p-6">No processed posts.</div>;

  if (!post || !nav) {
    return (
      <div className="mx-auto flex max-w-2xl flex-col gap-4 p-6">
        <div>
          {authorMode
            ? "No more processed posts by this author."
            : "Not found."}
        </div>
        {authorMode && (
          <Button variant="neutral" size="sm" onClick={exitAuthorMode}>
            Back to all processed posts
          </Button>
        )}
      </div>
    );
  }

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-4 p-6">
      {authorMode && (
        <div className="flex items-center gap-3">
          <span className="text-sm">
            Processed posts by <strong>{post.author}</strong>
          </span>
          <Button variant="neutral" size="xs" onClick={exitAuthorMode}>
            Back to all processed posts
          </Button>
        </div>
      )}

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
          if (c) {
            active.refetch();
          } else if (authorMode) {
            active.refetch();
          } else {
            await goFirst();
          }
        }}
        onSelectedChange={async (c) => {
          await postsApi.toggleSelected(post.id, c ? 1 : 0);
          active.refetch();
        }}
      />

      <PostMeta post={post} />

      {!authorMode && (
        <Button variant="neutral" size="sm" onClick={() => setAuthorMode(true)}>
          View all processed posts by this author
        </Button>
      )}

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
          if (!ok) return;
          if (authorMode) active.refetch();
          else await goFirst();
        }}
      >
        Delete this post
      </Button>
    </div>
  );
}
