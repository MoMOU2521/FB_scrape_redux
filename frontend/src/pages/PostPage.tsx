// frontend/src/pages/PostPage.tsx
import { useEffect, useState } from "react";
import * as api from "@/api/posts";
import { usePost, useAuthorPosts, usePostActions } from "@/hooks/usePosts";
import { PostMeta } from "@/components/posts/PostMeta";
import { PostNav } from "@/components/posts/PostNav";
import { PostStatusToggles } from "@/components/posts/PostStatusToggles";
import { ReasoningPanel } from "@/components/posts/ReasoningPanel";
import { TextBlock } from "@/components/posts/TextBlock";
import { AdminPanel } from "@/components/posts/AdminPanel";
import { EnterIntoDb } from "@/components/posts/EnterIntoDb";
import { Button } from "@/components/ui/button";
import { BuildingAliasPanel } from "@/components/posts/BuildingAliasPanel";

interface PostPageProps {
  initialAuthorRowId?: number | null;
}

export function PostPage({ initialAuthorRowId }: PostPageProps) {
  const [authorMode, setAuthorMode] = useState(initialAuthorRowId != null);
  const [rowId, setRowId] = useState<number | null>(initialAuthorRowId ?? null);
  const [initLoading, setInitLoading] = useState(initialAuthorRowId == null);

  useEffect(() => {
    if (initialAuthorRowId != null) return;
    api.getNextUnprocessed().then(({ row_id }) => {
      setRowId(row_id);
      setInitLoading(false);
    });
  }, [initialAuthorRowId]);

  const globalQ = usePost(authorMode ? null : rowId);
  const authorQ = useAuthorPosts(authorMode ? rowId : null);
  const active = authorMode ? authorQ : globalQ;

  const post = active.data?.post ?? null;
  const nav = active.data?.nav ?? null;

  const { markProcessed, toggleSelected, remove } = usePostActions(
    post?.id ?? null,
    active.refetch,
  );

  async function advance() {
    if (authorMode) {
      // author endpoint resolves to the first remaining unprocessed post
      authorQ.refetch();
      return;
    }
    const { row_id } = await api.getNextUnprocessed();
    setRowId(row_id);
  }

  async function exitAuthorMode() {
    setAuthorMode(false);
    const { row_id } = await api.getNextUnprocessed();
    setRowId(row_id);
  }

  if (initLoading || active.loading) return <div className="p-6">Loading…</div>;

  if (!authorMode && rowId == null)
    return <div className="p-6">All posts processed.</div>;

  if (!post || !nav) {
    return (
      <div className="mx-auto flex max-w-2xl flex-col gap-4 p-6">
        <div>
          {authorMode
            ? "No more unprocessed posts by this author."
            : "Not found."}
        </div>
        {authorMode && (
          <Button variant="neutral" size="sm" onClick={exitAuthorMode}>
            Back to all posts
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
            Unprocessed posts by <strong>{post.author}</strong>
          </span>
          <Button variant="neutral" size="xs" onClick={exitAuthorMode}>
            Back to all posts
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
          await markProcessed(c ? 1 : 0);
          await advance();
        }}
        onSelectedChange={(c) => toggleSelected(c ? 1 : 0)}
      />

      <PostMeta post={post} />

      {!authorMode && (
        <Button variant="neutral" size="sm" onClick={() => setAuthorMode(true)}>
          Process all unprocessed posts by this author
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

      <EnterIntoDb rowId={post.id} onDone={advance} />

      <BuildingAliasPanel />

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
