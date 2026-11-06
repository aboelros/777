import React from 'react';
import { motion } from 'framer-motion';

/**
 * TermsOfService Component
 * Renders the public Terms of Service page required for platform compliance
 * and Meta App Review verification.
 */
const TermsOfService = () => {
    return (
        <div className="min-h-screen bg-gray-900 text-white p-8 font-sans">
            <div className="max-w-4xl mx-auto">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                >
                    <h1 className="text-4xl font-bold mb-8 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-sky-600">
                        Terms of Service
                    </h1>

                    <div className="space-y-6 text-gray-300 leading-relaxed">
                        <p className="text-sm text-gray-500">Last Updated: January 1, 2026</p>

                        <section>
                            <h2 className="text-2xl font-semibold text-white mb-3">1. Acceptance of Terms</h2>
                            <p>
                                By accessing or using the Automio platform ("Service", "we", "our", or "us"), you agree to be bound by these Terms of Service. If you do not agree to these terms, you may not access or use the Service.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold text-white mb-3">2. Description of Service</h2>
                            <p>
                                Automio provides an enterprise-grade AI sales acceleration, omnichannel conversation triage, customer support automation, and social media engagement platform for businesses, e-commerce stores, and merchants.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold text-white mb-3">3. Third-Party Integrations and Meta Platform Terms</h2>
                            <p className="mb-2">
                                When connecting third-party platforms—including Meta Platforms, Inc. services (Facebook Pages, Instagram Professional Accounts, Messenger, and WhatsApp Business API)—you agree to:
                            </p>
                            <ul className="list-disc pl-5 space-y-2">
                                <li>Comply with Meta's Commercial Terms, Developer Policies, and Community Standards.</li>
                                <li>Authorize Automio to access, read, and dispatch messages and public comments strictly within the scope of permissions explicitly granted during OAuth authorization.</li>
                                <li>Maintain valid administrative rights over any connected Facebook Page, Instagram account, or WhatsApp Business account.</li>
                            </ul>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold text-white mb-3">4. User Accounts and Security</h2>
                            <p>
                                You are responsible for safeguarding the credentials associated with your account and for all activities that occur under your account. You agree to notify us immediately of any unauthorized access or security breach.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold text-white mb-3">5. Acceptable Use Policy</h2>
                            <p className="mb-2">You agree not to use the Service to:</p>
                            <ul className="list-disc pl-5 space-y-2">
                                <li>Send unsolicited marketing messages, spam, or abusive communications.</li>
                                <li>Violate intellectual property, privacy, or consumer protection laws.</li>
                                <li>Interfere with, disrupt, or place unreasonable load on third-party APIs or infrastructure.</li>
                            </ul>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold text-white mb-3">6. Intellectual Property</h2>
                            <p>
                                All software, algorithms, designs, trademarks, and documentation provided as part of the Service remain the exclusive property of Automio and its licensors. You retain all ownership rights to your business data and customer content.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold text-white mb-3">7. Limitation of Liability</h2>
                            <p>
                                To the maximum extent permitted by applicable law, Automio shall not be liable for any indirect, incidental, special, consequential, or punitive damages resulting from your use of or inability to use the Service.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold text-white mb-3">8. Contact Information</h2>
                            <p>
                                For questions, legal notices, or inquiries regarding these Terms of Service, please contact us at:
                            </p>
                            <p className="mt-2 text-sky-400 font-mono">
                                legal@automio.online
                            </p>
                        </section>
                    </div>
                </motion.div>
            </div>
        </div>
    );
};

export default TermsOfService;
