export enum Role {
  ADMIN = 'Administrator',
  EDITOR = 'Editor',
  AUDITOR = 'Auditor',
  VIEWER = 'Viewer'
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: Role;
  status: 'Active' | 'Inactive';
  lastLogin: string;
}

// Keeping an empty array or minimal default to prevent import errors, 
// but actual initial state will be handled in AuthContext
export const MOCK_USERS: User[] = [];

export interface AuditLog {
  id: string;
  timestamp: string;
  userId: string;
  userName: string;
  action: string;
  resource: string;
  status: 'Success' | 'Failure';
  ipAddress: string;
  details: string;
}

export interface ComplianceCheck {
  item: string;
  status: 'Pass' | 'Fail' | 'Warning';
  details: string;
  recommendation?: string;
}

export type ViewState = 'dashboard' | 'users' | 'audit' | 'compliance' | 'settings';

export type Language = 'en' | 'zh-TW';
