import { Card, CardContent } from "@/components/ui/card";
import type { Post } from "@/api/posts";

export function PostMeta({ post }: { post: Post }) {
  return (
    <Card>
      <CardContent className="flex flex-col gap-1 text-sm">
        <span className="font-base text-base">{post.author}</span>
        <span>Group: {post.group_name}</span>
        <span>Post ID: {post.post_id}</span>
        <span>Row ID: {post.id}</span>
        <span>Unprocessed by this author: {post.unprocessed_count}</span>
      </CardContent>
    </Card>
  );
}
