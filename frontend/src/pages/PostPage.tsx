import { useEffect, useState } from "react";
import * as api from "@/api/posts";
import { usePost, usePostActions } from "@/hooks/usePosts";
import { PostMeta } from "@/components/posts/PostMeta";
import { PostNav } from "@/components/posts/PostNav";
import { PostStatusToggles } from "@/components/posts/PostStatusToggles";
import { ReasoningPanel } from "@/components/posts/ReasoningPanel";
import { TextBlock } from "@/components/posts/TextBlock";
import { AdminPanel } from "@/components/posts/AdminPanel";
import { EnterIntoDb } from "@/components/posts/EnterIntoDb";
import { Button } from "@/components/ui/button";

export function PostPage() {
  const [rowId, setRowId] = useState<number | null>(null);
  const [initLoading, setInitLoading] = useState(true);

  useEffect(() => {
    api.getNextUnprocessed().then(({ row_id }) => {
      setRowId(row_id);
      setInitLoading(false);
    });
  }, []);

  const { data, loading, refetch } = usePost(rowId);
  const { markProcessed, toggleSelected, remove } = usePostActions(
    rowId,
    refetch,
  );

  async function advance() {
    const { row_id } = await api.getNextUnprocessed();
    setRowId(row_id);
  }

  if (initLoading || loading) return <div className="p-6">Loading…</div>;
  if (rowId == null) return <div className="p-6">All posts processed.</div>;
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
        onProcessedChange={(c) => markProcessed(c ? 1 : 0)}
        onSelectedChange={(c) => toggleSelected(c ? 1 : 0)}
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

      <EnterIntoDb rowId={post.id} onDone={advance} />

      <AdminPanel author={post.author} onBlacklisted={advance} />

      <Button
        variant="neutral"
        onClick={async () => {
          if (await remove()) await advance();
        }}
      >
        Delete this post
      </Button>
    </div>
  );
}
