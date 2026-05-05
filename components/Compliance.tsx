import React, { useState } from 'react';
import { ShieldCheck, AlertTriangle, Check, RefreshCw, Lock, Sparkles } from 'lucide-react';
import { analyzeCompliance } from '../services/geminiService';
import { ComplianceCheck } from '../types';
import { useLanguage } from '../contexts/LanguageContext';
import { useAuth } from '../contexts/AuthContext';
import { addLog } from '../services/auditService';

const INITIAL_CONFIG = `
System Configuration:
- TLS Version: 1.3
- Database Encryption: AES-256
- Access Control: Role-Based (RBAC) enforced
- Audit Logging: Enabled, retention 90 days
- Session Timeout: 15 minutes
- Password Policy: Min 8 chars, alphanumeric
- MFA: Enabled for Administrators only
- Data Backup: Daily, encrypted off-site
- PHI Access: Restricted to specific roles
`;

const Compliance: React.FC = () => {
  const [config, setConfig] = useState(INITIAL_CONFIG);
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<{ summary: string; checks: ComplianceCheck[] } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { t, language } = useLanguage();
  const { currentUser } = useAuth();

  const runAudit = async () => {
    setLoading(true);
    setError(null);
    try {
      // Pass the current language to the service
      const result = await analyzeCompliance(config, language);
      setReport(result);
      
      // Log the action
      addLog(
          currentUser?.id || 'sys', 
          currentUser?.name || 'System', 
          'Compliance Audit', 
          'HIPAA AI Analyzer', 
          'Success', 
          'Ran AI compliance verification'
      );
    } catch (err) {
      setError(t.compliance.error);
      addLog(
          currentUser?.id || 'sys', 
          currentUser?.name || 'System', 
          'Compliance Audit', 
          'HIPAA AI Analyzer', 
          'Failure', 
          'AI Audit Failed'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-800 dark:text-white">{t.compliance.title}</h2>
          <p className="text-slate-500 dark:text-slate-400 mt-1">{t.compliance.subtitle}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Input */}
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-4 transition-colors">
            <h3 className="font-semibold text-slate-800 dark:text-white mb-3 flex items-center">
              <Lock size={18} className="mr-2 text-blue-500" />
              {t.compliance.systemContext}
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">
              {t.compliance.contextDesc}
            </p>
            <textarea 
              value={config}
              onChange={(e) => setConfig(e.target.value)}
              className="w-full h-96 p-3 text-sm border border-slate-300 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-200"
            />
            <button 
              onClick={runAudit}
              disabled={loading}
              className="mt-4 w-full bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded-lg flex items-center justify-center transition-colors disabled:opacity-70"
            >
              {loading ? (
                <>
                  <RefreshCw size={18} className="mr-2 animate-spin" /> {t.compliance.analyzing}
                </>
              ) : (
                <>
                  <Sparkles size={18} className="mr-2" /> {t.compliance.runAudit}
                </>
              )}
            </button>
          </div>
        </div>

        {/* Report Output */}
        <div className="lg:col-span-2 space-y-4">
          {error && (
             <div className="p-4 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 rounded-xl border border-red-200 dark:border-red-800 flex items-center">
               <AlertTriangle size={20} className="mr-3" />
               {error}
             </div>
          )}

          {!report && !loading && !error && (
            <div className="h-full flex flex-col items-center justify-center p-12 bg-slate-50 dark:bg-slate-800/50 rounded-xl border-2 border-dashed border-slate-200 dark:border-slate-700 text-slate-400 dark:text-slate-500">
              <ShieldCheck size={48} className="mb-4 opacity-50" />
              <p>{t.compliance.ready}</p>
            </div>
          )}

          {report && (
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden animate-fade-in transition-colors">
              <div className="p-6 border-b border-slate-100 dark:border-slate-700 bg-gradient-to-r from-indigo-50 to-white dark:from-indigo-900/30 dark:to-slate-800">
                <h3 className="text-lg font-bold text-slate-800 dark:text-white flex items-center">
                  <ShieldCheck size={20} className="mr-2 text-indigo-600 dark:text-indigo-400" />
                  {t.compliance.auditResults}
                </h3>
                <p className="mt-2 text-slate-600 dark:text-slate-300 text-sm leading-relaxed">
                  {report.summary}
                </p>
              </div>
              <div className="divide-y divide-slate-100 dark:divide-slate-700">
                {report.checks.map((check, idx) => (
                  <div key={idx} className="p-4 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                    <div className="flex items-start">
                      <div className="flex-shrink-0 mt-0.5">
                        {check.status === 'Pass' && <Check size={20} className="text-green-500" />}
                        {check.status === 'Warning' && <AlertTriangle size={20} className="text-amber-500" />}
                        {check.status === 'Fail' && <AlertTriangle size={20} className="text-red-500" />}
                      </div>
                      <div className="ml-4 flex-1">
                        <div className="flex items-center justify-between">
                           <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200">{check.item}</h4>
                           <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                             check.status === 'Pass' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                             check.status === 'Warning' ? 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300' :
                             'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                           }`}>
                             {check.status.toUpperCase()}
                           </span>
                        </div>
                        <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">{check.details}</p>
                        {check.recommendation && (
                          <div className="mt-2 text-xs bg-slate-100 dark:bg-slate-700 p-2 rounded text-slate-700 dark:text-slate-300">
                            <span className="font-semibold">{t.compliance.recommendation}:</span> {check.recommendation}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Compliance;