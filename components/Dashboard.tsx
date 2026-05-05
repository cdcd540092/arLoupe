import React from 'react';
import { Users, Shield, AlertTriangle, CheckCircle, Activity, Server } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { useLanguage } from '../contexts/LanguageContext';
import { useTheme } from '../contexts/ThemeContext';

const data = [
  { name: 'Mon', apiCalls: 4000, errors: 240 },
  { name: 'Tue', apiCalls: 3000, errors: 139 },
  { name: 'Wed', apiCalls: 2000, errors: 980 },
  { name: 'Thu', apiCalls: 2780, errors: 390 },
  { name: 'Fri', apiCalls: 1890, errors: 480 },
  { name: 'Sat', apiCalls: 2390, errors: 380 },
  { name: 'Sun', apiCalls: 3490, errors: 430 },
];

const Dashboard: React.FC = () => {
  const { t } = useLanguage();
  const { theme } = useTheme();

  // Chart config based on theme
  const chartTextColor = theme === 'dark' ? '#94a3b8' : '#64748b';
  const chartGridColor = theme === 'dark' ? '#334155' : '#e2e8f0';
  const tooltipBg = theme === 'dark' ? '#1e293b' : '#fff';
  const tooltipBorder = theme === 'dark' ? '#334155' : '#e2e8f0';

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-800 dark:text-white">{t.dashboard.title}</h2>
        <p className="text-slate-500 dark:text-slate-400 mt-1">{t.dashboard.subtitle}</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-slate-100 dark:border-slate-700 transition-colors">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{t.dashboard.totalApiCalls}</p>
              <p className="text-2xl font-bold text-slate-800 dark:text-white mt-1">1.2M</p>
            </div>
            <div className="p-3 bg-blue-50 dark:bg-blue-900/30 rounded-lg text-blue-600 dark:text-blue-400">
              <Activity size={24} />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-green-500 font-medium">+12.5%</span>
            <span className="text-slate-400 dark:text-slate-500 ml-2">{t.dashboard.vsLastWeek}</span>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-slate-100 dark:border-slate-700 transition-colors">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{t.dashboard.activeUsers}</p>
              <p className="text-2xl font-bold text-slate-800 dark:text-white mt-1">8,549</p>
            </div>
            <div className="p-3 bg-indigo-50 dark:bg-indigo-900/30 rounded-lg text-indigo-600 dark:text-indigo-400">
              <Users size={24} />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-green-500 font-medium">+4.3%</span>
            <span className="text-slate-400 dark:text-slate-500 ml-2">{t.dashboard.vsLastWeek}</span>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-slate-100 dark:border-slate-700 transition-colors">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{t.dashboard.securityEvents}</p>
              <p className="text-2xl font-bold text-slate-800 dark:text-white mt-1">24</p>
            </div>
            <div className="p-3 bg-amber-50 dark:bg-amber-900/30 rounded-lg text-amber-600 dark:text-amber-400">
              <Shield size={24} />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-red-500 font-medium">+2</span>
            <span className="text-slate-400 dark:text-slate-500 ml-2">{t.dashboard.criticalAlerts}</span>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-slate-100 dark:border-slate-700 transition-colors">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{t.dashboard.hipaaScore}</p>
              <p className="text-2xl font-bold text-slate-800 dark:text-white mt-1">98%</p>
            </div>
            <div className="p-3 bg-emerald-50 dark:bg-emerald-900/30 rounded-lg text-emerald-600 dark:text-emerald-400">
              <CheckCircle size={24} />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-green-500 font-medium">{t.dashboard.compliant}</span>
            <span className="text-slate-400 dark:text-slate-500 ml-2">{t.dashboard.lastAudit}</span>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-slate-100 dark:border-slate-700 transition-colors">
          <h3 className="text-lg font-semibold text-slate-800 dark:text-white mb-4">{t.dashboard.apiGatewayTraffic}</h3>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={chartGridColor} />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: chartTextColor, fontSize: 12}} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: chartTextColor, fontSize: 12}} />
                <Tooltip 
                  contentStyle={{ backgroundColor: tooltipBg, borderRadius: '8px', border: `1px solid ${tooltipBorder}`, color: theme === 'dark' ? '#fff' : '#000', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  itemStyle={{ color: theme === 'dark' ? '#e2e8f0' : '#1e293b' }}
                />
                <Line type="monotone" dataKey="apiCalls" stroke="#3b82f6" strokeWidth={3} dot={{r: 4, strokeWidth: 2}} activeDot={{r: 6}} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-slate-100 dark:border-slate-700 transition-colors">
          <h3 className="text-lg font-semibold text-slate-800 dark:text-white mb-4">{t.dashboard.errorRateDistribution}</h3>
          <div className="h-80 w-full">
             <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={chartGridColor} />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: chartTextColor, fontSize: 12}} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: chartTextColor, fontSize: 12}} />
                <Tooltip 
                    cursor={{fill: theme === 'dark' ? '#334155' : '#f1f5f9'}} 
                    contentStyle={{ backgroundColor: tooltipBg, borderRadius: '8px', border: `1px solid ${tooltipBorder}`, color: theme === 'dark' ? '#fff' : '#000' }} 
                    itemStyle={{ color: theme === 'dark' ? '#e2e8f0' : '#1e293b' }}
                />
                <Bar dataKey="errors" fill="#ef4444" radius={[4, 4, 0, 0]} barSize={32} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Project Status */}
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-100 dark:border-slate-700 overflow-hidden transition-colors">
        <div className="px-6 py-4 border-b border-slate-100 dark:border-slate-700">
          <h3 className="text-lg font-semibold text-slate-800 dark:text-white">{t.dashboard.moduleStatus}</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {[
              { name: 'Management UI', progress: 100, status: t.dashboard.completed, color: 'bg-green-500' },
              { name: 'API Gateway', progress: 100, status: t.dashboard.completed, color: 'bg-green-500' },
              { name: 'User Management (RBAC)', progress: 90, status: t.dashboard.inReview, color: 'bg-blue-500' },
              { name: 'Identity / Security', progress: 85, status: t.dashboard.testing, color: 'bg-blue-500' },
              { name: 'Audit Log Core', progress: 75, status: t.dashboard.inProgress, color: 'bg-amber-500' },
              { name: 'Audit Query/Export', progress: 60, status: t.dashboard.inProgress, color: 'bg-amber-500' },
              { name: 'Compliance Check (HIPAA)', progress: 40, status: t.dashboard.development, color: 'bg-purple-500' },
            ].map((module) => (
              <div key={module.name} className="flex items-center">
                <div className="w-1/3 text-sm font-medium text-slate-700 dark:text-slate-300">{module.name}</div>
                <div className="w-1/2 mx-4 bg-slate-100 dark:bg-slate-700 rounded-full h-2.5">
                  <div className={`h-2.5 rounded-full ${module.color}`} style={{ width: `${module.progress}%` }}></div>
                </div>
                <div className="w-1/6 text-xs text-right text-slate-500 dark:text-slate-400">{module.status}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;