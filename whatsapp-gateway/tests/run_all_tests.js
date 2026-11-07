// Master Test Runner for WhatsApp Gateway Auth Persistence

const runSecurityLockingTests = require('./test_security_locking');
const runAuthPersistenceTests = require('./test_auth_persistence');
const { closePool } = require('../src/db/pool');

async function main() {
    console.log('====================================================');
    console.log('   WHATSAPP GATEWAY AUTH PERSISTENCE TEST RUNNER    ');
    console.log('====================================================\n');

    try {
        await runSecurityLockingTests();
        await runAuthPersistenceTests();
        console.log('====================================================');
        console.log('   ALL AUTH PERSISTENCE SUITES PASSED (8/8 TESTS)   ');
        console.log('====================================================\n');
    } catch (err) {
        console.error('Test Suite Failed:', err);
        process.exit(1);
    } finally {
        await closePool();
    }
}

if (require.main === module) {
    main();
}

module.exports = main;
