import React, { useState, useRef, useEffect } from 'react';
import { 
  LayoutDashboard, 
  Users, 
  FileText, 
  ShieldCheck, 
  Settings, 
  LogOut,
  Menu,
  Bell,
  Search,
  Globe,
  ChevronDown,
  User as UserIcon,
  CheckCircle,
  AlertTriangle,
  Info,
  Sun,
  Moon,
  Lock,
  X
} from 'lucide-react';
import { ViewState, User } from '../types';
import { useLanguage } from '../contexts/LanguageContext';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';

interface LayoutProps {
  currentView: ViewState;
  onChangeView: (view: ViewState) => void;
  children: React.ReactNode;
}

interface Notification {
    id: string;
    title: string;
    message: string;
    time: string;
    type: 'success' | 'warning' | 'info' | 'error';
    read: boolean;
}

const Layout: React.FC<LayoutProps> = ({ currentView, onChangeView, children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  
  // Switch Account Modal State
  const [targetSwitchUser, setTargetSwitchUser] = useState<User | null>(null);
  const [switchPassword, setSwitchPassword] = useState('');
  const [switchError, setSwitchError] = useState('');

  // Notification States
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([
      { id: '1', title: 'Security Alert', message: 'Multiple failed login attempts from IP 45.22.19.112', time: '10m ago', type: 'warning', read: false },
      { id: '2', title: 'System Update', message: 'HIPAA Compliance module updated to v2.1', time: '1h ago', type: 'success', read: false },
      { id: '3', title: 'Audit Log', message: 'Weekly audit report generated successfully.', time: '3h ago', type: 'info', read: true },
  ]);

  const { t, language, setLanguage } = useLanguage();
  const { currentUser, logout, switchUser, users, verifyUserPassword } = useAuth();
  const { theme, toggleTheme } = useTheme();
  
  const profileRef = useRef<HTMLDivElement>(null);
  const notificationRef = useRef<HTMLDivElement>(null);
  const switchPasswordInputRef = useRef<HTMLInputElement>(null);

  const unreadCount = notifications.filter(n => !n.read).length;

  const handleMarkAllRead = () => {
      setNotifications(prev => prev.map(n => ({...n, read: true})));
  };

  // Close profile/notification dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setIsProfileOpen(false);
      }
      if (notificationRef.current && !notificationRef.current.contains(event.target as Node)) {
        setIsNotificationsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Focus password input when modal opens
  useEffect(() => {
    if (targetSwitchUser && switchPasswordInputRef.current) {
        switchPasswordInputRef.current.focus();
    }
  }, [targetSwitchUser]);

  const menuItems = [
    { id: 'dashboard', label: t.layout.dashboard, icon: LayoutDashboard },
    { id: 'users', label: t.layout.users, icon: Users },
    { id: 'audit', label: t.layout.audit, icon: FileText },
    { id: 'compliance', label: t.layout.compliance, icon: ShieldCheck },
    { id: 'settings', label: t.layout.settings, icon: Settings },
  ];

  const toggleLanguage = () => {
    setLanguage(language === 'en' ? 'zh-TW' : 'en');
  };

  const getInitials = (name: string) => {
    return name.charAt(0).toUpperCase();
  };

  const getNotificationIcon = (type: string) => {
      switch (type) {
          case 'warning': return <AlertTriangle size={16} className="text-amber-500" />;
          case 'error': return <AlertTriangle size={16} className="text-red-500" />;
          case 'success': return <CheckCircle size={16} className="text-green-500" />;
          default: return <Info size={16} className="text-blue-500" />;
      }
  };

  const initiateSwitchUser = (user: User) => {
      setTargetSwitchUser(user);
      setSwitchPassword('');
      setSwitchError('');
      setIsProfileOpen(false);
  };

  const handleSwitchSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      if (targetSwitchUser) {
          if (verifyUserPassword(targetSwitchUser.id, switchPassword)) {
              switchUser(targetSwitchUser.id);
              setTargetSwitchUser(null);
              setSwitchPassword('');
              onChangeView('dashboard'); // Redirect to dashboard after switch
          } else {
              setSwitchError(t.layout.wrongPassword);
          }
      }
  };

  return (
    <div className="flex h-screen bg-slate-50 dark:bg-slate-900 transition-colors duration-200 overflow-hidden">
      {/* Sidebar */}
      <aside 
        className={`bg-slate-900 dark:bg-slate-950 text-slate-300 transition-all duration-300 ease-in-out flex flex-col ${
          isSidebarOpen ? 'w-64' : 'w-20'
        } border-r border-slate-800 dark:border-slate-900`}
      >
        <div className="h-16 flex items-center justify-center border-b border-slate-700 dark:border-slate-800">
          {isSidebarOpen ? (
            <h1 className="text-xl font-bold text-white tracking-wider">NFU<span className="text-blue-500">ADMIN</span></h1>
          ) : (
            <span className="text-xl font-bold text-blue-500">NA</span>
          )}
        </div>

        <nav className="flex-1 py-6 px-3 space-y-2 overflow-y-auto">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onChangeView(item.id as ViewState)}
                className={`w-full flex items-center p-3 rounded-lg transition-colors duration-200 ${
                  isActive 
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/50' 
                    : 'hover:bg-slate-800 dark:hover:bg-slate-800 hover:text-white'
                }`}
              >
                <Icon size={20} className="min-w-[20px]" />
                {isSidebarOpen && (
                  <span className="ml-3 font-medium whitespace-nowrap overflow-hidden text-ellipsis">
                    {item.label}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        <div className="p-4 border-t border-slate-700 dark:border-slate-800">
          <button 
            onClick={logout}
            className="flex items-center justify-center w-full p-2 text-red-400 hover:bg-slate-800 dark:hover:bg-slate-800 rounded-lg transition-colors"
          >
            <LogOut size={20} />
            {isSidebarOpen && <span className="ml-3">{t.layout.signOut}</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Header */}
        <header className="h-16 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between px-6 shadow-sm z-10 transition-colors duration-200">
          <div className="flex items-center">
            <button 
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 rounded-md hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300"
            >
              <Menu size={20} />
            </button>
            <div className="ml-4 relative hidden md:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
              <input 
                type="text" 
                placeholder={t.layout.search}
                className="pl-10 pr-4 py-2 border border-slate-300 dark:border-slate-600 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 w-64 bg-slate-50 dark:bg-slate-700 dark:text-slate-200 dark:placeholder-slate-400 transition-colors"
              />
            </div>
          </div>

          <div className="flex items-center space-x-3">
             {/* Theme Toggle */}
            <button
                onClick={toggleTheme}
                className="p-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-full transition-colors"
                title="Toggle Theme"
            >
                {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
            </button>

            <button 
              onClick={toggleLanguage}
              className="flex items-center px-3 py-1.5 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 rounded-full text-xs font-medium transition-colors"
            >
              <Globe size={14} className="mr-1.5" />
              {language === 'en' ? 'English' : '繁體中文'}
            </button>

            {/* Notification Dropdown */}
            <div className="relative" ref={notificationRef}>
              <button 
                onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
                className="relative p-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-full transition-colors"
              >
                <Bell size={20} />
                {unreadCount > 0 && (
                    <span className="absolute top-1 right-1 h-2.5 w-2.5 bg-red-500 rounded-full border-2 border-white dark:border-slate-800"></span>
                )}
              </button>

              {isNotificationsOpen && (
                <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-slate-800 rounded-xl shadow-xl border border-slate-100 dark:border-slate-700 py-2 animate-fade-in z-50">
                    <div className="px-4 py-3 border-b border-slate-100 dark:border-slate-700 flex justify-between items-center">
                        <h3 className="font-semibold text-slate-800 dark:text-slate-100">{t.layout.notifications}</h3>
                        {unreadCount > 0 && (
                            <button 
                                onClick={handleMarkAllRead}
                                className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-700 font-medium"
                            >
                                {t.layout.markAllRead}
                            </button>
                        )}
                    </div>
                    
                    <div className="max-h-80 overflow-y-auto">
                        {notifications.length === 0 ? (
                            <div className="px-4 py-8 text-center text-slate-500 dark:text-slate-400 text-sm">
                                {t.layout.noNotifications}
                            </div>
                        ) : (
                            notifications.map(notification => (
                                <div key={notification.id} className={`px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-700 border-b border-slate-50 dark:border-slate-700 last:border-0 transition-colors ${!notification.read ? 'bg-blue-50/30 dark:bg-blue-900/10' : ''}`}>
                                    <div className="flex items-start">
                                        <div className={`mt-0.5 flex-shrink-0 mr-3`}>
                                            {getNotificationIcon(notification.type)}
                                        </div>
                                        <div className="flex-1">
                                            <div className="flex justify-between items-start">
                                                <p className={`text-sm ${!notification.read ? 'font-semibold text-slate-800 dark:text-slate-100' : 'font-medium text-slate-700 dark:text-slate-300'}`}>
                                                    {notification.title}
                                                </p>
                                                {!notification.read && <span className="h-2 w-2 rounded-full bg-blue-500"></span>}
                                            </div>
                                            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-2">
                                                {notification.message}
                                            </p>
                                            <p className="text-[10px] text-slate-400 dark:text-slate-500 mt-1">
                                                {notification.time}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
              )}
            </div>
            
            {/* User Profile Dropdown */}
            <div className="relative pl-4 border-l border-slate-200 dark:border-slate-700" ref={profileRef}>
              <button 
                onClick={() => setIsProfileOpen(!isProfileOpen)}
                className="flex items-center space-x-3 hover:bg-slate-50 dark:hover:bg-slate-700 p-1.5 rounded-lg transition-colors"
              >
                <div className="text-right hidden md:block">
                  <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">{currentUser?.name}</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">{currentUser?.role}</p>
                </div>
                <div className="h-9 w-9 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center text-blue-600 dark:text-blue-300 font-bold border border-blue-200 dark:border-blue-800">
                  {currentUser ? getInitials(currentUser.name) : 'U'}
                </div>
                <ChevronDown size={14} className="text-slate-400" />
              </button>

              {/* Dropdown Menu */}
              {isProfileOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-slate-800 rounded-xl shadow-xl border border-slate-100 dark:border-slate-700 py-2 animate-fade-in z-50">
                   <div className="px-4 py-2 border-b border-slate-100 dark:border-slate-700 mb-1">
                      <p className="text-xs text-slate-500 dark:text-slate-400 uppercase font-semibold">{t.layout.signedInAs}</p>
                      <p className="text-sm font-medium text-slate-800 dark:text-slate-100 truncate">{currentUser?.email}</p>
                   </div>
                   
                   <div className="px-2 py-1">
                      <div className="px-2 py-1.5 text-xs text-slate-400 uppercase font-semibold flex items-center">
                        <Users size={12} className="mr-1.5" />
                        {t.layout.switchAccount}
                      </div>
                      {users.filter(u => u.id !== currentUser?.id).slice(0, 3).map(user => (
                        <button
                          key={user.id}
                          onClick={() => initiateSwitchUser(user)}
                          className="w-full text-left px-2 py-2 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg flex items-center group"
                        >
                           <div className="h-6 w-6 rounded-full bg-slate-200 dark:bg-slate-600 flex items-center justify-center text-xs font-bold text-slate-600 dark:text-slate-300 mr-3 group-hover:bg-blue-100 dark:group-hover:bg-blue-900 group-hover:text-blue-600 dark:group-hover:text-blue-300">
                              {getInitials(user.name)}
                           </div>
                           <div className="flex-1 overflow-hidden">
                             <div className="text-sm text-slate-700 dark:text-slate-200 font-medium truncate">{user.name}</div>
                             <div className="text-xs text-slate-400 dark:text-slate-500 truncate">{user.role}</div>
                           </div>
                        </button>
                      ))}
                   </div>

                   <div className="border-t border-slate-100 dark:border-slate-700 mt-1 pt-1 px-2">
                     <button 
                        onClick={logout}
                        className="w-full text-left px-2 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg flex items-center"
                     >
                       <LogOut size={16} className="mr-2" />
                       {t.layout.signOut}
                     </button>
                   </div>
                </div>
              )}
            </div>

          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6 bg-slate-50 dark:bg-slate-900 transition-colors duration-200">
          {children}
        </main>
      </div>

      {/* Switch Account Verification Modal */}
      {targetSwitchUser && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fade-in">
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-sm overflow-hidden border border-slate-200 dark:border-slate-700">
                <div className="p-4 border-b border-slate-100 dark:border-slate-700 flex justify-between items-center bg-slate-50 dark:bg-slate-800">
                    <h3 className="font-bold text-slate-800 dark:text-white flex items-center">
                        <Lock size={16} className="mr-2 text-blue-500" />
                        {t.layout.verifyIdentity}
                    </h3>
                    <button onClick={() => setTargetSwitchUser(null)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300">
                        <X size={20} />
                    </button>
                </div>
                <form onSubmit={handleSwitchSubmit} className="p-6 space-y-4">
                    <div className="flex items-center space-x-3 mb-4 p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
                        <div className="h-10 w-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center text-blue-600 dark:text-blue-300 font-bold">
                            {getInitials(targetSwitchUser.name)}
                        </div>
                        <div>
                             <p className="text-sm font-bold text-slate-800 dark:text-white">{targetSwitchUser.name}</p>
                             <p className="text-xs text-slate-500 dark:text-slate-400">{targetSwitchUser.email}</p>
                        </div>
                    </div>

                    <div>
                        <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase mb-1">
                            {t.layout.enterPasswordFor} <span className="text-blue-600 dark:text-blue-400">{targetSwitchUser.name}</span>
                        </label>
                        <input
                            ref={switchPasswordInputRef}
                            type="password"
                            value={switchPassword}
                            onChange={(e) => setSwitchPassword(e.target.value)}
                            className="w-full px-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-slate-700 text-slate-800 dark:text-white"
                            placeholder="Password"
                            required
                        />
                        {switchError && <p className="text-red-500 text-xs mt-2 flex items-center"><AlertTriangle size={12} className="mr-1"/> {switchError}</p>}
                    </div>

                    <div className="pt-2 flex justify-end space-x-3">
                        <button
                            type="button"
                            onClick={() => setTargetSwitchUser(null)}
                            className="px-4 py-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors text-sm font-medium"
                        >
                            {t.layout.cancel}
                        </button>
                        <button
                            type="submit"
                            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm font-medium shadow-sm"
                        >
                            {t.layout.confirmSwitch}
                        </button>
                    </div>
                </form>
            </div>
        </div>
      )}
    </div>
  );
};

export default Layout;