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
  const dashboardItems = [
    {
      title: 'Grants',
      description: 'Browse and manage funding opportunities',
      icon: DocumentMagnifyingGlassIcon,
      href: '/grants',
      color: 'bg-blue-500',
    },
    {
      title: 'Projects',
      description: 'Track your project portfolio',
      icon: FolderIcon,
      href: '/projects',
      color: 'bg-green-500',
    },
    {
      title: 'Tasks',
      description: 'Manage project tasks and workflows',
      icon: ClipboardDocumentListIcon,
      href: '/tasks',
      color: 'bg-purple-500',
    },
    {
      title: 'Impact',
      description: 'View impact metrics and analytics',
      icon: ChartBarIcon,
      href: '/impact',
      color: 'bg-orange-500',
    },
    {
      title: 'Media',
      description: 'Manage media assets and content',
      icon: PhotoIcon,
      href: '/media',
      color: 'bg-pink-500',
    },
    {
      title: 'Time Logs',
      description: 'Track time spent on projects',
      icon: ClockIcon,
      href: '/time-logs',
      color: 'bg-indigo-500',
    },
  ];

  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome to NavImpact</h1>
        <p className="text-gray-600">Your comprehensive grant management and project tracking platform</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {dashboardItems.map((item) => (
          <Card key={item.title} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-lg ${item.color}`}>
                  <item.icon className="h-6 w-6 text-white" />
                </div>
                <div>
                  <CardTitle className="text-lg">{item.title}</CardTitle>
                  <CardDescription>{item.description}</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Link href={item.href}>
                <Button className="w-full" variant="outline">
                  View {item.title}
                </Button>
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest updates from your projects</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center space-x-3 text-sm text-gray-600">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span>No recent activity</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Stats</CardTitle>
            <CardDescription>Overview of your grant portfolio</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">0</div>
                <div className="text-sm text-gray-600">Active Grants</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">0</div>
                <div className="text-sm text-gray-600">Projects</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 