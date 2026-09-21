// frontend/src/pages/ReviewBuildingPage.tsx
import { useEffect, useState } from "react";
import * as api from "@/api/reviewBuilding";
import * as postsApi from "@/api/posts";
import { useReviewBuilding } from "@/hooks/useReviewBuilding";
import { PostMeta } from "@/components/posts/PostMeta";
import { PostNav } from "@/components/posts/PostNav";
import { PostStatusToggles } from "@/components/posts/PostStatusToggles";
import { TextBlock } from "@/components/posts/TextBlock";
import { ReasoningPanel } from "@/components/posts/ReasoningPanel";
import { BuildingAliasPanel } from "@/components/posts/BuildingAliasPanel";
import { Button } from "@/components/ui/button";

export function ReviewBuildingPage() {
  const [postId, setPostId] = useState<number | null>(null);
  const [initLoading, setInitLoading] = useState(true);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.getNextBuildingReview().then(({ row_id }) => {
      setPostId(row_id);
      setInitLoading(false);
    });
  }, []);

  const { data, loading, refetch } = useReviewBuilding(postId);

  async function advance() {
    setFeedback(null);
    const { row_id } = await api.getNextBuildingReview();
    setPostId(row_id);
  }

  async function enterIntoDb() {
    if (postId == null) return;
    setBusy(true);
    setFeedback(null);
    try {
      const res = await api.enterBuilding(postId);
      if ("discarded" in res) {
        setFeedback("Skipped: exact duplicate exists.");
      } else if ("sent_to_review" in res) {
        setFeedback(
          `Sent to review (candidate ID: ${res.candidate_property_id})`,
        );
      } else {
        setFeedback(`Entered! Property ID: ${res.property_id}`);
      }
      await new Promise((r) => setTimeout(r, 1000));
      await advance();
    } catch (e) {
      setFeedback((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  if (initLoading || loading) return <div className="p-6">Loading…</div>;
  if (postId == null)
    return <div className="p-6">No pending building reviews.</div>;
  if (!data) return <div className="p-6">Not found.</div>;

  const { post, nav } = data;

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-4 p-6">
      <PostNav
        nav={nav}
        onPrev={() => nav.prev_id != null && setPostId(nav.prev_id)}
        onNext={() => nav.next_id != null && setPostId(nav.next_id)}
      />

      <PostStatusToggles
        processed={!!post.processed}
        selected={!!post.selected}
        onProcessedChange={async (c) => {
          await postsApi.markProcessed(post.id, c ? 1 : 0);
          await advance();
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

      <div className="flex items-center gap-3">
        <Button onClick={enterIntoDb} disabled={busy}>
          Enter into DB
        </Button>
        {feedback && <span className="text-sm">{feedback}</span>}
      </div>

      <BuildingAliasPanel />

      <Button
        variant="neutral"
        onClick={async () => {
          await api.dismissBuildingReview(post.id);
          await advance();
        }}
      >
        Dismiss from Building Review
      </Button>

      <Button
        variant="neutral"
        onClick={async () => {
          if (!confirm("Delete this post? This cannot be undone.")) return;
          const ok = (await postsApi.deletePost(post.id)).ok;
          if (ok) await advance();
        }}
      >
        Delete this post
      </Button>
    </div>
  );
}
