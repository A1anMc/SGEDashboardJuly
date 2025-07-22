import { FC } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  HomeIcon,
  DocumentMagnifyingGlassIcon,
  ClipboardDocumentListIcon,
  ChartBarIcon,
  PhotoIcon,
  ClockIcon,
  FolderIcon,
  CogIcon,
} from '@heroicons/react/24/outline';
import Logo from '@/components/ui/logo';

// Custom NavImpact dashboard navigation, built by Alan – not boilerplate
const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Projects', href: '/projects', icon: FolderIcon },
  { name: 'Grants', href: '/grants', icon: DocumentMagnifyingGlassIcon },
  { name: 'Tasks', href: '/tasks', icon: ClipboardDocumentListIcon },
  { name: 'Impact', href: '/impact', icon: ChartBarIcon },
  { name: 'Media', href: '/media', icon: PhotoIcon },
  { name: 'Time Logs', href: '/time-logs', icon: ClockIcon },
];

const Sidebar: FC = () => {
  const pathname = usePathname();

  return (
    <div className="flex h-full w-64 flex-col bg-impact-teal">
      <div className="flex h-16 items-center px-4">
        <Logo variant="full" size="md" href="/" className="text-white" />
      </div>
      
      <nav className="flex-1 space-y-1 px-2 py-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`group flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-all duration-300 ${
                isActive
                  ? 'bg-gradient-to-r from-white/20 to-white/10 text-white shadow-lg'
                  : 'text-white/80 hover:bg-gradient-to-r hover:from-white/10 hover:to-white/5 hover:text-white hover:shadow-md'
              }`}
            >
              <item.icon
                className={`mr-3 h-5 w-5 flex-shrink-0 transition-all duration-300 ${
                  isActive ? 'text-white scale-110' : 'text-white/60 group-hover:text-white group-hover:scale-105'
                }`}
                aria-hidden="true"
              />
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-white/20 p-4">
        <Link
          href="/settings"
          className={`group flex items-center rounded-lg px-3 py-2 text-sm font-medium text-white/80 hover:bg-white/10 hover:text-white ${
            pathname === '/settings' ? 'bg-white/20 text-white' : ''
          }`}
        >
          <CogIcon className="mr-3 h-5 w-5 text-white/60 group-hover:text-white" />
          Settings
        </Link>
      </div>
    </div>
  );
};

export default Sidebar; 