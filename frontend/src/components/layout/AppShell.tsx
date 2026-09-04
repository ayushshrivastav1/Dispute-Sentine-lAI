/** Authenticated console shell: sleek sidebar + top header, responsive. */
import { Link, useNavigate, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  ListChecks,
  LogOut,
  Menu,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { useState, type ReactNode } from "react";

import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { useAuth } from "@/hooks/useAuth";
import { clearSession } from "@/lib/auth-storage";
import { cn } from "@/lib/utils";

const NAV = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/queue", label: "Review Queue", icon: ListChecks },
] as const;

function NavLinks({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = useLocation().pathname;
  return (
    <nav className="flex flex-col gap-1">
      {NAV.map((item) => {
        const active = pathname === item.to || pathname.startsWith(`${item.to}/`);
        return (
          <Link
            key={item.to}
            to={item.to}
            onClick={onNavigate}
            className={cn(
              "interactive flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground",
              "hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
              active && "bg-sidebar-accent text-sidebar-accent-foreground shadow-sm",
            )}
          >
            <item.icon className="size-4" />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}

function Brand() {
  return (
    <Link to="/" className="flex items-center gap-2.5">
      <span className="flex size-8 items-center justify-center rounded-lg bg-primary/15 text-primary ring-1 ring-primary/30">
        <ShieldCheck className="size-4" />
      </span>
      <span className="text-sm font-semibold tracking-tight">DisputeSentinel</span>
    </Link>
  );
}

export function AppShell({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children: ReactNode;
}) {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  const signOut = () => {
    clearSession();
    navigate("/login");
  };

  return (
    <div className="grid-backdrop min-h-screen bg-background text-foreground lg:grid lg:grid-cols-[248px_1fr]">
      {/* Desktop sidebar */}
      <aside className="hidden border-r border-sidebar-border bg-sidebar/70 p-4 backdrop-blur-xl lg:flex lg:flex-col">
        <div className="px-1 pb-6">
          <Brand />
        </div>
        <NavLinks />
        <div className="mt-auto glass rounded-xl p-3">
          <p className="flex items-center gap-1.5 text-xs font-medium text-primary">
            <Sparkles className="size-3.5" /> AI Autopilot
          </p>
          <p className="mt-1 text-xs text-muted-foreground">
            Evidence gathering runs continuously on new chargebacks.
          </p>
        </div>
      </aside>

      <div className="flex min-h-screen flex-col">
        <header className="sticky top-0 z-30 flex items-center gap-3 border-b border-border/70 bg-background/70 px-4 py-3 backdrop-blur-xl md:px-6">
          <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="lg:hidden" aria-label="Open menu">
                <Menu className="size-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-64 bg-sidebar p-4">
              <SheetTitle className="sr-only">Navigation</SheetTitle>
              <div className="pb-6">
                <Brand />
              </div>
              <NavLinks onNavigate={() => setOpen(false)} />
            </SheetContent>
          </Sheet>

          <div className="min-w-0 flex-1">
            <h1 className="truncate text-base font-semibold tracking-tight md:text-lg">{title}</h1>
            {description ? (
              <p className="hidden truncate text-xs text-muted-foreground md:block">
                {description}
              </p>
            ) : null}
          </div>

          <div className="hidden text-right sm:block">
            <p className="text-xs font-medium">{user?.name ?? "Analyst"}</p>
            <p className="text-[11px] text-muted-foreground">
              {user?.organization ?? "DisputeSentinel"}
            </p>
          </div>
          <Button variant="outline" size="sm" onClick={signOut} className="interactive">
            <LogOut className="size-4" />
            <span className="hidden sm:inline">Sign out</span>
          </Button>
        </header>

        <main className="flex-1 px-4 py-6 md:px-6 md:py-8">{children}</main>
      </div>
    </div>
  );
}
