import crypto from 'crypto';

export interface WrappedKey {
  wrappedKeyB64: string;
  ivB64: string;
  saltB64?: string; // only for user-wrapped
}

export interface EncryptedAnamnesis {
  version: number;
  ciphertextB64: string;
  ivB64: string;
  userWrap: WrappedKey; // unwrap with user passphrase
  adminWrap?: WrappedKey; // unwrap with admin master key
}

function aesGcmEncrypt(key: Buffer, plaintext: Buffer) {
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
  const ciphertext = Buffer.concat([cipher.update(plaintext), cipher.final()]);
  const tag = cipher.getAuthTag();
  return { iv, ciphertext: Buffer.concat([ciphertext, tag]) };
}

function aesGcmDecrypt(key: Buffer, iv: Buffer, ciphertextWithTag: Buffer) {
  const tag = ciphertextWithTag.subarray(ciphertextWithTag.length - 16);
  const ciphertext = ciphertextWithTag.subarray(0, ciphertextWithTag.length - 16);
  const decipher = crypto.createDecipheriv('aes-256-gcm', key, iv);
  decipher.setAuthTag(tag);
  const plaintext = Buffer.concat([decipher.update(ciphertext), decipher.final()]);
  return plaintext;
}

function deriveKeyFromPassphrase(passphrase: string, salt: Buffer): Buffer {
  return crypto.pbkdf2Sync(passphrase, salt, 100_000, 32, 'sha256');
}

function getAdminMasterKey(): Buffer | null {
  const keyB64 = process.env.ADMIN_KMS_KEY_B64;
  if (!keyB64) return null;
  const raw = Buffer.from(keyB64, 'base64');
  if (raw.length === 32) return raw;
  // normalize to 32 bytes via hash if needed
  return crypto.createHash('sha256').update(raw).digest();
}

export function encryptAnamnesis(plaintext: string, userPassphrase: string): EncryptedAnamnesis {
  const dataKey = crypto.randomBytes(32);
  const { iv: dataIv, ciphertext } = aesGcmEncrypt(dataKey, Buffer.from(plaintext, 'utf8'));

  // user wrap
  const saltU = crypto.randomBytes(16);
  const userKey = deriveKeyFromPassphrase(userPassphrase, saltU);
  const { iv: ivU, ciphertext: wrappedU } = aesGcmEncrypt(userKey, dataKey);

  const adminKey = getAdminMasterKey();
  let adminWrap: WrappedKey | undefined;
  if (adminKey) {
    const { iv: ivA, ciphertext: wrappedA } = aesGcmEncrypt(adminKey, dataKey);
    adminWrap = {
      wrappedKeyB64: wrappedA.toString('base64'),
      ivB64: ivA.toString('base64')
    };
  }

  return {
    version: 1,
    ciphertextB64: ciphertext.toString('base64'),
    ivB64: dataIv.toString('base64'),
    userWrap: {
      wrappedKeyB64: wrappedU.toString('base64'),
      ivB64: ivU.toString('base64'),
      saltB64: saltU.toString('base64')
    },
    adminWrap
  };
}

export function decryptAnamnesisWithPassphrase(payload: EncryptedAnamnesis, passphrase: string): string {
  const salt = Buffer.from(payload.userWrap.saltB64 || '', 'base64');
  const userKey = deriveKeyFromPassphrase(passphrase, salt);
  const wrapped = Buffer.from(payload.userWrap.wrappedKeyB64, 'base64');
  const ivU = Buffer.from(payload.userWrap.ivB64, 'base64');
  const dataKey = aesGcmDecrypt(userKey, ivU, wrapped);
  const ivData = Buffer.from(payload.ivB64, 'base64');
  const ciphertext = Buffer.from(payload.ciphertextB64, 'base64');
  const plain = aesGcmDecrypt(dataKey, ivData, ciphertext);
  return plain.toString('utf8');
}

export function decryptAnamnesisAsAdmin(payload: EncryptedAnamnesis): string {
  const adminKey = getAdminMasterKey();
  if (!adminKey || !payload.adminWrap) throw new Error('Admin key not configured');
  const wrapped = Buffer.from(payload.adminWrap.wrappedKeyB64, 'base64');
  const ivA = Buffer.from(payload.adminWrap.ivB64, 'base64');
  const dataKey = aesGcmDecrypt(adminKey, ivA, wrapped);
  const ivData = Buffer.from(payload.ivB64, 'base64');
  const ciphertext = Buffer.from(payload.ciphertextB64, 'base64');
  const plain = aesGcmDecrypt(dataKey, ivData, ciphertext);
  return plain.toString('utf8');
}





