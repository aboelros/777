// Test Suite 2: Supabase Baileys Auth State, Key Storage, Migration & Restart Simulation

require('dotenv').config({ path: require('path').resolve(__dirname, '../.env') });
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const { BufferJSON } = require('@whiskeysockets/baileys');
const { useSupabaseAuthState } = require('../src/auth/supabaseAuthState');
const { migrateFilesystemSession } = require('../src/auth/migration');
const { query, closePool } = require('../src/db/pool');

async function runAuthPersistenceTests() {
    console.log('--- RUNNING TEST SUITE: AUTH PERSISTENCE & RESTORATION ---');
    const testIntegrationId = uuidv4();
    const testProjectId = uuidv4();

    // 1. Initialize Auth State and Save Credentials
    console.log('[1/4] Testing useSupabaseAuthState and saveCreds()...');
    const authAdapter = await useSupabaseAuthState(testIntegrationId, testProjectId);
    assert(authAdapter.state.creds, 'Credentials must be initialized');
    authAdapter.state.creds.me = { id: '201000000000@s.whatsapp.net', name: 'Automio Test' };
    await authAdapter.saveCreds();

    const dbCheck = await query(
        'SELECT auth_valid, version, session_status FROM whatsapp_gateway_sessions WHERE integration_id = $1',
        [testIntegrationId]
    );
    assert.strictEqual(dbCheck.rows.length, 1, 'Session record must exist in DB');
    assert.strictEqual(dbCheck.rows[0].auth_valid, true, 'auth_valid must be true');
    assert.strictEqual(dbCheck.rows[0].version, 2, 'Version must increment on saveCreds');
    console.log('   ✓ Credentials persisted and versioned in Supabase');

    // 2. Granular Signal Key Storage (set, get, delete)
    console.log('[2/4] Testing granular Signal keys batching and deletion...');
    const testKeyData = {
        'pre-key': {
            '1': { keyPair: { public: Buffer.from('test-pub-key'), private: Buffer.from('test-priv-key') } },
            '2': { keyPair: { public: Buffer.from('test-pub-2'), private: Buffer.from('test-priv-2') } }
        },
        'session': {
            'sess-001': { cipher: 'test-cipher-data' }
        }
    };
    await authAdapter.state.keys.set(testKeyData);

    const fetchedPreKeys = await authAdapter.state.keys.get('pre-key', ['1', '2', '3']);
    assert(fetchedPreKeys['1'] && Buffer.isBuffer(fetchedPreKeys['1'].keyPair.public), 'Key 1 must be revived with Buffer');
    assert(fetchedPreKeys['2'], 'Key 2 must be present');
    assert.strictEqual(fetchedPreKeys['3'], null, 'Non-existent key must return null');

    // Test Key Deletion
    await authAdapter.state.keys.set({
        'pre-key': { '2': null }
    });
    const fetchedAfterDelete = await authAdapter.state.keys.get('pre-key', ['2']);
    assert.strictEqual(fetchedAfterDelete['2'], null, 'Deleted key must return null');
    console.log('   ✓ Signal keys batch write, revival, and deletion passed');

    // 3. Filesystem Session Migration Helper
    console.log('[3/4] Testing filesystem to Supabase migration helper...');
    const mockFsSessionDir = path.resolve(__dirname, '../scratch_test_sessions');
    const mockSessionId = uuidv4();
    const mockDir = path.join(mockFsSessionDir, mockSessionId);
    fs.mkdirSync(mockDir, { recursive: true });

    const mockCreds = { accountSyncCounter: 1, myAppStateKeyId: 'key-1' };
    fs.writeFileSync(path.join(mockDir, 'creds.json'), JSON.stringify(mockCreds, BufferJSON.replacer));
    fs.writeFileSync(
        path.join(mockDir, 'pre-key-10.json'),
        JSON.stringify({ keyPair: { public: Buffer.from('mock-pub') } }, BufferJSON.replacer)
    );

    const migResult = await migrateFilesystemSession(mockFsSessionDir, mockSessionId, testProjectId);
    assert.strictEqual(migResult.migrated, true, 'Migration must succeed');
    assert(migResult.migratedKeys >= 1, 'At least 1 key must be migrated');
    assert(fs.existsSync(path.join(mockDir, 'creds.json')), 'Local creds must be preserved');

    // Verify migrated session in DB
    const migAuth = await useSupabaseAuthState(mockSessionId, testProjectId);
    assert.strictEqual(migAuth.state.creds.myAppStateKeyId, 'key-1', 'Migrated creds must match in Supabase');
    const migKeys = await migAuth.state.keys.get('pre-key', ['10']);
    assert(migKeys['10'], 'Migrated key must be retrievable from Supabase');
    fs.rmSync(mockFsSessionDir, { recursive: true, force: true });
    console.log('   ✓ Filesystem migration verified without deleting local files');

    // 4. Temporary Disconnect vs Explicit Logout
    console.log('[4/4] Testing temporary disconnect vs explicit logout...');
    // Temporary disconnect
    await authAdapter.markSessionStatus('disconnected');
    const statusCheck = await query(
        'SELECT auth_valid, session_status FROM whatsapp_gateway_sessions WHERE integration_id = $1',
        [testIntegrationId]
    );
    assert.strictEqual(statusCheck.rows[0].session_status, 'disconnected');
    assert.strictEqual(statusCheck.rows[0].auth_valid, true, 'auth_valid must remain true on disconnect');

    // Explicit logout
    await authAdapter.invalidateAuth();
    const logoutCheck = await query(
        'SELECT auth_valid, session_status FROM whatsapp_gateway_sessions WHERE integration_id = $1',
        [testIntegrationId]
    );
    assert.strictEqual(logoutCheck.rows[0].auth_valid, false, 'auth_valid must be false on explicit logout');

    const keysLeft = await query(
        'SELECT COUNT(*) as count FROM whatsapp_gateway_keys WHERE integration_id = $1',
        [testIntegrationId]
    );
    assert.strictEqual(parseInt(keysLeft.rows[0].count, 10), 0, 'Keys must be deleted on explicit logout');

    // Cleanup test records
    await query('DELETE FROM whatsapp_gateway_sessions WHERE integration_id = ANY($1)', [
        [testIntegrationId, mockSessionId]
    ]);
    console.log('   ✓ Disconnect vs Logout distinction verified');

    console.log('--- AUTH PERSISTENCE & RESTORATION SUITE PASSED ---\n');
}

if (require.main === module) {
    runAuthPersistenceTests()
        .then(() => closePool())
        .catch((err) => {
            console.error('Test failed:', err);
            process.exit(1);
        });
}

module.exports = runAuthPersistenceTests;
