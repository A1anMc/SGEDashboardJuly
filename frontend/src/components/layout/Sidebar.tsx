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
        <Link href="/" className="flex items-center space-x-3">
          <img src="/icon.svg" alt="NavImpact" className="h-8 w-8" />
          <span className="text-xl font-bold text-white">
            <span className="text-white">Nav</span>
            <span className="text-energy-coral">Impact</span>
          </span>
        </Link>
      </div>
      
      <nav className="flex-1 space-y-1 px-2 py-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`group flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-colors duration-150 ${
                isActive
                  ? 'bg-white/20 text-white'
                  : 'text-white/80 hover:bg-white/10 hover:text-white'
              }`}
            >
              <item.icon
                className={`mr-3 h-5 w-5 flex-shrink-0 transition-colors duration-150 ${
                  isActive ? 'text-white' : 'text-white/60 group-hover:text-white'
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