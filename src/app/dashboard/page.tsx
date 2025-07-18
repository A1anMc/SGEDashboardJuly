import { GrantDashboard } from "@/components/grants/GrantDashboard";

export default function DashboardPage() {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>
      <GrantDashboard />
    </div>
  );
} 