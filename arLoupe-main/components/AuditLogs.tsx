import React, { useState, useEffect } from 'react';
import { Download, Search, Filter, AlertCircle, CheckCircle, Calendar, X, RefreshCw } from 'lucide-react';
import { AuditLog } from '../types';
import { useLanguage } from '../contexts/LanguageContext';
import { getLogs } from '../services/auditService';

const AuditLogs: React.FC = () => {
  // Initialize from service
  const [logs, setLogs] = useState<AuditLog[]>([]);
  
  // Filter States
  const [searchTerm, setSearchTerm] = useState('');
  const [showDateFilter, setShowDateFilter] = useState(false);
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  
  const { t } = useLanguage();

  const fetchLogs = () => {
    const data = getLogs();
    setLogs(data);
  };

  // Fetch logs on mount
  useEffect(() => {
    fetchLogs();
  }, []);

  const filteredLogs = logs.filter(log => {
    // 1. Text Search Filter
    const matchesSearch = 
      log.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.userName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.resource.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.details.toLowerCase().includes(searchTerm.toLowerCase());

    // 2. Date Range Filter
    let matchesDate = true;
    if (dateRange.start || dateRange.end) {
      const logTime = new Date(log.timestamp).getTime();
      const startTime = dateRange.start ? new Date(dateRange.start).setHours(0,0,0,0) : 0;
      const endTime = dateRange.end ? new Date(dateRange.end).setHours(23,59,59,999) : Infinity;
      
      matchesDate = logTime >= startTime && logTime <= endTime;
    }

    return matchesSearch && matchesDate;
  });

  const clearDateFilter = () => {
    setDateRange({ start: '', end: '' });
    setShowDateFilter(false);
  };

  const handleExport = () => {
    // Helper to escape fields for CSV (wrap in quotes and escape internal quotes)
    const escape = (text: string) => {
      if (!text) return '""';
      return `"${String(text).replace(/"/g, '""')}"`;
    };

    const headers = ["Timestamp", "User", "Action", "Resource", "Status", "IP Address", "Details"];
    
    // Map data to CSV rows with escaping
    const rows = filteredLogs.map(log => 
      [
        escape(log.timestamp), 
        escape(log.userName), 
        escape(log.action), 
        escape(log.resource), 
        escape(log.status), 
        escape(log.ipAddress), 
        escape(log.details)
      ].join(",")
    );

    // Add Byte Order Mark (BOM) \uFEFF so Excel recognizes it as UTF-8
    const csvContent = "\uFEFF" + [headers.join(","), ...rows].join("\n");
    
    // Use Blob for better handling of encoding
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement("a");
    link.setAttribute("href", url);
    // Use ISO string for filename to avoid spaces/special chars issues
    link.setAttribute("download", `audit_logs_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-800 dark:text-white">{t.audit.title}</h2>
          <p className="text-slate-500 dark:text-slate-400 mt-1">{t.audit.subtitle}</p>
        </div>
        <div className="flex gap-2">
            <button 
            onClick={fetchLogs}
            className="bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 px-3 py-2 rounded-lg flex items-center shadow-sm transition-colors"
            title="Refresh Logs"
            >
            <RefreshCw size={18} />
            </button>
            <button 
            onClick={handleExport}
            className="bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700 px-4 py-2 rounded-lg flex items-center shadow-sm transition-colors"
            >
            <Download size={18} className="mr-2" />
            {t.audit.exportCsv}
            </button>
        </div>
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden transition-colors">
        {/* Main Toolbar */}
        <div className="p-4 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
          <div className="relative flex-1 w-full md:max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
            <input 
              type="text" 
              placeholder={t.audit.searchPlaceholder}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-200"
            />
          </div>
          <div className="flex gap-2 w-full md:w-auto">
            <button 
              onClick={() => setShowDateFilter(!showDateFilter)}
              className={`flex items-center px-4 py-2 border rounded-lg text-sm transition-colors ${
                showDateFilter || dateRange.start || dateRange.end
                  ? 'bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-300' 
                  : 'bg-white dark:bg-slate-800 border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700'
              }`}
            >
              <Filter size={16} className="mr-2" />
              {t.audit.filterDate}
              {(dateRange.start || dateRange.end) && (
                 <span className="ml-2 w-2 h-2 bg-blue-500 rounded-full"></span>
              )}
            </button>
          </div>
        </div>

        {/* Date Filter Panel */}
        {showDateFilter && (
            <div className="p-4 bg-slate-100 dark:bg-slate-800/80 border-b border-slate-200 dark:border-slate-700 flex flex-col sm:flex-row items-center gap-4 animate-fade-in">
                <div className="flex items-center gap-2 w-full sm:w-auto">
                    <span className="text-sm text-slate-600 dark:text-slate-400 font-medium">From:</span>
                    <input 
                        type="date" 
                        value={dateRange.start}
                        onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
                        className="px-3 py-1.5 border border-slate-300 dark:border-slate-600 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none w-full sm:w-auto bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-200"
                    />
                </div>
                <div className="flex items-center gap-2 w-full sm:w-auto">
                    <span className="text-sm text-slate-600 dark:text-slate-400 font-medium">To:</span>
                    <input 
                        type="date" 
                        value={dateRange.end}
                        onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
                        className="px-3 py-1.5 border border-slate-300 dark:border-slate-600 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none w-full sm:w-auto bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-200"
                    />
                </div>
                {(dateRange.start || dateRange.end) && (
                    <button 
                        onClick={clearDateFilter}
                        className="text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 flex items-center ml-auto sm:ml-0"
                    >
                        <X size={14} className="mr-1" /> Clear
                    </button>
                )}
            </div>
        )}

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 dark:bg-slate-700/50">
              <tr>
                <th className="px-6 py-3 text-left font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{t.audit.columns.timestamp}</th>
                <th className="px-6 py-3 text-left font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{t.audit.columns.user}</th>
                <th className="px-6 py-3 text-left font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{t.audit.columns.action}</th>
                <th className="px-6 py-3 text-left font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{t.audit.columns.resource}</th>
                <th className="px-6 py-3 text-left font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{t.audit.columns.status}</th>
                <th className="px-6 py-3 text-left font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{t.audit.columns.details}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
              {filteredLogs.length > 0 ? (
                  filteredLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap text-slate-500 dark:text-slate-400 font-mono text-xs">{log.timestamp}</td>
                      <td className="px-6 py-4 whitespace-nowrap font-medium text-slate-800 dark:text-slate-200">{log.userName}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 py-1 bg-slate-100 dark:bg-slate-700 rounded text-xs font-semibold text-slate-600 dark:text-slate-300">
                          {log.action}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-slate-600 dark:text-slate-400">{log.resource}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {log.status === 'Success' ? (
                          <span className="flex items-center text-green-600 dark:text-green-400 text-xs font-medium">
                            <CheckCircle size={14} className="mr-1" /> {t.audit.success}
                          </span>
                        ) : (
                          <span className="flex items-center text-red-600 dark:text-red-400 text-xs font-medium">
                            <AlertCircle size={14} className="mr-1" /> {t.audit.failure}
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-slate-500 dark:text-slate-400">{log.details}</td>
                    </tr>
                  ))
              ) : (
                  <tr>
                      <td colSpan={6} className="px-6 py-8 text-center text-slate-400">
                          <div className="flex flex-col items-center">
                              <Search size={32} className="mb-2 opacity-50" />
                              <p>No audit logs found matching your criteria.</p>
                          </div>
                      </td>
                  </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AuditLogs;