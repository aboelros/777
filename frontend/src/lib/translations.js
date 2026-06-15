import useThemeStore from '../store/themeStore';

const translations = {
    en: {
        common: {
            dashboard: "Dashboard",
            settings: "Settings",
            save: "Save",
            cancel: "Cancel",
            search: "Search...",
            active: "Active",
            loading: "Loading...",
            actions: "Actions",
            create: "Create",
            edit: "Edit",
            delete: "Delete",
            view: "View",
            status: "Status",
            date: "Date",
            submit: "Submit",
            back: "Back",
            next: "Next",
            confirm: "Confirm",
            yesterday: "yesterday"
        },
        sidebar: {
            dashboard: "Dashboard",
            projects: "Projects",
            integrations: "Integrations",
            pipeline: "Pipeline",
            ai_assistant: "AI Assistant",
            orders: "Orders",
            inbox: "Inbox",
            products: "Products",
            training: "Bot Training",
            social: "Social Media",
            campaigns: "Campaigns",
            payments: "Payments & Invoicing",
            reports: "Reports",
            usage: "Usage",
            subscription: "Subscription",
            settings: "Settings",
            about: "About"
        },
        auth: {
            welcome: "Welcome Back",
            subtitle: "Sign in to your account",
            email: "Email Address",
            password: "Password",
            login: "Sign In",
            forgot_password: "Forgot Password?",
            no_account: "Don't have an account?",
            sign_up: "Sign Up"
        },
        dashboard: {
            title: "Dashboard",
            welcome: "Welcome back",
            welcome_subtitle: "Here's what's happening with your sales.",
            overview: "Overview",
            active_projects: "Active Projects",
            total_revenue: "Total Revenue",
            total_orders: "Total Orders",
            messages: "Messages",
            unread: "unread",
            products: "Products",
            in_stock: "in stock",
            out_of_stock: "out of stock",
            pending_orders: "Pending Orders",
            ai_efficiency: "AI Efficiency",
            recent_activity: "Recent Activity",
            quick_actions: "Quick Actions",
            new_project: "New Project",
            connect_channel: "Connect Channel",
            revenue_overview: "Revenue Overview",
            message_activity: "Message Activity",
            last_7_days: "Last 7 days",
            meta_engagement: "Meta Engagement",
            active_integrations: "Active Integrations",
            integration_status: "Integration Status",
            product_inventory: "Product Inventory",
            no_social: "No social connection",
            operational: "All systems operational",
            active_count: "active"
        },
        projects: {
            title: "Projects",
            description: "Manage your business units and configurations.",
            create_new: "Create Project",
            no_projects: "No projects found. Create one to get started.",
            active: "Active",
            created: "Created",
            switched_to: "Switched to",
            current: "Current",
            switch: "Switch",
            delete_confirm_title: "Delete Project?",
            delete_confirm_desc: "Are you sure you want to delete this project? This action cannot be undone and will delete all associated data.",
            delete_success: "Project deleted successfully",
            delete_error: "Failed to delete project",
            creating: "Creating...",
            modal: {
                title: "Create New Project",
                subtitle: "Set up your new business project",
                name_label: "Project Name *",
                name_placeholder: "My Awesome Store",
                desc_label: "Description",
                desc_placeholder: "Brief description of your project...",
                timezone_label: "Timezone"
            },
            fields: {
                name: "Project Name",
                description: "Description",
                website: "Website URL",
                industry: "Industry"
            }
        },
        assistant: {
            title: "AI Assistant",
            subtitle: "Powered by Gemini 2.0 Flash • FREE • Context-Aware",
            placeholder: "Ask me anything about orders, customers, or sales...",
            suggested_actions: "Suggested Actions:",
            reasoning_engine: "Reasoning Engine",
            steps: {
                analyzing: "Analyzing request intent...",
                context: "Accessing business context...",
                formulating: "Formulating response..."
            },
            model_info: {
                title: "AI Model",
                model: "Model",
                temp: "Temperature",
                max_tokens: "Max Tokens",
                context: "Context Awareness",
                enabled: "Enabled"
            },
            business_context: {
                title: "Business Overview",
                project: "Project",
                total_messages: "Total Messages",
                unread_messages: "Unread Messages"
            },
            capabilities: {
                title: "AI Capabilities",
                analyze: "Analyze Sales Data",
                manage_orders: "Manage Orders",
                respond: "Respond to Customers",
                reports: "Generate Reports",
                follow_ups: "Schedule Follow-ups"
            },
            usage: {
                title: "Today's Usage",
                requests: "Requests",
                tokens: "Tokens",
                cost: "Est. Cost:"
            },
            suggestions: {
                show_sales: "Show me today's sales performance",
                list_orders: "List recent orders",
                summarize_unread: "Summarize unread messages",
                generate_report: "Generate weekly report",
                compare_sales: "Compare sales to last month",
                pending_orders: "Show pending orders",
                track_fulfillment: "Track order fulfillment",
                draft_responses: "Draft customer responses",
                urgent_messages: "Prioritize urgent messages",
                monthly_report: "Generate monthly report",
                customer_trends: "Analyze customer trends",
                export_csv: "Export data to CSV",
                customer_insights: "View customer insights",
                high_value: "Find high-value customers",
                feedback: "Review customer feedback"
            },
            welcome: {
                greeting: "Hi there! 👋 I'm your **AI Sales Assistant** - part of the AI Sales Commander platform.",
                what_i_am: "**🎯 What I Am:**",
                description: "I'm not just a chatbot - I'm your business intelligence partner built into this platform. I help you:",
                features: [
                    "Understand your sales data from Shopify and other integrations",
                    "Manage customer conversations from WhatsApp, Instagram, Facebook",
                    "Generate and interpret business reports",
                    "Navigate and use this platform effectively",
                    "Make data-driven decisions to grow your business"
                ],
                your_business: "**📊 Your Business:**",
                how_it_works: "**🔗 How This Platform Works:**",
                step1: "**1. Connect Integrations** (Data IN)",
                step1_desc: "   → Shopify brings your orders and sales\n   → WhatsApp/Instagram/Facebook bring customer messages\n   → All data flows into ONE central hub",
                step2: "**2. Manage Daily Operations** (Work FASTER)",
                step2_desc: "   → Dashboard shows everything at a glance\n   → Orders page has all orders from all channels\n   → Messages page has ALL conversations in one inbox\n   → I help you prioritize and respond",
                step3: "**3. Generate Insights** (Data OUT)",
                step3_desc: "   → Reports analyze your performance\n   → I explain what the numbers mean\n   → We identify opportunities together\n   → Your business grows! 📈",
                quick_start: "**💡 Quick Start Guide:**",
                ready: "**🚀 I'm Ready to Help!**",
                footer: "Click a suggested action below or ask me anything about your business. I understand the complete flow from integrations → platform → reports → insights."
            }
        },
        deals: {
            title: "Sales Pipeline",
            description: "Track leads and manage deals.",
            new_deal: "New Deal",
            filter: "Filter",
            move_error: "Failed to move deal",
            no_stages: "No pipeline stages found.",
            configure_pipeline: "Configure Pipeline",
            add_deal: "Add Deal",
            lead: "Lead",
            stages: {
                new_lead: "New Lead",
                contacted: "Contacted",
                qualified: "Qualified",
                proposal: "Proposal",
                negotiation: "Negotiation",
                won: "Won",
                lost: "Lost"
            },
            card: {
                value: "Value",
                probability: "Probability",
                expected: "Expected Close"
            }
        },
        integrations: {
            title: "Integrations",
            description: "Connect your sales channels and communication platforms to centralize your business operations.",
            refresh_identities: "Refresh Identities",
            terminal: "Webhook Terminal",
            connect: "Connect",
            connected: "Connected",
            disconnected: "Disconnected",
            pending: "Pending",
            syncing: "Syncing",
            error: "Error",
            sync: "Sync Now",
            verify: "Verify",
            delete_confirm: "Are you sure you want to delete this integration? This action cannot be undone.",
            setup_instructions: "Setup Instructions",
            connect_provider: "Connect {{name}}",
            save: "Save & Connect",
            cancel: "Cancel",
            status: "Status",
            sync_success: "Sync started successfully",
            delete_success: "Integration deleted successfully",
            verify_success: "Integration verified successfully!",
            connect_success: "Integration connected successfully!",
            qr_success: "Scan QR code to connect WhatsApp!",
            identities_success: "Successfully updated customer identities.",
            identities_up_to_date: "All customer identities are already up to date.",
            configure: "Configure",
            meta: "Connect Facebook & Instagram",
            whatsapp: "Connect WhatsApp",
            telegram: "Connect Telegram",
            tiktok: "Connect TikTok",
            discord: "Connect Discord",
            providers: {
                shopify: {
                    name: "Shopify",
                    description: "Sync orders and products from your Shopify store",
                    instructions: "1. Log into Shopify Admin\n2. Create a Develop App\n3. Configure Admin API scopes (read_orders, read_products)\n4. Copy API Key and Secret"
                },
                whatsapp: {
                    name: "WhatsApp",
                    description: "Connect via WhatsApp Business Cloud API or WA-Gateway",
                    instructions: "Official API: Use Phone Number ID and Token.\nWA-Gateway: Scan QR code via self-hosted server."
                },
                telegram: {
                    name: "Telegram",
                    description: "Connect your Telegram bot for customer communication",
                    instructions: "1. Create bot via @BotFather\n2. Get API Token\n3. Paste token here"
                },
                instagram: {
                    name: "Instagram",
                    description: "Manage Instagram Direct Messages and comments",
                    instructions: "Connect your Instagram Business account to manage DMs and comments."
                },
                facebook: {
                    name: "Facebook",
                    description: "Connect Facebook Messenger for customer support",
                    instructions: "Connect your Facebook Page to manage Messenger conversations."
                },
                tiktok: {
                    name: "TikTok",
                    description: "TikTok Shop and Business Messages integration",
                    instructions: "Connect your TikTok Shop to sync orders and messages."
                },
                discord: {
                    name: "Discord",
                    description: "AI-powered customer support via Discord server",
                    instructions: "1. Create App in Discord Developer Portal\n2. Get Bot Token"
                }
            },
            form: {
                shopify_url: "Shopify Store URL (e.g. mystore.myshopify.com)",
                api_key: "API Key / Phone Number ID",
                api_secret: "Admin API Access Token / Secret",
                webhook_url: "Webhook URL (Optional)",
                whatsapp_provider: "WhatsApp Provider",
                business_api: "WhatsApp Business API (Official)",
                go_whatsapp: "Go-WhatsApp (Self-Hosted)",
                phone_number: "Phone Number (with country code)",
                business_account_id: "Business Account ID",
                base_url: "WA-Gateway Base URL",
                session_id: "Session ID",
                page_id: "Facebook Page ID",
                app_id: "Facebook App ID",
                shop_id: "TikTok Shop ID",
                app_key: "TikTok App Key",
                app_secret: "TikTok App Secret",
                access_token: "TikTok Access Token",
                guild_id: "Discord Server ID"
            }
        },
        settings: {
            title: "Properties",
            general: "General",
            account: "Account",
            notifications: "Notifications",
            theme: "Appearance",
            language: "Language"
        },
        bot_training: {
            title: "Bot Training Center",
            subtitle: "Supercharge your AI with custom instructions and knowledge",
            tabs: {
                instructions: "AI Instructions",
                knowledge: "Knowledge Base (RAG)"
            },
            buttons: {
                auto_train: "Auto-Train AI",
                add_instruction: "Add Instruction",
                add_knowledge: "Add Knowledge",
                scrape_url: "Scrape URL",
                edit: "Edit",
                delete: "Delete",
                save: "Save changes",
                cancel: "Cancel",
                extract: "Extract Knowledge"
            },
            search_placeholder: "Search...",
            stats: {
                total_instructions: "Total Instructions",
                total_knowledge: "Total Knowledge",
                status: "Status",
                live: "Live & Syncing"
            },
            empty: {
                no_instructions: "No Instructions Found",
                no_knowledge: "Knowledge Base is Empty",
                add_instruction_desc: "Add instructions to teach your AI how to behave.",
                add_knowledge_desc: "Add business knowledge or FAQs to help the AI answer complex questions."
            },
            modals: {
                edit_instruction: "Edit Instruction",
                add_instruction: "Add Instruction",
                edit_knowledge: "Edit Knowledge",
                add_knowledge: "Add Knowledge",
                scrape_title: "Scrape URL",
                scrape_desc: "Enter a URL (FAQ page, guide, or documentation) to automatically extract content for your knowledge base.",
                fields: {
                    title: "Title",
                    instruction: "Instruction",
                    category: "Category",
                    priority: "Priority",
                    content: "Content",
                    website_url: "Website URL",
                    published: "Published & Active"
                }
            }
        },
        inbox: {
            title: "Inbox",
            subtitle: "Manage omni-channel communications with AI-assisted intelligence.",
            search_placeholder: "Search conversations...",
            tabs: {
                all: "All"
            },
            empty: {
                no_conversations: "No conversations found",
                select: "Select a Conversation",
                select_desc: "Select a conversation to view history, AI insights, and manage orders."
            },
            chat: {
                start_conversation: "Start a conversation",
                type_message: "Type a message...",
                input_placeholder: "Type your message...",
                ai_assistant: "AI Assistant",
                clear_chat: "Clear Chat",
                enable_ai: "Enable AI",
                disable_ai: "Disable AI",
                manual: "MANUAL",
                auto: "AUTO",
                vip_customer: "VIP Customer"
            }
        },
        orders: {
            title: "Order Management",
            subtitle: "Automatic order tracking and AI-powered processing",
            stats: {
                total_orders: "Total Orders",
                total_revenue: "Total Revenue",
                pending_orders: "Pending Orders",
                fulfillment_rate: "Fulfillment Rate"
            },
            search_placeholder: "Search orders by customer, email, or ID...",
            filters: {
                all: "All Orders",
                pending: "Pending",
                processing: "Processing",
                fulfilled: "Fulfilled",
                shipped: "Shipped",
                cancelled: "Cancelled"
            },
            table: {
                id: "Order ID",
                customer: "Customer",
                date: "Date",
                total: "Total",
                status: "Status",
                actions: "Actions"
            },
            empty: {
                title: "No orders found",
                subtitle: "Orders will appear here when customers make purchases"
            },
            actions: {
                view: "View Details",
                ai_process: "AI Process",
                fulfill: "Mark as Fulfilled",
                delete: "Delete Order",
                delete_confirm: "Are you sure you want to delete this order?"
            },
            details: {
                title: "Order Details",
                customer_info: "Customer Information",
                delivery_address: "Delivery Address",
                items: "Order Items",
                quantity: "Quantity"
            }
        },
        products: {
            title: "Product Catalog",
            subtitle: "Manage products for AI-powered responses",
            buttons: {
                bulk_upload: "Bulk Upload CSV",
                add_product: "Add Product",
                add_first: "Add Your First Product",
                cancel: "Cancel",
                save: "Create Product",
                update: "Update Product",
                delete_confirm: "Are you sure you want to delete this product?"
            },
            search_placeholder: "Search products by name, SKU, or description...",
            empty: {
                title: "No Products Yet",
                desc_search: "No products match your search",
                desc_empty: "Add products to train your AI assistant"
            },
            card: {
                in_stock: "In Stock",
                out_of_stock: "Out of Stock",
                view_storage: "View storage details",
                viewing_storage: "Viewing storage details",
                edit: "Edit",
                qty: "Qty",
                more: "more"
            },
            storage: {
                title: "Inventory Storage Details",
                empty_title: "No products yet",
                empty_desc: "Create a product to manage storage details.",
                select_product: "Select a product to manage storage.",
                current_qty: "Current Quantity",
                reorder_point: "Reorder Point",
                safety_stock: "Safety Stock",
                locations: "Storage Locations",
                notes: "Storage Notes",
                attachments: "Reference Files",
                select_prompt: "Select a product to view/edit storage details"
            },
            modal: {
                add_title: "Add New Product",
                edit_title: "Edit Product",
                fields: {
                    name: "Product Name",
                    description: "Description",
                    sku: "SKU",
                    category: "Category",
                    price: "Price",
                    currency: "Currency",
                    stock: "Stock",
                    in_stock: "In Stock",
                    tags: "Tags (comma-separated)",
                    keywords: "Keywords for AI (comma-separated)",
                    storage_locations: "Storage Locations",
                    storage_locations_hint: "Use \"|\" to separate multiple locations.",
                    reorder_point: "Reorder Point",
                    safety_stock: "Safety Stock",
                    storage_notes: "Storage Notes",
                    attachments: "Storage Attachments (comma-separated URLs)"
                }
            }
        },
        reports: {
            title: "Analytics & Reports",
            subtitle: "AI-powered insights and comprehensive analytics",
            cards: {
                escalations: "Support Escalations",
                escalations_desc: "Requires human attention today",
                sales: "Today's Sales",
                sales_desc: "Real-time revenue",
                vs_yesterday: "vs yesterday",
                performance: "Performance Overview",
                week_revenue: "This Week Revenue",
                last_week_revenue: "Last Week Revenue",
                month_revenue: "This Month Revenue",
                month_escalations: "Escalations (Month)"
            },
            types: {
                sales: "Sales Analytics",
                sales_desc: "Revenue, orders, and performance metrics",
                orders: "Order Tracking",
                orders_desc: "Order fulfillment and tracking analytics",
                customers: "Customer Engagement",
                customers_desc: "Customer behavior and sentiment analysis",
                performance: "System Performance",
                performance_desc: "AI automation and system metrics",
                roi: "ROI Analysis",
                roi_desc: "Return on investment for AI automation"
            },
            controls: {
                generate: "Generate AI Report",
                generating: "Generating...",
                ranges: {
                    last_7: "Last 7 Days",
                    last_30: "Last 30 Days",
                    last_month: "Last Month"
                }
            },
            charts: {
                revenue: "Revenue Trend",
                status: "Order Status Distribution",
                channel: "Channel Usage",
                ai: "AI Automation"
            },
            insights: {
                title: "AI-Powered Insights",
                trends: "Key Trends",
                recommendations: "Recommendations"
            },
            empty: {
                title: "No Report Generated Yet",
                desc: "Select a report type and click \"Generate AI Report\" to create comprehensive analytics",
                button: "Generate First Report"
            },
            summary: {
                total_orders: "Total Orders",
                total_revenue: "Total Revenue",
                average_order_value: "Avg Order Value",
                total_messages: "Total Messages",
                inbound_messages: "Inbound",
                outbound_messages: "Outbound",
                ai_generated_messages: "AI Generated",
                automation_rate: "Automation Rate",
                total_tokens: "Total Tokens",
                total_cost_usd: "Total AI Cost",
                average_cost_per_message: "Avg Cost/Msg",
                revenue_per_message: "Revenue/Msg",
                ai_cost_per_order: "AI Cost/Order"
            }
        },
        campaigns: {
            title: "Drip Campaigns",
            subtitle: "Automate customer journeys with timed message sequences.",
            new: "New Campaign",
            empty: "No campaigns found. Create a new one to get started.",
            status: {
                active: "Active",
                paused: "Paused",
                steps: "Steps"
            },
            builder: {
                title: "Campaign Builder",
                name: "Campaign Name",
                trigger: "Trigger Type",
                add_step: "Add Step",
                save: "Save Campaign"
            }
        },
        payments: {
            title: "Payments & Invoicing",
            subtitle: "Manage billing and create quick payment links.",
            new_invoice: "New Invoice",
            quick_link: "Quick Link",
            table: {
                invoice_num: "Invoice #",
                customer: "Customer",
                amount: "Amount",
                status: "Status",
                date: "Date",
                actions: "Actions",
                empty: "No invoices found. Create a quick link or a new invoice."
            },
            modal: {
                title: "Create Payment Link",
                amount: "Amount (USD)",
                description: "Description",
                generate: "Generate Link",
                copy: "Copy",
                open: "Open",
                close: "Close",
                success: "Payment link created!",
                copied: "Copied to clipboard"
            }
        },
        subscription: {
            title: "Subscription Plans",
            headline: "Choose Your Perfect Plan",
            subheadline: "Scale your business with AI-powered automation. From startups to enterprises.",
            billing: {
                monthly: "Monthly",
                annually: "Annually",
                save: "Save 17%"
            },
            current: {
                title: "Current Plan",
                usage_monthly: "Monthly Usage",
                messages: "Messages",
                orders: "Orders",
                ai_requests: "AI Requests"
            },
            cards: {
                popular: "MOST POPULAR",
                mo: "/mo",
                yr: "/yr",
                save_amount: "Save {amount} ({percent}%)",
                more_features: "+{count} more features",
                buttons: {
                    current: "Current Plan",
                    start: "Get Started",
                    upgrade: "Upgrade Now"
                }
            },
            comparison: {
                title: "Compare Features Across All Plans",
                header_feature: "Feature",
                features: {
                    projects: "Projects",
                    messages: "Messages/month",
                    orders: "Orders/month",
                    ai_requests: "AI Requests/month",
                    integrations: "Integrations",
                    storage: "Storage",
                    team_members: "Team Members",
                    ai_automation: "AI Automation",
                    advanced_reports: "Advanced Reports",
                    social_media: "Social Media Management",
                    memory: "Conversation Memory",
                    order_auto: "Order Automation",
                    api: "API Access",
                    white_label: "White Label",
                    custom_ai: "Custom AI Models"
                },
                unlimited: "Unlimited"
            },
            faq: {
                title: "Questions?",
                desc: "Need help choosing the right plan? Contact our support team.",
                contact: "Contact Sales",
                docs: "View Documentation"
            },
            states: {
                loading: "Loading subscription plans...",
                error: "Failed to Load",
                retry: "Try Again"
            }
        },
        social: {
            title: "Social Hub",
            subtitle: "Manage all your social presence in one place",
            tabs: {
                feed: "Social Feed",
                comments: "Customer Comments"
            },
            stats: {
                comments: "Total Comments",
                pending: "Pending",
                responded: "Responded",
                rate: "Response Rate"
            },
            filters: {
                platform: "Platform",
                status: "Status",
                all_platforms: "All Platforms",
                all_status: "All Status",
                pending: "Pending",
                responded: "Responded"
            },
            feed: {
                no_items: "No Feed Items",
                connect_hint: "Connect a Meta account to see your feed",
                loading: "Loading social feed...",
                view_details: "View Details",
                manage_comments: "Manage Comments",
                view_on: "View on {platform}",
                likes: "Likes",
                comments: "Comments"
            },
            comments: {
                no_comments: "No Comments Yet",
                hint: "Comments from social media will appear here",
                loading: "Loading comments...",
                intent: "Intent",
                response: "Response",
                sent: "Sent",
                generate: "Generate AI Response",
                generating: "Generating...",
                reply_modal: "Generated Response:\n\n{response}\n\nSend this response?"
            },
            accounts: {
                all: "All Accounts",
                unnamed: "Unnamed Account",
                id: "ID"
            },
            drawer: {
                title: "Post Details",
                no_media: "No Media",
                view_original: "View Original",
                likes: "Likes",
                comments: "Comments",
                thread: "Comments Thread",
                no_thread: "No comments to display",
                generate_reply: "Generate Reply",
                thinking: "Thinking..."
            }
        },
        predictive: {
            title: "Predictive Nexus",
            subtitle: "AI-driven forecasting and behavioral modeling engine.",
            confidence: "Model Confidence",
            metrics: {
                projection: "30-Day Projection",
                churn_risk: "High Churn Risk",
                conversion: "Predicted Conversion",
                risk_score: "Risk Score",
                potential_loss: "Potential Loss",
                vs_baseline: "vs baseline"
            },
            charts: {
                revenue: "Revenue Trajectory"
            },
            risks: {
                title: "Retention Alerts",
                view_all: "View All Risks"
            },
            recommendations: {
                title: "Strategic Next Sets",
                top_opportunity: "Top Opportunity",
                execute: "Execute Strategy"
            }
        },
        smart_signals: {
            title: "Smart Signals",
            live_analysis: "Live Analysis",
            scanning: "Scanning Data Streams...",
            signals_feed: "Signals Feed",
            signals: {
                revenue_velocity: {
                    title: "Revenue Velocity",
                    message: "Projected turnover +12% vs. baseline. High-value cohorts active."
                },
                anomaly: {
                    title: "Anomaly Detected",
                    message: "DM volume deviation (+3σ). Support intervention recommended."
                },
                conversion: {
                    title: "Conversion Signal",
                    message: "\"Premium\" intent detected in 8 active sessions. Auto-engage?"
                },
                system: {
                    title: "System Integrity",
                    message: "All APIs operational. 99.9% uptime maintained during peak load."
                }
            }
        }
    },
    ar: {
        common: {
            dashboard: "لوحة التحكم",
            settings: "الإعدادات",
            save: "حفظ",
            cancel: "إلغاء",
            search: "بحث...",
            active: "نشط",
            loading: "جاري التحميل...",
            actions: "إجراءات",
            create: "إنشاء",
            edit: "تعديل",
            delete: "حذف",
            view: "عرض",
            status: "الحالة",
            date: "التاريخ",
            submit: "إرسال",
            back: "رجوع",
            next: "التالي",
            confirm: "تأكيد",
            yesterday: "أمس"
        },
        sidebar: {
            dashboard: "لوحة التحكم",
            projects: "المشاريع",
            integrations: "التكاملات",
            pipeline: "المبيعات",
            ai_assistant: "مساعد الذكاء الاصطناعي",
            orders: "الطلبات",
            inbox: "البريد الوارد",
            products: "المنتجات",
            training: "تدريب البوت",
            social: "التواصل الاجتماعي",
            campaigns: "الحملات",
            payments: "المدفوعات والفواتير",
            reports: "التقارير",
            usage: "الاستهلاك",
            subscription: "الاشتراك",
            settings: "الإعدادات",
            about: "حول التطبيق"
        },
        auth: {
            welcome: "مرحباً بعودتك",
            subtitle: "سجل الدخول إلى حسابك",
            email: "البريد الإلكتروني",
            password: "كلمة المرور",
            login: "تسجيل الدخول",
            forgot_password: "نسيت كلمة المرور؟",
            no_account: "ليس لديك حساب؟",
            sign_up: "إنشاء حساب"
        },
        dashboard: {
            title: "لوحة التحكم",
            welcome: "مرحباً بعودتك",
            welcome_subtitle: "إليك ما يحدث في مبيعاتك اليوم.",
            overview: "نظرة عامة",
            active_projects: "المشاريع النشطة",
            total_revenue: "إجمالي الإيرادات",
            total_orders: "إجمالي الطلبات",
            messages: "الرسائل",
            unread: "غير مقروءة",
            products: "المنتجات",
            in_stock: "في المخزن",
            out_of_stock: "نفذت الكمية",
            pending_orders: "طلبات معلقة",
            ai_efficiency: "كفاءة الذكاء الاصطناعي",
            recent_activity: "النشاط الأخير",
            quick_actions: "إجراءات سريعة",
            new_project: "مشروع جديد",
            connect_channel: "ربط قناة",
            revenue_overview: "نظرة عامة على الإيرادات",
            message_activity: "نشاط الرسائل",
            last_7_days: "آخر 7 أيام",
            meta_engagement: "تفاعل ميتا",
            active_integrations: "الربط النشط",
            integration_status: "حالة الربط",
            product_inventory: "مخزون المنتجات",
            no_social: "لا يوجد اتصال بالتواصل الاجتماعي",
            operational: "جميع الأنظمة تعمل بشكل طبيعي",
            active_count: "نشط"
        },
        assistant: {
            title: "مساعد الذكاء الاصطناعي",
            subtitle: "مدعوم بـ Gemini 2.0 Flash • مجاني • مدرك للسياق",
            placeholder: "اسألني عن الطلبات أو العملاء أو المبيعات...",
            suggested_actions: "الإجراءات المقترحة:",
            reasoning_engine: "محرك التفكير",
            steps: {
                analyzing: "تحليل نية الطلب...",
                context: "الوصول إلى سياق العمل...",
                formulating: "صياغة الرد..."
            },
            model_info: {
                title: "نموذج الذكاء الاصطناعي",
                model: "النموذج",
                temp: "درجة الحرارة",
                max_tokens: "الحد الأقصى للرموز",
                context: "إدراك السياق",
                enabled: "مفعل"
            },
            business_context: {
                title: "نظرة عامة على العمل",
                project: "المشروع",
                total_messages: "إجمالي الرسائل",
                unread_messages: "رسائل غير مقروءة"
            },
            capabilities: {
                title: "قدرات الذكاء الاصطناعي",
                analyze: "تحليل بيانات المبيعات",
                manage_orders: "إدارة الطلبات",
                respond: "الرد على العملاء",
                reports: "إنشاء التقارير",
                follow_ups: "جدولة المتابعات"
            },
            usage: {
                title: "الاستخدام اليومي",
                requests: "الطلبات",
                tokens: "الرموز",
                cost: "التكلفة التقديرية:"
            },
            suggestions: {
                show_sales: "أرني أداء المبيعات اليوم",
                list_orders: "عرض الطلبات الأخيرة",
                summarize_unread: "تلخيص الرسائل غير المقروءة",
                generate_report: "إنشاء التقرير الأسبوعي",
                compare_sales: "مقارنة مبيعات هذا الشهر بالشهر الماضي",
                pending_orders: "عرض الطلبات المعلقة",
                track_fulfillment: "تتبع تنفيذ الطلبات",
                draft_responses: "صياغة ردود للعملاء",
                urgent_messages: "ترتيب الرسائل حسب الأولوية",
                monthly_report: "إنشاء التقرير الشهري",
                customer_trends: "تحليل اتجاهات العملاء",
                export_csv: "تصدير البيانات إلى CSV",
                customer_insights: "عرض رؤى العملاء",
                high_value: "البحث عن العملاء ذوي القيمة العالية",
                feedback: "مراجعة ملاحظات العملاء"
            },
            welcome: {
                greeting: "أهلاً بك! 👋 أنا **مساعد المبيعات الذكي** الخاص بك - جزء من منصة AI Sales Commander.",
                what_i_am: "**🎯 من أنا:**",
                description: "أنا لست مجرد روبوت محادثة - أنا شريكك في ذكاء الأعمال المدمج في هذه المنصة. سأساعدك في:",
                features: [
                    "فهم بيانات مبيعاتك من Shopify وعمليات الربط الأخرى",
                    "إدارة محادثات العملاء من WhatsApp و Instagram و Facebook",
                    "إنشاء وتفسير تقارير العمل",
                    "التنقل في المنصة واستخدامها بفعالية",
                    "اتخاذ قرارات مبنية على البيانات لنمو عملك"
                ],
                your_business: "**📊 عملك:**",
                how_it_works: "**🔗 كيف تعمل هذه المنصة:**",
                step1: "**1. ربط التكاملات** (إدخال البيانات)",
                step1_desc: "   ← يجلب Shopify طلباتك ومبيعاتك\n   → تجلب WhatsApp/Instagram/Facebook رسائل العملاء\n   → تتدفق جميع البيانات إلى مركز واحد",
                step2: "**2. إدارة العمليات اليومية** (عمل أسرع)",
                step2_desc: "   → يظهر لوحة التحكم كل شيء في لمحة\n   → تحتوي صفحة الطلبات على كل الطلبات من كل القنوات\n   → تحتوي صفحة الرسائل على كل المحادثات في صندوق واحد\n   → أساعدك في تحديد الأولويات والرد",
                step3: "**3. توليد الرؤى** (إخراج البيانات)",
                step3_desc: "   → تحلل التقارير أداءك\n   → أشرح ما تعنيه الأرقام\n   → نحدد الفرص معاً\n   → عملك ينمو! 📈",
                quick_start: "**💡 دليل البدء السريع:**",
                ready: "**🚀 أنا مستعد للمساعدة!**",
                footer: "انقر فوق أحد الإجراءات المقترحة أدناه أو اسألني عن أي شيء يخص عملك. أنا أفهم التدفق الكامل من التكاملات ← المنصة ← التقارير ← الرؤى."
            }
        },
        projects: {
            title: "المشاريع",
            description: "إدارة وحدات العمل والإعدادات الخاصة بك.",
            create_new: "إنشاء مشروع",
            no_projects: "لا توجد مشاريع. قم بإنشاء مشروع للبدء.",
            active: "نشط",
            created: "تم الإنشاء في",
            switched_to: "تم الانتقال إلى",
            current: "الحالي",
            switch: "انتقال",
            delete_confirm_title: "حذف المشروع؟",
            delete_confirm_desc: "هل أنت متأكد أنك تريد حذف هذا المشروع؟ لا يمكن التراجع عن هذا الإجراء وسيتم حذف جميع البيانات المرتبطة.",
            delete_success: "تم حذف المشروع بنجاح",
            delete_error: "فشل حذف المشروع",
            creating: "جاري الإنشاء...",
            modal: {
                title: "إنشاء مشروع جديد",
                subtitle: "قم بإعداد مشروع عملك الجديد",
                name_label: "اسم المشروع *",
                name_placeholder: "متجري الرائع",
                desc_label: "الوصف",
                desc_placeholder: "وصف موجز لمشروعك...",
                timezone_label: "المنطقة الزمنية"
            },
            fields: {
                name: "اسم المشروع",
                description: "الوصف",
                website: "رابط الموقع",
                industry: "المجال"
            }
        },
        deals: {
            title: "خط المبيعات",
            description: "تتبع العملاء المحتملين وإدارة الصفقات.",
            new_deal: "صفقة جديدة",
            filter: "تصفية",
            move_error: "فشل نقل الصفقة",
            no_stages: "لا توجد مراحل في خط المبيعات.",
            configure_pipeline: "إعداد خط المبيعات",
            add_deal: "إضافة صفقة",
            lead: "عميل محتمل",
            stages: {
                new_lead: "عميل جديد",
                contacted: "تم التواصل",
                qualified: "مؤهل",
                proposal: "عرض سعر",
                negotiation: "مفاوضات",
                won: "مكسب",
                lost: "خسارة"
            },
            card: {
                value: "القيمة",
                probability: "الاحتمالية",
                expected: "تاريخ الإغلاق"
            }
        },
        integrations: {
            title: "التكاملات",
            description: "اربط قنوات المبيعات ومنصات التواصل الخاصة بك لتركيز عملياتك التجارية في مكان واحد.",
            refresh_identities: "تحديث الهويات",
            terminal: "محطة الويب هوك",
            connect: "ربط",
            connected: "متصل",
            disconnected: "غير متصل",
            pending: "معلق",
            syncing: "جاري المزامنة",
            error: "خطأ",
            sync: "مزامنة الآن",
            verify: "تحقق",
            delete_confirm: "هل أنت متأكد من حذف هذا التكامل؟ لا يمكن التراجع عن هذا الإجراء.",
            setup_instructions: "تعليمات الإعداد",
            connect_provider: "ربط {{name}}",
            save: "حفظ وربط",
            cancel: "إلغاء",
            status: "الحالة",
            sync_success: "بدأت المزامنة بنجاح",
            delete_success: "تم حذف التكامل بنجاح",
            verify_success: "تم التحقق من التكامل بنجاح!",
            connect_success: "تم ربط التكامل بنجاح!",
            qr_success: "امسح رمز QR لربط واتساب!",
            identities_success: "تم تحديث هويات العملاء بنجاح.",
            identities_up_to_date: "جميع هويات العملاء محدثة بالفعل.",
            configure: "إعداد",
            meta: "ربط فيسبوك وإنستغرام",
            whatsapp: "ربط واتساب",
            telegram: "ربط تيليجرام",
            tiktok: "ربط تيك توك",
            discord: "ربط ديسكورد",
            providers: {
                shopify: {
                    name: "Shopify",
                    description: "قم بمزامنة الطلبات والمنتجات من متجر Shopify الخاص بك",
                    instructions: "1. قم بتسجيل الدخول إلى مسؤول Shopify\n2. قم بإنشاء تطبيق تطوير\n3. قم بتكوين نطاقات Admin API (read_orders, read_products)\n4. انسخ مفتاح API والسر"
                },
                whatsapp: {
                    name: "واتساب",
                    description: "الاتصال عبر WhatsApp Business Cloud API أو WA-Gateway",
                    instructions: "API الرسمي: استخدم معرف رقم الهاتف والرمز.\nWA-Gateway: امسح رمز QR عبر الخادم المستضاف ذاتيًا."
                },
                telegram: {
                    name: "تيليجرام",
                    description: "اربط بوت تيليجرام الخاص بك للتواصل مع العملاء",
                    instructions: "1. أنشئ بوت عبر @BotFather\n2. احصل على رمز API\n3. الصق الرمز هنا"
                },
                instagram: {
                    name: "إنستغرام",
                    description: "إدارة رسائل إنستغرام المباشرة والتعليقات",
                    instructions: "1. اربط إنستغرام بصفحة فيسبوك\n2. احصل على معرف حساب الأعمال والرمز"
                },
                facebook: {
                    name: "فيسبوك",
                    description: "اربط فيسبوك ماسنجر لدعم العملاء",
                    instructions: "1. احصل على معرف صفحة فيسبوك\n2. قم بتوليد رمز وصول الصفحة"
                },
                tiktok: {
                    name: "تيك توك",
                    description: "تكامل متجر تيك توك ورسائل الأعمال",
                    instructions: "1. سجل الدخول إلى مركز بائع تيك توك\n2. احصل على مفتاح التطبيق والسر"
                },
                discord: {
                    name: "ديسكورد",
                    description: "دعم العملاء المدعوم بالذكاء الاصطناعي عبر تطبيق ديسكورد",
                    instructions: "1. أنشئ تطبيقًا في بوابة مطوري ديسكورد\n2. احصل على رمز البوت"
                }
            },
            form: {
                shopify_url: "رابط متجر Shopify (مثال: mystore.myshopify.com)",
                api_key: "مفتاح API / معرف رقم الهاتف",
                api_secret: "رمز الوصول إلى API / السر",
                webhook_url: "رابط Webhook (اختياري)",
                whatsapp_provider: "مزود واتساب",
                business_api: "واتساب Business API (الرسمي)",
                go_whatsapp: "Go-WhatsApp (استضافة ذاتية)",
                phone_number: "رقم الهاتف (مع رمز الدولة)",
                business_account_id: "معرف حساب الأعمال",
                base_url: "رابط WA-Gateway",
                session_id: "معرف الجلسة",
                page_id: "معرف صفحة فيسبوك",
                app_id: "معرف تطبيق فيسبوك",
                shop_id: "معرف متجر تيك توك",
                app_key: "مفتاح تطبيق تيك توك",
                app_secret: "سر تطبيق تيك توك",
                access_token: "رمز الوصول لتيك توك",
                guild_id: "معرف سيرفر ديسكورد"
            }
        },
        settings: {
            title: "الخصائص",
            general: "عام",
            account: "الحساب",
            notifications: "الإشعارات",
            theme: "المظهر",
            language: "اللغة"
        },
        bot_training: {
            title: "مركز تدريب البوت",
            subtitle: "قم بتعزيز ذكاء البوت بتعليمات ومعرفة مخصصة",
            tabs: {
                instructions: "تعليمات الذكاء الاصطناعي",
                knowledge: "قاعدة المعرفة (RAG)"
            },
            buttons: {
                auto_train: "تدريب تلقائي",
                add_instruction: "إضافة تعليمات",
                add_knowledge: "إضافة معرفة",
                scrape_url: "سحب من رابط",
                edit: "تعديل",
                delete: "حذف",
                save: "حفظ التغييرات",
                cancel: "إلغاء",
                extract: "استخراج المعرفة"
            },
            search_placeholder: "بحث...",
            stats: {
                total_instructions: "إجمالي التعليمات",
                total_knowledge: "إجمالي المعرفة",
                status: "الحالة",
                live: "نشط ومتزامن"
            },
            empty: {
                no_instructions: "لا توجد تعليمات",
                no_knowledge: "قاعدة المعرفة فارغة",
                add_instruction_desc: "أضف تعليمات لتعليم الذكاء الاصطناعي كيفية التصرف.",
                add_knowledge_desc: "أضف معرفة تجارية أو أسئلة شائعة لمساعدة الذكاء الاصطناعي في الإجابة."
            },
            modals: {
                edit_instruction: "تعديل التعليمات",
                add_instruction: "إضافة تعليمات",
                edit_knowledge: "تعديل المعرفة",
                add_knowledge: "إضافة معرفة",
                scrape_title: "سحب من رابط",
                scrape_desc: "أدخل رابطًا (صفحة أسئلة شائعة، دليل، أو وثائق) لاستخراج المحتوى تلقائيًا لقاعدة المعرفة.",
                fields: {
                    title: "العنوان",
                    instruction: "التعليمات",
                    category: "الفئة",
                    priority: "الأولوية",
                    content: "المحتوى",
                    website_url: "رابط الموقع",
                    published: "منشور ونشط"
                }
            }
        },
        inbox: {
            title: "الرسائل",
            subtitle: "إدارة الاتصالات متعددة القنوات بذكاء مدعوم بالذكاء الاصطناعي.",
            search_placeholder: "بحث عن محادثات...",
            tabs: {
                all: "الكل"
            },
            empty: {
                no_conversations: "لا توجد محادثات",
                select: "حدد محادثة",
                select_desc: "حدد محادثة لعرض التاريخ، ورؤى الذكاء الاصطناعي، وإدارة الطلبات."
            },
            chat: {
                start_conversation: "ابدأ محادثة",
                type_message: "اكتب رسالة...",
                input_placeholder: "اكتب رسالتك...",
                ai_assistant: "مساعد AI",
                clear_chat: "مسح المحادثة",
                enable_ai: "تفعيل AI",
                disable_ai: "تعطيل AI",
                manual: "يدوي",
                auto: "تلقائي",
                vip_customer: "عميل VIP",
                system_event: "حدث النظام"
            }
        },
        orders: {
            title: "إدارة الطلبات",
            subtitle: "تتبع تلقائي للطلبات ومعالجة بالذكاء الاصطناعي",
            stats: {
                total_orders: "إجمالي الطلبات",
                total_revenue: "إجمالي الإيرادات",
                pending_orders: "طلبات معلقة",
                fulfillment_rate: "معدل التنفيذ"
            },
            search_placeholder: "بحث عن الطلبات بالاسم، البريد الإلكتروني، أو المعرف...",
            filters: {
                all: "كل الطلبات",
                pending: "معلق",
                processing: "جاري المعالجة",
                fulfilled: "تم التنفيذ",
                shipped: "تم الشحن",
                cancelled: "ملغي"
            },
            table: {
                id: "رقم الطلب",
                customer: "العميل",
                date: "التاريخ",
                total: "الإجمالي",
                status: "الحالة",
                actions: "إجراءات"
            },
            empty: {
                title: "لا توجد طلبات",
                subtitle: "ستظهر الطلبات هنا عندما يقوم العملاء بالشراء"
            },
            actions: {
                view: "عرض التفاصيل",
                ai_process: "معالجة AI",
                fulfill: "تحديد كمكتمل",
                delete: "حذف الطلب",
                delete_confirm: "هل أنت متأكد من حذف هذا الطلب؟"
            },
            details: {
                title: "تفاصيل الطلب",
                customer_info: "معلومات العميل",
                delivery_address: "عنوان التوصيل",
                items: "عناصر الطلب",
                quantity: "الكمية"
            }
        },
        products: {
            title: "كتالوج المنتجات",
            subtitle: "إدارة المنتجات لردود الذكاء الاصطناعي",
            buttons: {
                bulk_upload: "رفع ملف CSV",
                add_product: "إضافة منتج",
                add_first: "أضف منتجك الأول",
                cancel: "إلغاء",
                save: "إنشاء منتج",
                update: "تحديث المنتج",
                delete_confirm: "هل أنت متأكد من حذف هذا المنتج؟"
            },
            search_placeholder: "بحث عن المنتجات بالاسم، الرمز، أو الوصف...",
            empty: {
                title: "لا توجد منتجات",
                desc_search: "لا توجد منتجات تطابق بحثك",
                desc_empty: "أضف منتجات لتدريب مساعد الذكاء الاصطناعي"
            },
            card: {
                in_stock: "متوفر",
                out_of_stock: "غير متوفر",
                view_storage: "عرض تفاصيل التخزين",
                viewing_storage: "عرض التخزين",
                edit: "تعديل",
                qty: "الكمية",
                more: "المزيد"
            },
            storage: {
                title: "تفاصيل تخزين المخزون",
                empty_title: "لا توجد منتجات",
                empty_desc: "أنشئ منتجاً لإدارة تفاصيل التخزين.",
                select_product: "اختر منتجاً لإدارة التخزين.",
                current_qty: "الكمية الحالية",
                reorder_point: "نقطة إعادة الطلب",
                safety_stock: "مخزون الأمان",
                locations: "مواقع التخزين",
                notes: "ملاحظات التخزين",
                attachments: "ملفات مرجعية",
                select_prompt: "اختر منتجاً لعرض/تعديل تفاصيل التخزين"
            },
            modal: {
                add_title: "إضافة منتج جديد",
                edit_title: "تعديل المنتج",
                fields: {
                    name: "اسم المنتج",
                    description: "الوصف",
                    sku: "رمز SKU",
                    category: "الفئة",
                    price: "السعر",
                    currency: "العملة",
                    stock: "المخزون",
                    in_stock: "متوفر",
                    tags: "الوسوم (مفصولة بفواصل)",
                    keywords: "كلمات مفتاحية للذكاء الاصطناعي",
                    storage_locations: "مواقع التخزين",
                    storage_locations_hint: "استخدم \"|\" للفصل بين المواقع المتعددة.",
                    reorder_point: "نقطة إعادة الطلب",
                    safety_stock: "مخزون الأمان",
                    storage_notes: "ملاحظات التخزين",
                    attachments: "روابط المرفقات (مفصولة بفواصل)"
                }
            }
        },
        reports: {
            title: "التحليلات والتقارير",
            subtitle: "رؤى مدعومة بالذكاء الاصطناعي وتحليلات شاملة",
            cards: {
                escalations: "تصعيدات الدعم",
                escalations_desc: "تتطلب انتباه بشري اليوم",
                sales: "مبيعات اليوم",
                sales_desc: "إيرادات فورية",
                vs_yesterday: "مقارنة بالأمس",
                performance: "نظرة عامة على الأداء",
                week_revenue: "إيرادات هذا الأسبوع",
                last_week_revenue: "إيرادات الأسبوع الماضي",
                month_revenue: "إيرادات هذا الشهر",
                month_escalations: "التصعيدات (شهري)"
            },
            types: {
                sales: "تحليلات المبيعات",
                sales_desc: "الإيرادات، الطلبات، ومؤشرات الأداء",
                orders: "تتبع الطلبات",
                orders_desc: "تحليلات تنفيذ وتتبع الطلبات",
                customers: "تفاعل العملاء",
                customers_desc: "تحليل سلوك ومشاعر العملاء",
                performance: "أداء النظام",
                performance_desc: "أتمتة الذكاء الاصطناعي ومقاييس النظام",
                roi: "تحليل العائد",
                roi_desc: "العائد على الاستثمار لأتمتة AI"
            },
            controls: {
                generate: "إنشاء تقرير AI",
                generating: "جاري الإنشاء...",
                ranges: {
                    last_7: "آخر 7 أيام",
                    last_30: "آخر 30 يوم",
                    last_month: "الشهر الماضي"
                }
            },
            charts: {
                revenue: "اتجاه الإيرادات",
                status: "توزيع حالات الطلب",
                channel: "استخدام القنوات",
                ai: "أتمتة AI"
            },
            insights: {
                title: "رؤى الذكاء الاصطناعي",
                trends: "أهم الاتجاهات",
                recommendations: "التوصيات"
            },
            empty: {
                title: "لم يتم إنشاء تقرير بعد",
                desc: "اختر نوع التقرير واضغط \"إنشاء تقرير AI\" للحصول على تحليلات شاملة",
                button: "إنشاء أول تقرير"
            },
            summary: {
                total_orders: "إجمالي الطلبات",
                total_revenue: "إجمالي الإيرادات",
                average_order_value: "متوسط قيمة الطلب",
                total_messages: "إجمالي الرسائل",
                inbound_messages: "الرسائل الواردة",
                outbound_messages: "الرسائل الصادرة",
                ai_generated_messages: "رسائل AI",
                automation_rate: "نسبة الأتمتة",
                total_tokens: "إجمالي التوكنز",
                total_cost_usd: "تكلفة AI الإجمالية",
                average_cost_per_message: "متوسط تكلفة الرسالة",
                revenue_per_message: "الإيراد لكل رسالة",
                ai_cost_per_order: "تكلفة AI لكل طلب"
            }
        },
        campaigns: {
            title: "الحملات المتتابعة (Drip)",
            subtitle: "أتمتة رحلات العملاء مع تتابعات رسائل زمنية.",
            new: "حملة جديدة",
            empty: "لم يتم العثور على حملات. أنشئ واحدة للبدء.",
            status: {
                active: "نشط",
                paused: "متوقف",
                steps: "خطوات"
            },
            builder: {
                title: "منشئ الحملات",
                name: "اسم الحملة",
                trigger: "نوع المشغل",
                add_step: "إضافة خطوة",
                save: "حفظ الحملة"
            }
        },
        payments: {
            title: "المدفوعات والفواتير",
            subtitle: "إدارة الفواتير وإنشاء روابط دفع سريعة.",
            new_invoice: "فاتورة جديدة",
            quick_link: "رابط سريع",
            table: {
                invoice_num: "رقم الفاتورة #",
                customer: "العميل",
                amount: "المبلغ",
                status: "الحالة",
                date: "التاريخ",
                actions: "الإجراءات",
                empty: "لا توجد فواتير. أنشئ رابطاً سريعاً أو فاتورة جديدة."
            },
            modal: {
                title: "إنشاء رابط دفع",
                amount: "المبلغ (USD)",
                description: "الوصف",
                generate: "إنشاء الرابط",
                copy: "نسخ",
                open: "فتح",
                close: "إغلاق",
                success: "تم إنشاء رابط الدفع!",
                copied: "تم النسخ"
            }
        },
        subscription: {
            title: "خطط الاشتراك",
            headline: "اختر خطتك المثالية",
            subheadline: "قم بتنمية عملك مع الأتمتة بالذكاء الاصطناعي. من الشركات الناشئة إلى المؤسسات.",
            billing: {
                monthly: "شهري",
                annually: "سنوي",
                save: "وفر 17%"
            },
            current: {
                title: "الخطة الحالية",
                usage_monthly: "الاستخدام الشهري",
                messages: "الرسائل",
                orders: "الطلبات",
                ai_requests: "طلبات AI"
            },
            cards: {
                popular: "الأكثر شيوعاً",
                mo: "/شهر",
                yr: "/سنة",
                save_amount: "وفر {amount} ({percent}%)",
                more_features: "+{count} ميزات إضافية",
                buttons: {
                    current: "الخطة الحالية",
                    start: "ابدأ الآن",
                    upgrade: "ترقية الآن"
                }
            },
            comparison: {
                title: "مقارنة الميزات عبر جميع الخطط",
                header_feature: "الميزة",
                features: {
                    projects: "المشاريع",
                    messages: "رسائل/شهر",
                    orders: "طلبات/شهر",
                    ai_requests: "طلبات AI/شهر",
                    integrations: "عمليات الربط",
                    storage: "التخزين",
                    team_members: "أعضاء الفريق",
                    ai_automation: "أتمتة AI",
                    advanced_reports: "تقارير متقدمة",
                    social_media: "إدارة التواصل الاجتماعي",
                    memory: "ذاكرة المحادثة",
                    order_auto: "أتمتة الطلبات",
                    api: "وصول API",
                    white_label: "علامة تجارية بيضاء",
                    custom_ai: "نماذج AI مخصصة"
                },
                unlimited: "غير محدود"
            },
            faq: {
                title: "أسئلة؟",
                desc: "هل تحتاج مساعدة في اختيار الخطة المناسبة؟ تواصل مع فريق الدعم.",
                contact: "تواصل مع المبيعات",
                docs: "عرض التوثيق"
            },
            states: {
                loading: "جاري تحميل خطط الاشتراك...",
                error: "فشل التحميل",
                retry: "حاول مرة أخرى"
            }
        },
        social: {
            title: "مركز التواصل الاجتماعي",
            subtitle: "إدارة جميع حسابات التواصل الاجتماعي في مكان واحد",
            tabs: {
                feed: "التغذية الاجتماعية",
                comments: "تعليقات العملاء"
            },
            stats: {
                comments: "إجمالي التعليقات",
                pending: "قيد الانتظار",
                responded: "تم الرد",
                rate: "معدل الاستجابة"
            },
            filters: {
                platform: "المنصة",
                status: "الحالة",
                all_platforms: "كل المنصات",
                all_status: "كل الحالات",
                pending: "قيد الانتظار",
                responded: "تم الرد"
            },
            feed: {
                no_items: "لا توجد عناصر",
                connect_hint: "قم بربط حساب Meta لرؤية التغذية",
                loading: "جاري تحميل التغذية...",
                view_details: "عرض التفاصيل",
                manage_comments: "إدارة التعليقات",
                view_on: "عرض على {platform}",
                likes: "الإعجابات",
                comments: "التعليقات"
            },
            comments: {
                no_comments: "لا توجد تعليقات بعد",
                hint: "ستظهر تعليقات التواصل الاجتماعي هنا",
                loading: "جاري تحميل التعليقات...",
                intent: "النية",
                response: "الرد",
                sent: "أرسلت",
                generate: "إنشاء رد AI",
                generating: "جاري الإنشاء...",
                reply_modal: "الرد المنشأ:\n\n{response}\n\nإرسال هذا الرد؟"
            },
            accounts: {
                all: "كل الحسابات",
                unnamed: "حساب غير مسمى",
                id: "المعرف"
            },
            drawer: {
                title: "تفاصيل المنشور",
                no_media: "لا توجد وسائط",
                view_original: "عرض الأصل",
                likes: "الإعجابات",
                comments: "التعليقات",
                thread: "سلسلة التعليقات",
                no_thread: "لا توجد تعليقات لعرضها",
                generate_reply: "إنشاء رد",
                thinking: "جاري التفكير..."
            }
        },
        predictive: {
            title: "رابط التنبؤ",
            subtitle: "محرك التنبؤ السلوكي والتحليل المدعوم بالذكاء الاصطناعي.",
            confidence: "ثقة النموذج",
            metrics: {
                projection: "توقعات 30 يوم",
                churn_risk: "خطر تسرب العملاء",
                conversion: "التحويل المتوقع",
                risk_score: "درجة المخاطرة",
                potential_loss: "الخسارة المحتملة",
                vs_baseline: "مقابل الأساس"
            },
            charts: {
                revenue: "مسار الإيرادات"
            },
            risks: {
                title: "تنبيهات الاحتفاظ",
                view_all: "عرض جميع المخاطر"
            },
            recommendations: {
                title: "الخطوات الاستراتيجية التالية",
                top_opportunity: "أفضل فرصة",
                execute: "تنفيذ الاستراتيجية"
            }
        },
        smart_signals: {
            title: "إشارات ذكية",
            live_analysis: "تحليل مباشر",
            scanning: "جاري مسح تدفقات البيانات...",
            signals_feed: "تغذية الإشارات",
            signals: {
                revenue_velocity: {
                    title: "سرعة الإيرادات",
                    message: "دوران متوقع +12% مقابل الأساس. مجموعات عالية القيمة نشطة."
                },
                anomaly: {
                    title: "تم اكتشاف خلل",
                    message: "انحراف في حجم الرسائل (+3σ). يوصى بتدخل الدعم."
                },
                conversion: {
                    title: "إشارة تحويل",
                    message: "تم اكتشاف نية 'مميزة' في 8 جلسات نشطة. هل تود التفاعل التلقائي؟"
                },
                system: {
                    title: "سلامة النظام",
                    message: "جميع واجهات برمجة التطبيقات تعمل. 99.9% وقت تشغيل خلال الحمل الأقصى."
                }
            }
        }
    }
};

export default translations;

/**
 * Custom hook to handle translations with dot-notation support.
 * Automatically pulls current language from useThemeStore.
 * @returns {object} - { t: translation function, language: current language code }
 */
export const useTranslation = () => {
    const { language } = useThemeStore();

    const t = (key) => {
        const keys = key.split('.');
        let result = translations[language] || translations['en'];

        for (const k of keys) {
            result = result?.[k];
            if (!result) break;
        }

        return result || key;
    };

    return { t, language };
};
