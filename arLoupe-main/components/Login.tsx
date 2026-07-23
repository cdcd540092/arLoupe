import React, { useState, useEffect } from 'react';
import { Lock, Mail, ArrowRight, ShieldCheck, Globe, User as UserIcon, Check, AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  // Registration States
  const [isRegistering, setIsRegistering] = useState(false);
  const [name, setName] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const [error, setError] = useState('');
  const { login, register } = useAuth();
  const { t, language, setLanguage } = useLanguage();

  const [passwordStrength, setPasswordStrength] = useState<0 | 1 | 2 | 3>(0);

  // Password Complexity Regex: At least 1 Uppercase, 1 Number, 1 Special Char
  // This is a comprehensive check
  const complexityRegex = /(?=.*[A-Z])(?=.*[0-9])(?=.*[^A-Za-z0-9])/;

  const checkStrength = (pass: string) => {
    let score = 0;
    if (!pass) return 0;
    if (pass.length >= 8) score++;
    if (/[A-Z]/.test(pass)) score++;
    if (/[0-9]/.test(pass)) score++;
    if (/[^A-Za-z0-9]/.test(pass)) score++;
    
    // Normalize to 1-3 scale for simple UI
    if (score < 2) return 1; // Weak
    if (score === 3) return 2; // Medium
    if (score >= 4) return 3; // Strong
    return 1;
  };

  useEffect(() => {
    if (isRegistering) {
        setPasswordStrength(checkStrength(password) as any);
    }
  }, [password, isRegistering]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (isRegistering) {
        if (password !== confirmPassword) {
            setError(t.login.passwordsDoNotMatch);
            return;
        }
        
        // Strict Validation for Registration
        if (!complexityRegex.test(password)) {
            setError(t.login.requirements);
            return;
        }

        if (!name || !email || !password) {
            setError(t.login.invalid);
            return;
        }
        const success = register(name, email, password);
        if (!success) {
            setError("User already exists");
        }
    } else {
        const success = login(email, password);
        if (!success) {
            setError(t.login.invalid);
        }
    }
  };

  const toggleLanguage = () => {
    setLanguage(language === 'en' ? 'zh-TW' : 'en');
  };

  const getStrengthColor = (s: number) => {
      if (s === 1) return 'bg-red-500';
      if (s === 2) return 'bg-yellow-500';
      if (s === 3) return 'bg-green-500';
      return 'bg-slate-200';
  };

  const getStrengthText = (s: number) => {
      if (s === 1) return t.login.weak;
      if (s === 2) return t.login.medium;
      if (s === 3) return t.login.strong;
      return '';
  };

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0">
        <div className="absolute -top-40 -left-40 w-96 h-96 rounded-full bg-blue-600/20 blur-3xl"></div>
        <div className="absolute top-1/2 right-0 w-80 h-80 rounded-full bg-purple-600/10 blur-3xl"></div>
      </div>

      <div className="absolute top-6 right-6 z-20">
         <button 
            onClick={toggleLanguage}
            className="flex items-center px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-full text-sm font-medium transition-colors border border-slate-700"
          >
            <Globe size={16} className="mr-2" />
            {language === 'en' ? 'English' : '繁體中文'}
          </button>
      </div>

      <div className="w-full max-w-md bg-white dark:bg-slate-800 rounded-2xl shadow-2xl overflow-hidden z-10 animate-fade-in border border-slate-700/50">
        <div className="p-8 pb-8">
          <div className="flex justify-center mb-6">
            <div className="h-16 w-16 bg-blue-100 dark:bg-blue-900/30 rounded-2xl flex items-center justify-center text-blue-600 dark:text-blue-400 shadow-inner">
              <ShieldCheck size={36} />
            </div>
          </div>
          
          <h2 className="text-2xl font-bold text-center text-slate-800 dark:text-white mb-2">
            {isRegistering ? t.login.titleRegister : t.login.title}
          </h2>
          <p className="text-center text-slate-500 dark:text-slate-400 text-sm mb-8">
            {isRegistering ? t.login.subtitleRegister : t.login.subtitle}
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            
            {/* Name Field (Register Only) */}
            {isRegistering && (
                <div className="animate-fade-in">
                <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase mb-1">{t.login.name}</label>
                <div className="relative">
                    <UserIcon className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                    <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 border border-slate-300 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-slate-800 dark:text-white bg-white dark:bg-slate-700"
                    placeholder="User Name"
                    required={isRegistering}
                    />
                </div>
                </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase mb-1">{t.login.email}</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input
                  type="text" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 border border-slate-300 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-slate-800 dark:text-white bg-white dark:bg-slate-700"
                  placeholder="user"
                  required
                />
              </div>
            </div>
            
            <div>
              <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase mb-1">{t.login.password}</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 border border-slate-300 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-slate-800 dark:text-white bg-white dark:bg-slate-700"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            {/* Password Strength Indicator (Register Only) */}
            {isRegistering && password && (
                <div className="animate-fade-in">
                    <div className="flex justify-between items-center mb-1">
                        <span className="text-xs text-slate-500 dark:text-slate-400">{t.login.passwordStrength}</span>
                        <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">{getStrengthText(passwordStrength)}</span>
                    </div>
                    <div className="h-1.5 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden flex">
                        <div className={`h-full ${getStrengthColor(passwordStrength)} transition-all duration-300`} style={{ width: `${(passwordStrength / 3) * 100}%` }}></div>
                    </div>
                    <div className="mt-2 text-xs text-slate-500 dark:text-slate-400 flex items-start">
                         <AlertCircle size={12} className="mr-1 mt-0.5 flex-shrink-0" />
                         {t.login.requirements}
                    </div>
                </div>
            )}

            {/* Confirm Password (Register Only) */}
             {isRegistering && (
                <div className="animate-fade-in">
                <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase mb-1">{t.login.confirmPassword}</label>
                <div className="relative">
                    <Check className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                    <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 border border-slate-300 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-slate-800 dark:text-white bg-white dark:bg-slate-700"
                    placeholder="••••••••"
                    required={isRegistering}
                    />
                </div>
                </div>
            )}

            {error && <p className="text-red-500 text-sm text-center font-medium bg-red-50 dark:bg-red-900/20 p-2 rounded border border-red-100 dark:border-red-800">{error}</p>}

            <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 rounded-lg transition-colors flex items-center justify-center group shadow-lg shadow-blue-900/20"
            >
              {isRegistering ? t.login.signUp : t.login.signIn}
              <ArrowRight size={18} className="ml-2 group-hover:translate-x-1 transition-transform" />
            </button>
          </form>

          {/* Toggle Register/Login */}
          <div className="mt-6 text-center">
            <p className="text-sm text-slate-500 dark:text-slate-400">
                {isRegistering ? t.login.haveAccount : t.login.noAccount}{' '}
                <button 
                    onClick={() => {
                        setIsRegistering(!isRegistering);
                        setError('');
                        setPassword('');
                        setConfirmPassword('');
                        setEmail('');
                        setName('');
                    }}
                    className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-semibold transition-colors"
                >
                    {isRegistering ? t.login.signIn : t.login.signUp}
                </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;