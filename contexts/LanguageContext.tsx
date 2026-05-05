import React, { createContext, useContext, useState, ReactNode } from 'react';
import { Language } from '../types';

const translations = {
  en: {
    layout: {
      dashboard: 'Dashboard',
      users: 'User Management (RBAC)',
      audit: 'Audit Logs',
      compliance: 'Compliance (HIPAA)',
      settings: 'API Gateway Settings',
      signOut: 'Sign Out',
      adminUser: 'Admin User',
      superAdmin: 'Super Administrator',
      search: 'Global Search...',
      switchAccount: 'Switch Account',
      profile: 'Profile',
      signedInAs: 'Signed in as',
      notifications: 'Notifications',
      noNotifications: 'No new notifications',
      markAllRead: 'Mark all as read',
      new: 'New',
      verifyIdentity: 'Verify Identity',
      enterPasswordFor: 'Enter password for',
      confirmSwitch: 'Switch Account',
      cancel: 'Cancel',
      wrongPassword: 'Incorrect Password'
    },
    login: {
      title: 'Sign in to NFU Admin',
      titleRegister: 'Create an Account',
      subtitle: 'Enter your credentials to access the secure dashboard.',
      subtitleRegister: 'Join us to manage your secure dashboard.',
      email: 'Account / Email',
      name: 'Full Name',
      password: 'Password',
      confirmPassword: 'Confirm Password',
      signIn: 'Sign In',
      signUp: 'Sign Up',
      demoNote: '', 
      invalid: 'Invalid credentials',
      passwordsDoNotMatch: 'Passwords do not match',
      noAccount: "Don't have an account?",
      haveAccount: "Already have an account?",
      passwordStrength: "Password Strength",
      weak: "Weak",
      medium: "Medium",
      strong: "Strong",
      requirements: "Must contain: 1 uppercase, 1 number, 1 special char"
    },
    dashboard: {
      title: 'Phase 2: API Integration Status',
      subtitle: 'System overview and M6-M8 milestone tracking.',
      totalApiCalls: 'Total API Calls',
      activeUsers: 'Active Users',
      securityEvents: 'Security Events',
      hipaaScore: 'HIPAA Score',
      vsLastWeek: 'vs last week',
      criticalAlerts: 'Critical alerts',
      compliant: 'Compliant',
      lastAudit: 'Last audit: 2h ago',
      apiGatewayTraffic: 'API Gateway Traffic',
      errorRateDistribution: 'Error Rate Distribution',
      moduleStatus: 'Module Completion Status (M6-M8)',
      completed: 'Completed',
      inReview: 'In Review',
      testing: 'Testing',
      inProgress: 'In Progress',
      development: 'Development'
    },
    users: {
      title: 'User Management',
      subtitle: 'Manage system access, roles, and permissions (RBAC).',
      addUser: 'Add User',
      searchPlaceholder: 'Search users...',
      allRoles: 'All Roles',
      allStatus: 'All Status',
      columns: {
        user: 'User',
        role: 'Role',
        status: 'Status',
        lastLogin: 'Last Login',
        actions: 'Actions'
      },
      showing: 'Showing',
      of: 'of',
      results: 'results',
      previous: 'Previous',
      next: 'Next',
      modalTitle: 'Create New User',
      modalTitleEdit: 'Edit User',
      save: 'Create User',
      update: 'Update User',
      cancel: 'Cancel',
      role: 'Role',
      userExists: 'User with this email already exists',
      success: 'User created successfully',
      successUpdate: 'User updated successfully',
      confirmDelete: 'Are you sure you want to delete this user?',
      cannotDeleteSelf: 'You cannot delete your own account.',
      leaveBlank: 'Leave blank to keep current password'
    },
    audit: {
      title: 'Audit Logs',
      subtitle: 'Track system activity, security events, and data access.',
      exportCsv: 'Export CSV',
      searchPlaceholder: 'Search by User, Action, or Resource...',
      filterDate: 'Filter Date',
      columns: {
        timestamp: 'Timestamp',
        user: 'User',
        action: 'Action',
        resource: 'Resource',
        status: 'Status',
        details: 'Details'
      },
      success: 'Success',
      failure: 'Failure'
    },
    compliance: {
      title: 'HIPAA Compliance Center',
      subtitle: 'AI-driven automated compliance verification and risk assessment.',
      systemContext: 'System Context',
      contextDesc: 'Paste your system configuration, security policies, or infrastructure details here for the AI to analyze against HIPAA standards.',
      runAudit: 'Run AI Audit',
      analyzing: 'Analyzing...',
      auditResults: 'Audit Results',
      ready: 'Ready to analyze. Click "Run AI Audit" to start.',
      error: 'Failed to generate compliance report. Please check API Key and try again.',
      recommendation: 'Recommendation'
    },
    settings: {
      title: 'API Gateway Settings',
      subtitle: 'Configure routing, rate limiting, and security policies.',
      routingRules: 'Routing Rules',
      securityPolicies: 'Security Policies',
      jwt: 'JWT Verification',
      jwtDesc: 'Validate tokens on all protected routes',
      rateLimit: 'Rate Limiting',
      rateLimitDesc: 'Max 100 req/min per IP'
    }
  },
  'zh-TW': {
    layout: {
      dashboard: '儀表板',
      users: '用戶管理 (RBAC)',
      audit: '審計日誌',
      compliance: '合規性檢查 (HIPAA)',
      settings: 'API 網關設置',
      signOut: '登出',
      adminUser: '管理員',
      superAdmin: '超級管理員',
      search: '全局搜尋...',
      switchAccount: '切換帳號',
      profile: '個人檔案',
      signedInAs: '目前登入',
      notifications: '通知',
      noNotifications: '沒有新通知',
      markAllRead: '全部標為已讀',
      new: '新',
      verifyIdentity: '身份驗證',
      enterPasswordFor: '請輸入密碼：',
      confirmSwitch: '確認切換',
      cancel: '取消',
      wrongPassword: '密碼錯誤'
    },
    login: {
      title: '登入 NFU 管理系統',
      titleRegister: '建立新帳號',
      subtitle: '輸入您的憑證以訪問安全儀表板。',
      subtitleRegister: '加入我們以管理您的安全儀表板。',
      email: '帳號 / 電子郵件',
      name: '全名',
      password: '密碼',
      confirmPassword: '確認密碼',
      signIn: '登入',
      signUp: '註冊',
      demoNote: '',
      invalid: '帳號或密碼錯誤',
      passwordsDoNotMatch: '密碼不相符',
      noAccount: "還沒有帳號？",
      haveAccount: "已經有帳號了？",
      passwordStrength: "密碼強度",
      weak: "弱",
      medium: "中",
      strong: "強",
      requirements: "需包含：1個大寫英文、1個數字、1個特殊符號"
    },
    dashboard: {
      title: '第二階段：API 整合狀態',
      subtitle: '系統概覽與 M6-M8 里程碑追蹤。',
      totalApiCalls: '總 API 調用',
      activeUsers: '活躍用戶',
      securityEvents: '安全事件',
      hipaaScore: 'HIPAA 分數',
      vsLastWeek: '比上週',
      criticalAlerts: '嚴重警報',
      compliant: '合規',
      lastAudit: '上次審計：2小時前',
      apiGatewayTraffic: 'API 網關流量',
      errorRateDistribution: '錯誤率分佈',
      moduleStatus: '模組完成狀態 (M6-M8)',
      completed: '已完成',
      inReview: '審核中',
      testing: '測試中',
      inProgress: '進行中',
      development: '開發中'
    },
    users: {
      title: '用戶管理',
      subtitle: '管理系統訪問權限、角色和許可 (RBAC)。',
      addUser: '新增用戶',
      searchPlaceholder: '搜尋用戶...',
      allRoles: '所有角色',
      allStatus: '所有狀態',
      columns: {
        user: '用戶',
        role: '角色',
        status: '狀態',
        lastLogin: '上次登入',
        actions: '操作'
      },
      showing: '顯示',
      of: '中的',
      results: '筆結果',
      previous: '上一頁',
      next: '下一頁',
      modalTitle: '新增用戶',
      modalTitleEdit: '編輯用戶',
      save: '建立用戶',
      update: '更新用戶',
      cancel: '取消',
      role: '角色',
      userExists: '此電子郵件的用戶已存在',
      success: '用戶建立成功',
      successUpdate: '用戶更新成功',
      confirmDelete: '您確定要刪除此用戶嗎？',
      cannotDeleteSelf: '您無法刪除自己的帳號。',
      leaveBlank: '若不修改密碼請留空'
    },
    audit: {
      title: '審計日誌',
      subtitle: '追蹤系統活動、安全事件和數據訪問。',
      exportCsv: '導出 CSV',
      searchPlaceholder: '搜尋用戶、操作或資源...',
      filterDate: '日期篩選',
      columns: {
        timestamp: '時間戳',
        user: '用戶',
        action: '操作',
        resource: '資源',
        status: '狀態',
        details: '詳細信息'
      },
      success: '成功',
      failure: '失敗'
    },
    compliance: {
      title: 'HIPAA 合規中心',
      subtitle: 'AI 驅動的自動化合規驗證和風險評估。',
      systemContext: '系統環境',
      contextDesc: '在此貼上您的系統配置、安全策略或基礎架構詳細信息，以便 AI 根據 HIPAA 標準進行分析。',
      runAudit: '執行 AI 審計',
      analyzing: '分析中...',
      auditResults: '審計結果',
      ready: '準備就緒。點擊「執行 AI 審計」開始。',
      error: '生成合規報告失敗。請檢查 API 金鑰並重試。',
      recommendation: '建議'
    },
    settings: {
      title: 'API 網關設置',
      subtitle: '配置路由、速率限制和安全策略。',
      routingRules: '路由規則',
      securityPolicies: '安全策略',
      jwt: 'JWT 驗證',
      jwtDesc: '在所有受保護的路由上驗證令牌',
      rateLimit: '速率限制',
      rateLimitDesc: '每 IP 每分鐘最多 100 次請求'
    }
  }
};

type Translations = typeof translations.en;

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: Translations;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [language, setLanguage] = useState<Language>('en');

  const value = {
    language,
    setLanguage,
    t: translations[language]
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};