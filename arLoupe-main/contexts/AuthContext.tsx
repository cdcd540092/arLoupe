import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { User, Role } from '../types';
import { addLog } from '../services/auditService';

interface AuthContextType {
  currentUser: User | null;
  login: (email: string, password?: string) => boolean;
  register: (name: string, email: string, password?: string) => boolean;
  addUser: (name: string, email: string, role: Role, password?: string) => boolean;
  updateUser: (id: string, data: Partial<User>, password?: string) => boolean;
  deleteUser: (id: string) => boolean;
  logout: () => void;
  switchUser: (userId: string) => void;
  verifyUserPassword: (userId: string, password: string) => boolean;
  isAuthenticated: boolean;
  users: User[];
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Initial default admin user
const DEFAULT_ADMIN: User = {
    id: 'admin-001',
    name: 'Administrator',
    email: 'user', // The specific login ID requested
    role: Role.ADMIN,
    status: 'Active',
    lastLogin: new Date().toLocaleString()
};

const DEFAULT_ADMIN_PASS = '0410nfu';

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [users, setUsers] = useState<User[]>([DEFAULT_ADMIN]);
  
  // In a real app, passwords are never stored in plain text. 
  // For this mock, we map userId/email to password.
  const [userPasswords, setUserPasswords] = useState<Record<string, string>>({
      'user': DEFAULT_ADMIN_PASS
  });

  const login = (email: string, password?: string) => {
    // Check if user exists
    const user = users.find(u => u.email.toLowerCase() === email.toLowerCase());
    
    if (user) {
        // Verify password
        if (password && userPasswords[user.email] === password) {
            setCurrentUser(user);
            // Update last login
            const updatedUsers = users.map(u => u.id === user.id ? {...u, lastLogin: new Date().toLocaleString()} : u);
            setUsers(updatedUsers);
            
            // Log Success
            addLog(user.id, user.name, 'Login', 'System Authentication', 'Success', 'User logged in successfully');
            return true;
        }
    }
    
    // Log Failure
    addLog('unknown', email || 'Unknown', 'Login Attempt', 'System Authentication', 'Failure', `Failed login attempt for email: ${email}`);
    return false;
  };

  const register = (name: string, email: string, password?: string) => {
    if (users.some(u => u.email.toLowerCase() === email.toLowerCase())) {
        return false;
    }

    const newUser: User = {
        id: `user-${Date.now()}`,
        name: name,
        email: email,
        role: Role.VIEWER,
        status: 'Active',
        lastLogin: new Date().toLocaleString()
    };

    setUsers(prev => [...prev, newUser]);
    if (password) {
        setUserPasswords(prev => ({...prev, [email]: password}));
    }
    setCurrentUser(newUser);

    addLog(newUser.id, newUser.name, 'Register', 'User Database', 'Success', 'New user account created');
    return true;
  };

  // Add User (for Admin usage, does not log in)
  const addUser = (name: string, email: string, role: Role, password?: string) => {
    if (users.some(u => u.email.toLowerCase() === email.toLowerCase())) {
        return false;
    }

    const newUser: User = {
        id: `user-${Date.now()}`,
        name: name,
        email: email,
        role: role,
        status: 'Active',
        lastLogin: '-'
    };

    setUsers(prev => [...prev, newUser]);
    if (password) {
        setUserPasswords(prev => ({...prev, [email]: password}));
    }

    addLog(
      currentUser?.id || 'system', 
      currentUser?.name || 'System', 
      'Create User', 
      `User: ${email}`, 
      'Success', 
      `Created new user ${name} with role ${role}`
    );
    return true;
  };

  const updateUser = (id: string, data: Partial<User>, password?: string) => {
      const targetUser = users.find(u => u.id === id);
      setUsers(prev => prev.map(u => u.id === id ? { ...u, ...data } : u));
      
      // Update current user if it's the one being edited
      if (currentUser?.id === id) {
          setCurrentUser(prev => prev ? { ...prev, ...data } : null);
      }

      if (password && data.email) {
          setUserPasswords(prev => ({...prev, [data.email!]: password}));
      }

      addLog(
        currentUser?.id || 'system', 
        currentUser?.name || 'System', 
        'Update User', 
        `User: ${targetUser?.email || id}`, 
        'Success', 
        `Updated profile details`
      );
      return true;
  };

  const deleteUser = (id: string) => {
      if (currentUser?.id === id) {
          return false; // Cannot delete self
      }
      const targetUser = users.find(u => u.id === id);
      setUsers(prev => prev.filter(u => u.id !== id));

      addLog(
        currentUser?.id || 'system', 
        currentUser?.name || 'System', 
        'Delete User', 
        `User: ${targetUser?.email || id}`, 
        'Success', 
        `Deleted user account`
      );
      return true;
  };

  const logout = () => {
    if (currentUser) {
        addLog(currentUser.id, currentUser.name, 'Logout', 'System Authentication', 'Success', 'User logged out');
    }
    setCurrentUser(null);
  };

  const verifyUserPassword = (userId: string, password: string): boolean => {
      const user = users.find(u => u.id === userId);
      if (!user) return false;
      return userPasswords[user.email] === password;
  };

  const switchUser = (userId: string) => {
    const user = users.find(u => u.id === userId);
    if (user) {
      if (currentUser) {
          addLog(currentUser.id, currentUser.name, 'Switch Account', 'Session Management', 'Success', `Switched to user ${user.name}`);
      }
      setCurrentUser(user);
    }
  };

  return (
    <AuthContext.Provider value={{ currentUser, login, register, addUser, updateUser, deleteUser, logout, switchUser, verifyUserPassword, isAuthenticated: !!currentUser, users }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};