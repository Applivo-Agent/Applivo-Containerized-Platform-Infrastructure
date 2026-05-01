import { Sidebar } from "@/components/sidebar";
import { AuthGuard } from "@/components/auth-guard";
import { PageTransition } from "@/components/page-transition";
import { NavBar } from "@/components/NavBar";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <div className="flex min-h-screen bg-[#050505]">
        <Sidebar />
        <NavBar />
        <main className="dashboard-typography flex-1 ml-[17rem] min-h-screen overflow-x-hidden pt-[88px] px-8 bg-[#050505]">
          <div className="max-w-7xl mx-auto w-full">
            <PageTransition>
              {children}
            </PageTransition>
          </div>
        </main>
      </div>
    </AuthGuard>
  );
}
