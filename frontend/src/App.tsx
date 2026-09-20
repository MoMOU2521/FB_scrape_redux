// frontend/src/App.tsx
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  NavLink,
  useParams,
  useNavigate,
} from "react-router-dom";
import { PostPage } from "@/pages/PostPage";
import { ProcessedPage } from "@/pages/ProcessedPage";
import { BlacklistPage } from "@/pages/BlacklistPage";
import { FiltersPage } from "@/pages/FiltersPage";
import { ReviewPage } from "@/pages/ReviewPage";
import { LookupPage } from "@/pages/LookupPage";
import { ReviewBuildingPage } from "@/pages/ReviewBuildingPage";
import { StatsPage } from "@/pages/StatsPage";
import { AuthorsPage } from "@/pages/AuthorsPage";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { to: "/unprocessed", label: "Unprocessed" },
  { to: "/processed", label: "Processed" },
  { to: "/lookup", label: "Lookup" },
  { to: "/review", label: "Review" },
  { to: "/review-building", label: "Building Review" },
  { to: "/stats", label: "Stats" },
  { to: "/authors", label: "Authors" },
  { to: "/blacklist", label: "Blacklist" },
  { to: "/filters", label: "Filters" },
];

function Nav() {
  return (
    <div className="mx-auto flex max-w-2xl flex-wrap gap-2 pt-6">
      {NAV_ITEMS.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) =>
            cn(
              buttonVariants({
                variant: isActive ? "default" : "neutral",
                size: "sm",
              }),
            )
          }
        >
          {item.label}
        </NavLink>
      ))}
    </div>
  );
}

function UnprocessedRoute() {
  const { rowId } = useParams<{ rowId: string }>();
  return (
    <PostPage
      key={rowId ?? "root"}
      initialAuthorRowId={rowId ? Number(rowId) : null}
    />
  );
}

function StatsRoute() {
  const navigate = useNavigate();
  return (
    <StatsPage
      onViewAuthorPosts={(rowId) => navigate(`/unprocessed/author/${rowId}`)}
    />
  );
}

function AuthorsRoute() {
  const navigate = useNavigate();
  return (
    <AuthorsPage
      onViewAuthorPosts={(rowId) => navigate(`/unprocessed/author/${rowId}`)}
    />
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="flex flex-col gap-4">
        <Nav />
        <Routes>
          <Route path="/" element={<Navigate to="/unprocessed" replace />} />
          <Route path="/unprocessed" element={<UnprocessedRoute />} />
          <Route
            path="/unprocessed/author/:rowId"
            element={<UnprocessedRoute />}
          />
          <Route path="/processed" element={<ProcessedPage />} />
          <Route path="/lookup" element={<LookupPage />} />
          <Route path="/review" element={<ReviewPage />} />
          <Route path="/review-building" element={<ReviewBuildingPage />} />
          <Route path="/stats" element={<StatsRoute />} />
          <Route path="/authors" element={<AuthorsRoute />} />
          <Route path="/blacklist" element={<BlacklistPage />} />
          <Route path="/filters" element={<FiltersPage />} />
          <Route path="*" element={<Navigate to="/unprocessed" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
