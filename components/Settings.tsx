import React from 'react';
import { Server, Shield, Globe, Database } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';

const Settings: React.FC = () => {
  const { t } = useLanguage();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-800 dark:text-white">{t.settings.title}</h2>
        <p className="text-slate-500 dark:text-slate-400 mt-1">{t.settings.subtitle}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 transition-colors">
            <h3 className="font-semibold text-slate-800 dark:text-white mb-4 flex items-center">
                <Globe className="mr-2 text-blue-500" size={20}/> {t.settings.routingRules}
            </h3>
            <div className="space-y-4">
                <div className="flex justify-between items-center p-3 border border-slate-100 dark:border-slate-700 rounded-lg">
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-300">/api/v1/patients</span>
                    <span className="text-xs bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 px-2 py-1 rounded">Active</span>
                </div>
                <div className="flex justify-between items-center p-3 border border-slate-100 dark:border-slate-700 rounded-lg">
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-300">/api/v1/auth</span>
                    <span className="text-xs bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 px-2 py-1 rounded">Active</span>
                </div>
                <div className="flex justify-between items-center p-3 border border-slate-100 dark:border-slate-700 rounded-lg">
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-300">/api/v1/audit</span>
                    <span className="text-xs bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 px-2 py-1 rounded">Rate Limited</span>
                </div>
            </div>
        </div>

        <div className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 transition-colors">
            <h3 className="font-semibold text-slate-800 dark:text-white mb-4 flex items-center">
                <Shield className="mr-2 text-purple-500" size={20}/> {t.settings.securityPolicies}
            </h3>
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-sm font-medium text-slate-800 dark:text-slate-200">{t.settings.jwt}</p>
                        <p className="text-xs text-slate-500 dark:text-slate-400">{t.settings.jwtDesc}</p>
                    </div>
                     <div className="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in">
                        <input type="checkbox" name="toggle" id="jwt-toggle" className="toggle-checkbox absolute block w-5 h-5 rounded-full bg-white border-4 appearance-none cursor-pointer" checked readOnly/>
                        <label htmlFor="jwt-toggle" className="toggle-label block overflow-hidden h-5 rounded-full bg-blue-600 cursor-pointer"></label>
                    </div>
                </div>
                 <div className="flex items-center justify-between">
                    <div>
                        <p className="text-sm font-medium text-slate-800 dark:text-slate-200">{t.settings.rateLimit}</p>
                        <p className="text-xs text-slate-500 dark:text-slate-400">{t.settings.rateLimitDesc}</p>
                    </div>
                     <div className="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in">
                        <input type="checkbox" name="toggle" id="rate-toggle" className="toggle-checkbox absolute block w-5 h-5 rounded-full bg-white border-4 appearance-none cursor-pointer" checked readOnly/>
                        <label htmlFor="rate-toggle" className="toggle-label block overflow-hidden h-5 rounded-full bg-blue-600 cursor-pointer"></label>
                    </div>
                </div>
            </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;