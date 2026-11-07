// Test Suite 1: Security, Encryption, Distributed Advisory Locking & Restoration Queue

require('dotenv').config({ path: require('path').resolve(__dirname, '../.env') });
const assert = require('assert');
const { encrypt, decrypt } = require('../src/security/encryption');
const { DistributedLock } = require('../src/db/lock');
const RestorationQueue = require('../src/auth/queue');
const { closePool } = require('../src/db/pool');

async function runSecurityLockingTests() {
    console.log('--- RUNNING TEST SUITE: SECURITY, LOCKING & QUEUE ---');

    // 1. Encryption roundtrip
    console.log('[1/4] Testing AES-256-GCM encryption roundtrip...');
    const originalText = JSON.stringify({ hello: 'baileys-persistence', time: Date.now() });
    const encrypted = encrypt(originalText);
    assert(encrypted.startsWith('v1:'), 'Ciphertext must start with v1: version prefix');
    const decrypted = decrypt(encrypted);
    assert.strictEqual(decrypted, originalText, 'Decrypted text must match original plaintext');
    console.log('   ✓ AES-256-GCM encryption and decryption roundtrip passed');

    // 2. Tamper detection
    console.log('[2/4] Testing tamper resistance...');
    const parts = encrypted.split(':');
    const tampered = `${parts[0]}:${parts[1]}:${parts[2]}:tampered_${parts[3]}`;
    assert.throws(
        () => decrypt(tampered),
        /Authentication tag verification failed|ERR_AUTH_FAILED/,
        'Tampered payload must be rejected'
    );
    console.log('   ✓ Tamper resistance and integrity verification passed');

    // 3. Distributed advisory locking
    console.log('[3/4] Testing PostgreSQL advisory lock isolation...');
    const testIntegrationId = 'a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d';
    const lockA = new DistributedLock(testIntegrationId);
    const lockB = new DistributedLock(testIntegrationId);

    const acquiredA = await lockA.acquire();
    assert.strictEqual(acquiredA, true, 'First lock instance must succeed');

    const acquiredB = await lockB.acquire();
    assert.strictEqual(acquiredB, false, 'Second concurrent lock for same integration must be blocked');

    await lockA.release();

    const acquiredBAfterRelease = await lockB.acquire();
    assert.strictEqual(acquiredBAfterRelease, true, 'Lock must be acquirable after previous release');
    await lockB.release();
    console.log('   ✓ Distributed advisory locking concurrency isolation passed');

    // 4. Restoration queue with bounded concurrency and exponential backoff
    console.log('[4/4] Testing RestorationQueue bounded concurrency & backoff...');
    const queue = new RestorationQueue({ concurrency: 2, maxRetries: 2, baseDelayMs: 50 });
    let activeMax = 0;
    let currentActive = 0;
    let retriedTaskAttempts = 0;

    const normalTask = () =>
        new Promise((resolve) => {
            currentActive++;
            activeMax = Math.max(activeMax, currentActive);
            setTimeout(() => {
                currentActive--;
                resolve('done');
            }, 50);
        });

    const retriedTask = () =>
        new Promise((resolve, reject) => {
            retriedTaskAttempts++;
            if (retriedTaskAttempts < 2) {
                reject(new Error('Simulated transient network drop'));
            } else {
                resolve('recovered');
            }
        });

    await Promise.all([
        queue.add(normalTask),
        queue.add(normalTask),
        queue.add(normalTask),
        queue.add(retriedTask)
    ]);

    assert(activeMax <= 2, `Active tasks (${activeMax}) exceeded maximum concurrency of 2`);
    assert(retriedTaskAttempts >= 2, 'Retried task must have attempted retry with backoff');
    console.log('   ✓ Restoration queue concurrency bounds and retry backoff passed');

    console.log('--- SECURITY, LOCKING & QUEUE SUITE PASSED ---\n');
}

if (require.main === module) {
    runSecurityLockingTests()
        .then(() => closePool())
        .catch((err) => {
            console.error('Test failed:', err);
            process.exit(1);
        });
}

module.exports = runSecurityLockingTests;
