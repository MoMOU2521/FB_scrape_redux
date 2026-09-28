import type { ReactNode } from "react";
import { Card, CardContent } from "@/components/ui/card";

interface MetaPost {
  id: number;
  author: string;
  group_name: string;
  post_id: string;
  scraped_at: string;
  post_url: string;
}

interface PostMetaProps {
  post: MetaPost;
  countLabel?: string;
  count?: number;
  children?: ReactNode;
}

export function PostMeta({ post, countLabel, count, children }: PostMetaProps) {
  return (
    <Card>
      <CardContent className="flex flex-col gap-1 text-sm">
        <span>SQLite Row ID: {post.id}</span>
        <span className="font-base text-base">{post.author}</span>
        <span>Group: {post.group_name}</span>
        <span>Post ID: {post.post_id}</span>
        <span>Scraped at: {post.scraped_at}</span>
        <span>
          Original:{" "}
          <a href={post.post_url} target="_blank" rel="noreferrer">
            {post.post_url}
          </a>
        </span>
        {countLabel && (
          <span>
            {countLabel}: {count}
          </span>
        )}
        {children}
      </CardContent>
    </Card>
  );
}
