import { Card, CardContent } from "@/components/ui/card";
import type { Post } from "@/api/posts";

// after
interface PostMetaProps {
  post: Post;
  countLabel?: string;
  count?: number;
}

export function PostMeta({ post, countLabel, count }: PostMetaProps) {
  return (
    <Card>
      <CardContent className="flex flex-col gap-1 text-sm">
        <span className="font-base text-base">{post.author}</span>
        <span>Group: {post.group_name}</span>
        <span>Post ID: {post.post_id}</span>
        <span>Row ID: {post.id}</span>
        {countLabel && (
          <span>
            {countLabel}: {count}
          </span>
        )}
      </CardContent>
    </Card>
  );
}
