import { cn } from "@/lib/utils"
import {
  LayoutDashboard,
  FileText,
  GitBranch,
  ChevronLeft,
  ChevronRight,
} from "lucide-react"
import { useState } from "react"

export type Page = "dashboard" | "prompts" | "workflows"

interface NavBarProps {
  activePage: Page
  onPageChange: (page: Page) => void
}

const pages: { key: Page; label: string; icon: typeof LayoutDashboard; description: string }[] = [
  { key: "dashboard", label: "Dashboard", icon: LayoutDashboard, description: "Overview & query" },
  { key: "prompts", label: "Prompts", icon: FileText, description: "Manage templates" },
  { key: "workflows", label: "Workflows", icon: GitBranch, description: "Build DAGs" },
]

export function NavBar({ activePage, onPageChange }: NavBarProps) {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <aside
      className={cn(
        "flex flex-col h-full border-r border-white/[0.06] bg-card/40 backdrop-blur-xl transition-all duration-300 shrink-0",
        collapsed ? "w-[68px]" : "w-[var(--sidebar-width)]"
      )}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 h-16 border-b border-white/[0.06]">
        <img src="/icon.png" alt="Vectraxis" className="h-8 w-8 shrink-0" />
        {!collapsed && (
          <div className="overflow-hidden">
            <h1 className="text-base font-bold gradient-text leading-tight">
              Vectraxis
            </h1>
            <p className="text-[10px] text-muted-foreground leading-tight">
              AI Pipeline Studio
            </p>
          </div>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 p-3 space-y-1">
        {pages.map((p) => {
          const Icon = p.icon
          const isActive = activePage === p.key
          return (
            <button
              key={p.key}
              onClick={() => onPageChange(p.key)}
              className={cn(
                "nav-item w-full",
                isActive ? "nav-item-active" : "nav-item-inactive"
              )}
              title={collapsed ? p.label : undefined}
            >
              <Icon className={cn("h-[18px] w-[18px] shrink-0", isActive && "text-primary")} />
              {!collapsed && (
                <div className="overflow-hidden text-left">
                  <div className="truncate">{p.label}</div>
                  <div className="text-[10px] text-muted-foreground truncate leading-tight">
                    {p.description}
                  </div>
                </div>
              )}
            </button>
          )
        })}
      </nav>

      {/* Collapse toggle */}
      <div className="p-3 border-t border-white/[0.06]">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="nav-item nav-item-inactive w-full justify-center"
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <>
              <ChevronLeft className="h-4 w-4" />
              <span className="text-xs">Collapse</span>
            </>
          )}
        </button>
      </div>
    </aside>
  )
}
