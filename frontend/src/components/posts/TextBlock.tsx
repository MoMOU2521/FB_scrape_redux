import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

interface TextBlockProps {
  label: string;
  text: string | null;
  fallback?: string;
}

export function TextBlock({ label, text, fallback = "" }: TextBlockProps) {
  return (
    <Card className="gap-2">
      <CardHeader>
        <CardTitle>{label}</CardTitle>
      </CardHeader>
      <CardContent className="whitespace-pre-wrap text-sm">
        {text || fallback}
      </CardContent>
    </Card>
  );
}
