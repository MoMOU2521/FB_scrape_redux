// frontend/src/pages/ReviewPage.tsx
import { useEffect, useState } from "react";
import * as api from "@/api/review";
import { useReview } from "@/hooks/useReview";
import { PostNav } from "@/components/posts/PostNav";
import { TextBlock } from "@/components/posts/TextBlock";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export function ReviewPage() {
  const [reviewId, setReviewId] = useState<number | null>(null);
  const [initLoading, setInitLoading] = useState(true);

  useEffect(() => {
    api.getNextReview().then(({ row_id }) => {
      setReviewId(row_id);
      setInitLoading(false);
    });
  }, []);

  const { data, loading } = useReview(reviewId);

  async function advance() {
    const { row_id } = await api.getNextReview();
    setReviewId(row_id);
  }

  if (initLoading || loading) return <div className="p-6">Loading…</div>;
  if (reviewId == null) return <div className="p-6">No pending reviews.</div>;
  if (!data) return <div className="p-6">Not found.</div>;

  const { row, nav } = data;

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-4 p-6">
      <PostNav
        nav={nav}
        onPrev={() => nav.prev_id != null && setReviewId(nav.prev_id)}
        onNext={() => nav.next_id != null && setReviewId(nav.next_id)}
      />

      <Card>
        <CardContent className="flex flex-col gap-1 text-sm">
          <span className="font-base text-base">{row.author}</span>
          <span>
            Post URL:{" "}
            <a href={row.post_url} target="_blank" rel="noreferrer">
              {row.post_url}
            </a>
          </span>
          <span>Scraped at: {row.scraped_at}</span>
          <span>
            Candidate duplicate property ID:{" "}
            {row.candidate_property_id ?? "None recorded"}
          </span>
        </CardContent>
      </Card>

      <TextBlock label="Post text" text={row.text} />
      <TextBlock label="Extraction JSON" text={row.extraction_result_json} />

      <div className="flex gap-2">
        <Button
          onClick={async () => {
            await api.approveReview(row.review_id);
            await advance();
          }}
        >
          Approve (insert)
        </Button>
        <Button
          variant="neutral"
          onClick={async () => {
            await api.rejectReview(row.review_id);
            await advance();
          }}
        >
          Reject (discard)
        </Button>
        <Button
          variant="neutral"
          onClick={async () => {
            await api.dismissReview(row.review_id);
            await advance();
          }}
        >
          Dismiss (leave as-is)
        </Button>
      </div>
    </div>
  );
}
