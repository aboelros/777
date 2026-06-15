/**
 * Test Script - Verify Baileys Connection & Pairing Code
 * Run with: node test_baileys.js
 */

const { default: makeWASocket, useMultiFileAuthState, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const pino = require('pino');
const fs = require('fs');

async function startTest() {
    console.log('🚀 Starting Baileys Test...');

    // 1. Setup Auth
    const sessionDir = './test_session';
    if (!fs.existsSync(sessionDir)) {
        fs.mkdirSync(sessionDir, { recursive: true });
    }
    const { state, saveCreds } = await useMultiFileAuthState(sessionDir);
    const { version } = await fetchLatestBaileysVersion();

    console.log(`📦 Baileys Version: ${version.join('.')}`);

    // 2. Create Socket
    const sock = makeWASocket({
        version,
        auth: state,
        printQRInTerminal: true, // Print QR to console to verify generation
        logger: pino({ level: 'silent' }),
        browser: ['Chrome (Linux)', '', ''],
        connectTimeoutMs: 60000,
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            console.log('\n✅ QR Code Generated!');
            console.log('Scan this to test QR flow (or wait for pairing code test below)');
        }

        if (connection === 'close') {
            console.log('❌ Connection Closed:', lastDisconnect?.error?.message);
        } else if (connection === 'open') {
            console.log('✅ Connection Opened Successfully!');
        }
    });

    // 3. Test Pairing Code (Optional - Uncomment to test)
    // const phoneNumber = '628123456789'; // REPLACE WITH REAL NUMBER TO TEST
    // console.log(`\nTesting Pairing Code for ${phoneNumber}...`);
    // setTimeout(async () => {
    //     try {
    //         const code = await sock.requestPairingCode(phoneNumber);
    //         console.log(`✅ Pairing Code Generated: ${code}`);
    //     } catch (err) {
    //         console.error('❌ Pairing Code Failed:', err.message);
    //     }
    // }, 5000);
}

startTest();
