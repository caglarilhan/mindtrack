/**
 * HIPAA Compliance Module
 * Centralized exports for all HIPAA-related functionality
 */

// Encryption
export {
  encryptPHI,
  decryptPHI,
  encryptPHIObject,
  decryptPHIObject,
  isEncrypted,
  generateEncryptionKey,
} from "./encryption";

// Access Controls
export {
  checkMinimumNecessary,
  hasAccess,
  getUserRole,
  isAdmin,
  isSupervisor,
  checkSessionTimeout,
  checkConcurrentSessions,
  type UserRole,
} from "./access-control";

// Audit Logging
export {
  createAuditLog,
  logLogin,
  logLogout,
  logDataAccess,
  logDataModification,
  logDataExport,
  logAccessDenied,
  getAuditLogs,
  searchAuditLogs,
  type AuditAction,
  type AuditLogEntry,
} from "./audit-log";

// Backup & Recovery
export {
  createBackup,
  restoreBackup,
  cleanupExpiredBackups,
  listBackups,
  type BackupConfig,
} from "./backup";





