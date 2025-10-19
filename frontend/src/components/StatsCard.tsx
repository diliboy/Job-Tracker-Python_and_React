import type { LucideIcon } from 'lucide-react';

interface StatsCardProps {
  title: string;
  value: number;
  icon: LucideIcon;
  color: 'blue' | 'yellow' | 'green' | 'red' | 'gray';
}

const colorClasses = {
  blue: 'bg-blue-50 text-blue-600',
  yellow: 'bg-yellow-50 text-yellow-600',
  green: 'bg-green-50 text-green-600',
  red: 'bg-red-50 text-red-600',
  gray: 'bg-gray-50 text-gray-600',
};

const iconColorClasses = {
  blue: 'text-blue-600',
  yellow: 'text-yellow-600',
  green: 'text-green-600',
  red: 'text-red-600',
  gray: 'text-gray-600',
};

export default function StatsCard({ title, value, icon: Icon, color }: StatsCardProps) {
  return (
    <div className={`card ${colorClasses[color]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium opacity-80">{title}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>
        </div>
        <Icon className={`w-12 h-12 ${iconColorClasses[color]} opacity-50`} />
      </div>
    </div>
  );
}