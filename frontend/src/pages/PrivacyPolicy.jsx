import React from 'react';
import { motion } from 'framer-motion';

const PrivacyPolicy = () => {
    return (
        <div className="min-h-screen bg-gray-900 text-white p-8 font-sans">
            <div className="max-w-4xl mx-auto">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                >
                    <h1 className="text-4xl font-bold mb-8 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600">
                        Privacy Policy
                    </h1>

                    <div className="space-y-6 text-gray-300">
                        <p className="text-sm text-gray-500">Last Updated: December 17, 2025</p>

                        <section>
                            <h2 className="text-2xl font-semibold text-white mb-3">1. Introduction</h2>
                            <p>
                                Welcome to AI Sales Commander ("we," "our," or "us"). We are committed to protecting your privacy and ensuring the security of your personal information. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our application and services, including our integration with Meta Platforms (Facebook, Instagram, Messenger, WhatsApp).
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold text-white mb-3">2. Information We Collect</h2>
                            <p className="mb-2">We collect information that you provide directly to us and information automatically collected when you use our services:</p>
                            <ul className="list-disc pl-5 space-y-2">
                                <li><strong>Account Information:</strong> Name, email address, and business details provided during registration.</li>
                                <li><strong>Meta Platform Data:</strong> When you connect your Facebook Pages, Instagram Business accounts, or WhatsApp accounts, we receive public profile information, messages, comments, and posts as authorized by you via Meta's permissions system.</li>
                                <li><strong>Communication Data:</strong> Content of messages sent and received through our platform for the purpose of automation and management.</li>
                                <li><strong>Usage Data:</strong> Information about how you interact with our dashboard and services.</li>
                            </ul>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold text-white mb-3">3. How We Use Your Information</h2>
                            <p className="mb-2">We use the collected information for the following purposes:</p>
                            <ul className="list-disc pl-5 space-y-2">
                                <li>To provide, operate, and maintain our AI Sales Commander services.</li>
                                <li>To automate responses to customer inquiries on your behalf using AI.</li>
                                <li>To manage and organize your customer interactions across different platforms.</li>
                                <li>To improve our AI models and service quality (using anonymized data).</li>
                                <li>To communicate with you about updates, security alerts, and support.</li>
                            </ul>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold text-white mb-3">4. Data Sharing and Disclosure</h2>
                            <p>
                                We do not sell your personal data. We may share your information with:
                            </p>
                            <ul className="list-disc pl-5 space-y-2 mt-2">
                                <li><strong>Service Providers:</strong> Third-party vendors who perform services on our behalf (e.g., cloud hosting, AI processing).</li>
                                <li><strong>Legal Requirements:</strong> If required to do so by law or in response to valid requests by public authorities.</li>
                            </ul>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold text-white mb-3">5. Data Security</h2>
                            <p>
                                We implement appropriate technical and organizational security measures to protect your data. However, please note that no method of transmission over the Internet is 100% secure.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold text-white mb-3">6. Your Rights</h2>
                            <p>
                                You have the right to access, correct, or delete your personal information. You can manage your connected accounts and data directly within the application settings or by contacting us.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold text-white mb-3">7. Contact Us</h2>
                            <p>
                                If you have any questions about this Privacy Policy, please contact us at: support@aisalescommander.com
                            </p>
                        </section>
                    </div>
                </motion.div>
            </div>
        </div>
    );
};

export default PrivacyPolicy;
