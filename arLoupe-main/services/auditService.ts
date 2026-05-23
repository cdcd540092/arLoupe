import { AuditLog } from '../types';

const STORAGE_KEY = 'nfu_admin_audit_logs';

// Helper to generate initial history so the table isn't empty on first load
const generateInitialHistory = (): AuditLog[] => {
  const actions = ['Login', 'Update Record', 'View Record', 'Delete User', 'Export Data', 'Failed Login', 'System Config Change'];
  const resources = ['System', 'Patient: #4829', 'Patient: #9921', 'User: temp-01', 'Audit Logs', 'API Gateway'];
  const users = [
    { id: 'user-1', name: 'Dr. Sarah Connor' },
    { id: 'user-2', name: 'John Doe' },
    { id: 'user-3', name: 'Jane Smith' },
    { id: 'admin-001', name: 'Administrator' }
  ];

  const logs: AuditLog[] = [];
  const now = new Date();

  for (let i = 0; i < 15; i++) {
    const timeOffset = Math.floor(Math.random() * 72 * 60 * 60 * 1000) + 3600000; // Past 3 days, skipping last hour
    const logDate = new Date(now.getTime() - timeOffset);
    
    const user = users[Math.floor(Math.random() * users.length)];
    const action = actions[Math.floor(Math.random() * actions.length)];
    const isFailure = action === 'Failed Login';
    
    logs.push({
      id: `hist-${Date.now()}-${i}`,
      timestamp: logDate.toLocaleString('sv-SE').replace('T', ' '),
      userId: user.id,
      userName: user.name,
      action: action,
      resource: resources[Math.floor(Math.random() * resources.length)],
      status: isFailure ? 'Failure' : 'Success',
      ipAddress: `192.168.1.${Math.floor(Math.random() * 255)}`,
      details: isFailure ? 'Invalid credentials' : 'Historical record'
    });
  }
  return logs.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
};

export const getLogs = (): AuditLog[] => {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (!stored) {
    const initial = generateInitialHistory();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(initial));
    return initial;
  }
  try {
    return JSON.parse(stored);
  } catch (e) {
    return [];
  }
};

export const addLog = (
  userId: string,
  userName: string,
  action: string,
  resource: string,
  status: 'Success' | 'Failure',
  details: string
) => {
  const newLog: AuditLog = {
    id: `log-${Date.now()}`,
    timestamp: new Date().toLocaleString('sv-SE').replace('T', ' '),
    userId,
    userName,
    action,
    resource,
    status,
    ipAddress: '127.0.0.1', // Client-side mock usually implies localhost
    details
  };

  const logs = getLogs();
  // Add new log to beginning
  const updatedLogs = [newLog, ...logs];
  // Limit to last 500 logs to prevent localStorage overflow
  const trimmedLogs = updatedLogs.slice(0, 500);
  
  localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmedLogs));
  return newLog;
};

export const clearLogs = () => {
    localStorage.removeItem(STORAGE_KEY);
};