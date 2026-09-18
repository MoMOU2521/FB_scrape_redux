import { ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { NavContext } from "@/api/posts"

interface PostNavProps {
  nav: NavContext
  onPrev: () => void
  onNext: () => void
}

export function PostNav({ nav, onPrev, onNext }: PostNavProps) {
  return (
    <div className="flex items-center gap-3">
      <Button
        variant="neutral"
        size="sm"
        onClick={onPrev}
        disabled={nav.prev_id == null}
      >
        <ChevronLeft />
        Previous
      </Button>
      <Button
        variant="neutral"
        size="sm"
        onClick={onNext}
        disabled={nav.next_id == null}
      >
        Next
        <ChevronRight />
      </Button>
      <span className="text-sm text-muted-foreground">
        {nav.current} / {nav.total}
      </span>
    </div>
  )
}