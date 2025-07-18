import { GrantList } from "@/components/grants/GrantList";
import { GrantForm } from "@/components/grants/GrantForm";
import { ScraperManager } from "@/components/grants/ScraperManager";

export default function GrantsPage() {
  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Grants</h1>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <GrantList />
        </div>
        <div className="space-y-6">
          <GrantForm />
          <ScraperManager />
        </div>
      </div>
    </div>
  );
} 