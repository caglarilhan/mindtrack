export type UserRole = 'admin' | 'clinician' | 'staff' | 'client';

export type Permission =
  | 'telehealth:link:create'
  | 'telehealth:reminder:send'
  | 'appointments:read'
  | 'appointments:write'
  | 'patients:read'
  | 'patients:write'
  | 'patient:preferences:read'
  | 'patient:preferences:write'
  | 'patient:anamnesis:read'
  | 'patient:anamnesis:write'
  | 'patient:anamnesis:decrypt:user'
  | 'patient:anamnesis:decrypt:admin'
  | 'settings:communications:read'
  | 'settings:communications:write'
  | 'patient:education:read'
  | 'patient:education:write'
  | 'patient:messages:read'
  | 'patient:messages:write'
  | 'analytics:patients:read'
  | 'analytics:appointments:read'
  | 'analytics:medications:read'
  | 'analytics:compliance:read'
  | 'ai:clinical:read'
  | 'medications:interactions:read'
  | 'lab:results:read'
  | 'lab:results:write'
  | 'lab:integration:sync';

export interface RoleDefinition {
  role: UserRole;
  permissions: Permission[];
}

export const ROLE_DEFINITIONS: RoleDefinition[] = [
  {
    role: 'admin',
    permissions: [
      'appointments:read',
      'appointments:write',
      'patients:read',
      'patients:write',
      'telehealth:link:create',
      'telehealth:reminder:send',
      'patient:preferences:read',
      'patient:preferences:write',
      'patient:anamnesis:read',
      'patient:anamnesis:write',
      'patient:anamnesis:decrypt:user',
      'patient:anamnesis:decrypt:admin',
      'settings:communications:read',
      'settings:communications:write',
      'patient:education:read',
      'patient:education:write',
      'patient:messages:read',
      'patient:messages:write',
      'analytics:patients:read',
      'analytics:appointments:read',
      'analytics:medications:read',
      'analytics:compliance:read',
      'ai:clinical:read',
      'medications:interactions:read',
      'lab:results:read',
      'lab:results:write',
      'lab:integration:sync'
    ]
  },
  {
    role: 'clinician',
    permissions: [
      'appointments:read',
      'appointments:write',
      'patients:read',
      'patients:write',
      'telehealth:link:create',
      'telehealth:reminder:send',
      'patient:preferences:read',
      'patient:preferences:write',
      'patient:anamnesis:read',
      'patient:anamnesis:write',
      'patient:anamnesis:decrypt:user',
      'settings:communications:read',
      'patient:education:read',
      'patient:education:write',
      'patient:messages:read',
      'patient:messages:write',
      'analytics:patients:read',
      'analytics:appointments:read',
      'analytics:medications:read',
      'ai:clinical:read',
      'medications:interactions:read',
      'lab:results:read',
      'lab:results:write'
    ]
  },
  {
    role: 'staff',
    permissions: [
      'appointments:read',
      'patients:read',
      'telehealth:link:create',
      'telehealth:reminder:send',
      'patient:preferences:read',
      'settings:communications:read',
      'patient:education:read',
      'patient:messages:read',
      'analytics:patients:read',
      'analytics:appointments:read',
      'lab:results:read'
    ]
  },
  {
    role: 'client',
    permissions: []
  }
];


