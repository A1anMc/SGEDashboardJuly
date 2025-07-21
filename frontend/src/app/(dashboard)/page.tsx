'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { 
  DocumentMagnifyingGlassIcon, 
  FolderIcon, 
  ClipboardDocumentListIcon,
  ChartBarIcon,
  PhotoIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

export default function DashboardPage() {
  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-4">NavImpact Dashboard</h1>
      <p className="text-gray-600 mb-4">Welcome to NavImpact - your grant management platform</p>
      
      <div className="bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded">
        <p>✅ Frontend is working!</p>
        <p>API Status: <a href="https://navimpact-api.onrender.com/api/v1/grants/" target="_blank" className="underline">Check API</a></p>
      </div>
      
      <div className="mt-6">
        <h2 className="text-xl font-semibold mb-3">Quick Links:</h2>
        <ul className="space-y-2">
          <li><a href="/grants" className="text-blue-600 hover:underline">Grants</a></li>
          <li><a href="/projects" className="text-blue-600 hover:underline">Projects</a></li>
          <li><a href="/tasks" className="text-blue-600 hover:underline">Tasks</a></li>
        </ul>
      </div>
    </div>
  );
} 