// No look-alike characters (0/O, 1/l/I): temporary passwords get read out or typed from a message.
const ALPHABET = "abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789";

export const MIN_PASSWORD_LENGTH = 8;

export function generatePassword(length = 12): string {
  const limit = 256 - (256 % ALPHABET.length);
  let password = "";
  while (password.length < length) {
    for (const byte of crypto.getRandomValues(new Uint8Array(length))) {
      // Rejecting the uneven remainder keeps every character equally likely.
      if (byte < limit && password.length < length) password += ALPHABET[byte % ALPHABET.length];
    }
  }
  return password;
}
