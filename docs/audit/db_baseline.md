# Database Schema Baseline

## Table: `bot_instructions` (Model: `BotInstruction`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `project_id` | `UUID` |  | projects.id |
| `title` | `VARCHAR(255)` |  |  |
| `instruction` | `TEXT` |  |  |
| `category` | `VARCHAR(100)` |  |  |
| `priority` | `INTEGER` |  |  |
| `active_for_platforms` | `JSONB` |  |  |
| `active_for_topics` | `JSONB` |  |  |
| `examples` | `JSONB` |  |  |
| `is_active` | `BOOLEAN` |  |  |
| `created_at` | `DATETIME` |  |  |
| `updated_at` | `DATETIME` |  |  |

## Table: `usage_tracking` (Model: `UsageTracking`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `subscription_id` | `UUID` |  | subscriptions.id |
| `user_id` | `UUID` |  | users.id |
| `period_start` | `DATETIME` |  |  |
| `period_end` | `DATETIME` |  |  |
| `messages_sent` | `INTEGER` |  |  |
| `messages_received` | `INTEGER` |  |  |
| `orders_created` | `INTEGER` |  |  |
| `ai_requests` | `INTEGER` |  |  |
| `ai_tokens_used` | `INTEGER` |  |  |
| `storage_used_gb` | `FLOAT` |  |  |
| `ai_cost` | `FLOAT` |  |  |
| `storage_cost` | `FLOAT` |  |  |
| `total_cost` | `FLOAT` |  |  |
| `limits_exceeded` | `JSONB` |  |  |
| `overage_charges` | `FLOAT` |  |  |
| `extra_data` | `JSONB` |  |  |
| `created_at` | `DATETIME` |  |  |
| `updated_at` | `DATETIME` |  |  |

## Table: `deals` (Model: `Deal`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `project_id` | `UUID` |  | projects.id |
| `stage_id` | `UUID` |  | pipeline_stages.id |
| `customer_id` | `UUID` |  | customer_profiles.id |
| `title` | `VARCHAR(255)` |  |  |
| `value` | `FLOAT` |  |  |
| `currency` | `VARCHAR(3)` |  |  |
| `probability` | `FLOAT` |  |  |
| `priority` | `VARCHAR(20)` |  |  |
| `expected_close_date` | `DATETIME` |  |  |
| `tags` | `JSONB` |  |  |
| `notes` | `TEXT` |  |  |
| `extra_data` | `JSONB` |  |  |
| `is_active` | `BOOLEAN` |  |  |
| `status` | `VARCHAR(50)` |  |  |
| `created_at` | `DATETIME` |  |  |
| `updated_at` | `DATETIME` |  |  |

## Table: `drip_campaigns` (Model: `DripCampaign`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `project_id` | `UUID` |  | projects.id |
| `name` | `VARCHAR(255)` |  |  |
| `description` | `TEXT` |  |  |
| `trigger_type` | `VARCHAR(50)` |  |  |
| `trigger_value` | `VARCHAR(255)` |  |  |
| `is_active` | `BOOLEAN` |  |  |
| `created_at` | `DATETIME` |  |  |
| `updated_at` | `DATETIME` |  |  |

## Table: `auto_response_templates` (Model: `AutoResponseTemplate`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `project_id` | `UUID` |  | projects.id |
| `name` | `VARCHAR(255)` |  |  |
| `description` | `TEXT` |  |  |
| `trigger_keywords` | `JSONB` |  |  |
| `trigger_platforms` | `JSONB` |  |  |
| `trigger_intent` | `VARCHAR(100)` |  |  |
| `response_template` | `TEXT` |  |  |
| `variations` | `JSONB` |  |  |
| `use_ai_enhancement` | `BOOLEAN` |  |  |
| `requires_approval` | `BOOLEAN` |  |  |
| `times_used` | `INTEGER` |  |  |
| `success_rate` | `FLOAT` |  |  |
| `is_active` | `BOOLEAN` |  |  |
| `created_at` | `DATETIME` |  |  |
| `updated_at` | `DATETIME` |  |  |

## Table: `api_logs` (Model: `APILog`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `INTEGER` | Yes |  |
| `project_id` | `UUID` |  | projects.id |
| `endpoint` | `VARCHAR(255)` |  |  |
| `method` | `VARCHAR(10)` |  |  |
| `request` | `JSONB` |  |  |
| `response` | `JSONB` |  |  |
| `status_code` | `INTEGER` |  |  |
| `duration_ms` | `FLOAT` |  |  |
| `ai_tokens_used` | `INTEGER` |  |  |
| `cost_estimate` | `FLOAT` |  |  |
| `user_id` | `UUID` |  |  |
| `ip_address` | `VARCHAR(45)` |  |  |
| `user_agent` | `TEXT` |  |  |
| `created_at` | `DATETIME` |  |  |

## Table: `customer_profiles` (Model: `CustomerProfile`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `project_id` | `UUID` |  | projects.id |
| `customer_id` | `VARCHAR(255)` |  |  |
| `platform_accounts` | `JSONB` |  |  |
| `name` | `VARCHAR(255)` |  |  |
| `email` | `VARCHAR(255)` |  |  |
| `phone` | `VARCHAR(50)` |  |  |
| `avatar_url` | `TEXT` |  |  |
| `last_sync` | `DATETIME` |  |  |
| `preferred_language` | `VARCHAR(10)` |  |  |
| `preferred_platform` | `VARCHAR(50)` |  |  |
| `communication_style` | `VARCHAR(50)` |  |  |
| `interaction_count` | `INTEGER` |  |  |
| `last_interaction` | `DATETIME` |  |  |
| `first_interaction` | `DATETIME` |  |  |
| `total_orders` | `INTEGER` |  |  |
| `total_spent` | `FLOAT` |  |  |
| `average_order_value` | `FLOAT` |  |  |
| `favorite_products` | `JSONB` |  |  |
| `overall_sentiment` | `VARCHAR(50)` |  |  |
| `satisfaction_score` | `FLOAT` |  |  |
| `customer_type` | `VARCHAR(50)` |  |  |
| `tags` | `JSONB` |  |  |
| `interests` | `JSONB` |  |  |
| `purchase_patterns` | `JSONB` |  |  |
| `lifetime_value_estimate` | `FLOAT` |  |  |
| `ai_enabled` | `BOOLEAN` |  |  |
| `ai_settings` | `JSONB` |  |  |
| `notes` | `TEXT` |  |  |
| `special_instructions` | `TEXT` |  |  |
| `is_vip` | `BOOLEAN` |  |  |
| `is_blocked` | `BOOLEAN` |  |  |
| `requires_special_attention` | `BOOLEAN` |  |  |
| `extra_data` | `JSONB` |  |  |
| `created_at` | `DATETIME` |  |  |

## Table: `model_trainings` (Model: `ModelTraining`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `project_id` | `UUID` |  | projects.id |
| `status` | `VARCHAR(9)` |  |  |
| `gemini_model` | `VARCHAR(100)` |  |  |
| `dataset_location` | `VARCHAR(500)` |  |  |
| `training_params` | `JSONB` |  |  |
| `model_version` | `VARCHAR(100)` |  |  |
| `metrics` | `JSONB` |  |  |
| `error_message` | `TEXT` |  |  |
| `started_at` | `DATETIME` |  |  |
| `completed_at` | `DATETIME` |  |  |
| `created_at` | `DATETIME` |  |  |

## Table: `users` (Model: `User`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `email` | `VARCHAR(255)` |  |  |
| `password_hash` | `VARCHAR(255)` |  |  |
| `name` | `VARCHAR(255)` |  |  |
| `role` | `VARCHAR(5)` |  |  |
| `is_active` | `BOOLEAN` |  |  |
| `last_login` | `DATETIME` |  |  |
| `created_at` | `DATETIME` |  |  |
| `updated_at` | `DATETIME` |  |  |

## Table: `drip_steps` (Model: `DripStep`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `campaign_id` | `UUID` |  | drip_campaigns.id |
| `step_order` | `INTEGER` |  |  |
| `delay_hours` | `INTEGER` |  |  |
| `content_template` | `TEXT` |  |  |
| `message_type` | `VARCHAR(50)` |  |  |
| `created_at` | `DATETIME` |  |  |
| `updated_at` | `DATETIME` |  |  |

## Table: `projects` (Model: `Project`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `owner_id` | `UUID` |  | users.id |
| `project_code` | `VARCHAR(50)` |  |  |
| `name` | `VARCHAR(255)` |  |  |
| `description` | `TEXT` |  |  |
| `timezone` | `VARCHAR(50)` |  |  |
| `settings` | `JSONB` |  |  |
| `bot_name` | `VARCHAR(100)` |  |  |
| `bot_tone` | `VARCHAR(50)` |  |  |
| `personality_prompt` | `TEXT` |  |  |
| `is_active` | `BOOLEAN` |  |  |
| `created_at` | `DATETIME` |  |  |
| `updated_at` | `DATETIME` |  |  |

## Table: `social_media_comments` (Model: `SocialMediaComment`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `project_id` | `UUID` |  | projects.id |
| `platform` | `VARCHAR(50)` |  |  |
| `external_id` | `VARCHAR(255)` |  |  |
| `post_id` | `VARCHAR(255)` |  |  |
| `content` | `TEXT` |  |  |
| `author_username` | `VARCHAR(255)` |  |  |
| `author_id` | `VARCHAR(255)` |  |  |
| `responded` | `BOOLEAN` |  |  |
| `response_content` | `TEXT` |  |  |
| `response_sent_at` | `DATETIME` |  |  |
| `auto_generated` | `BOOLEAN` |  |  |
| `sentiment` | `VARCHAR(50)` |  |  |
| `intent` | `VARCHAR(100)` |  |  |
| `requires_human` | `BOOLEAN` |  |  |
| `priority` | `INTEGER` |  |  |
| `extra_data` | `JSONB` |  |  |
| `created_at` | `DATETIME` |  |  |
| `updated_at` | `DATETIME` |  |  |

## Table: `payment_links` (Model: `PaymentLink`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `project_id` | `UUID` |  | projects.id |
| `invoice_id` | `UUID` |  | invoices.id |
| `url` | `VARCHAR(500)` |  |  |
| `amount` | `FLOAT` |  |  |
| `currency` | `VARCHAR(3)` |  |  |
| `description` | `VARCHAR(255)` |  |  |
| `status` | `VARCHAR(50)` |  |  |
| `is_active` | `BOOLEAN` |  |  |
| `stripe_payment_link_id` | `VARCHAR(255)` |  |  |
| `created_at` | `DATETIME` |  |  |
| `expires_at` | `DATETIME` |  |  |

## Table: `conversation_history` (Model: `ConversationHistory`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `project_id` | `UUID` |  | projects.id |
| `customer_id` | `VARCHAR(255)` |  |  |
| `customer_name` | `VARCHAR(255)` |  |  |
| `platform` | `VARCHAR(50)` |  |  |
| `conversation_id` | `VARCHAR(255)` |  |  |
| `message_content` | `TEXT` |  |  |
| `message_direction` | `VARCHAR(8)` |  |  |
| `intent` | `VARCHAR(100)` |  |  |
| `sentiment` | `VARCHAR(50)` |  |  |
| `entities_extracted` | `JSONB` |  |  |
| `summary` | `TEXT` |  |  |
| `embedding_vector` | `JSONB` |  |  |
| `extra_data` | `JSONB` |  |  |
| `created_at` | `DATETIME` |  |  |

## Table: `business_context` (Model: `BusinessContext`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `project_id` | `UUID` |  | projects.id |
| `context_type` | `VARCHAR(100)` |  |  |
| `context_key` | `VARCHAR(255)` |  |  |
| `title` | `VARCHAR(255)` |  |  |
| `content` | `TEXT` |  |  |
| `tags` | `JSONB` |  |  |
| `relevance_score` | `FLOAT` |  |  |
| `times_used` | `INTEGER` |  |  |
| `learned_from` | `VARCHAR(100)` |  |  |
| `confidence_score` | `FLOAT` |  |  |
| `active_for_platforms` | `JSONB` |  |  |
| `examples` | `JSONB` |  |  |
| `is_active` | `BOOLEAN` |  |  |
| `last_used` | `DATETIME` |  |  |
| `created_at` | `DATETIME` |  |  |
| `updated_at` | `DATETIME` |  |  |

## Table: `campaign_enrollments` (Model: `CampaignEnrollment`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `project_id` | `UUID` |  | projects.id |
| `campaign_id` | `UUID` |  | drip_campaigns.id |
| `customer_id` | `UUID` |  | customer_profiles.id |
| `status` | `VARCHAR(50)` |  |  |
| `current_step` | `INTEGER` |  |  |
| `next_execution_at` | `DATETIME` |  |  |
| `metadata_info` | `JSONB` |  |  |
| `started_at` | `DATETIME` |  |  |
| `completed_at` | `DATETIME` |  |  |

## Table: `invoices` (Model: `Invoice`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `project_id` | `UUID` |  | projects.id |
| `customer_id` | `UUID` |  | customer_profiles.id |
| `order_id` | `UUID` |  | orders.id |
| `invoice_number` | `VARCHAR(50)` |  |  |
| `status` | `VARCHAR(50)` |  |  |
| `issue_date` | `DATETIME` |  |  |
| `due_date` | `DATETIME` |  |  |
| `paid_at` | `DATETIME` |  |  |
| `amount` | `FLOAT` |  |  |
| `currency` | `VARCHAR(3)` |  |  |
| `tax_amount` | `FLOAT` |  |  |
| `total_amount` | `FLOAT` |  |  |
| `items` | `JSONB` |  |  |
| `notes` | `TEXT` |  |  |
| `stripe_invoice_id` | `VARCHAR(255)` |  |  |
| `payment_link` | `VARCHAR(500)` |  |  |
| `created_at` | `DATETIME` |  |  |
| `updated_at` | `DATETIME` |  |  |

## Table: `social_media_posts` (Model: `SocialMediaPost`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `project_id` | `UUID` |  | projects.id |
| `platform` | `VARCHAR(50)` |  |  |
| `external_id` | `VARCHAR(255)` |  |  |
| `post_url` | `VARCHAR(500)` |  |  |
| `content` | `TEXT` |  |  |
| `media_type` | `VARCHAR(50)` |  |  |
| `media_urls` | `JSONB` |  |  |
| `author_username` | `VARCHAR(255)` |  |  |
| `author_id` | `VARCHAR(255)` |  |  |
| `likes_count` | `INTEGER` |  |  |
| `comments_count` | `INTEGER` |  |  |
| `shares_count` | `INTEGER` |  |  |
| `views_count` | `INTEGER` |  |  |
| `ai_analyzed` | `BOOLEAN` |  |  |
| `sentiment` | `VARCHAR(50)` |  |  |
| `topics` | `JSONB` |  |  |
| `keywords` | `JSONB` |  |  |
| `ai_summary` | `TEXT` |  |  |
| `last_comment_check` | `DATETIME` |  |  |
| `unresponded_comments` | `INTEGER` |  |  |
| `engagement_rate` | `FLOAT` |  |  |
| `best_performing` | `BOOLEAN` |  |  |
| `hashtags` | `JSONB` |  |  |
| `mentions` | `JSONB` |  |  |
| `location` | `VARCHAR(255)` |  |  |
| `extra_data` | `JSONB` |  |  |
| `posted_at` | `DATETIME` |  |  |
| `created_at` | `DATETIME` |  |  |
| `updated_at` | `DATETIME` |  |  |

## Table: `messages` (Model: `Message`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `project_id` | `UUID` |  | projects.id |
| `customer_id` | `UUID` |  | customer_profiles.id |
| `order_id` | `UUID` |  | orders.id |
| `direction` | `VARCHAR(8)` |  |  |
| `platform` | `VARCHAR(50)` |  |  |
| `provider` | `VARCHAR(50)` |  |  |
| `external_id` | `VARCHAR(255)` |  |  |
| `content` | `TEXT` |  |  |
| `content_type` | `VARCHAR(50)` |  |  |
| `attachments` | `JSONB` |  |  |
| `sender` | `JSONB` |  |  |
| `recipient` | `JSONB` |  |  |
| `ai_generated` | `BOOLEAN` |  |  |
| `ai_model` | `VARCHAR(100)` |  |  |
| `ai_prompt_tokens` | `INTEGER` |  |  |
| `ai_completion_tokens` | `INTEGER` |  |  |
| `ai_cost` | `FLOAT` |  |  |
| `extra_data` | `JSONB` |  |  |
| `is_read` | `BOOLEAN` |  |  |
| `status` | `VARCHAR(50)` |  |  |
| `error_message` | `TEXT` |  |  |
| `sent_at` | `DATETIME` |  |  |
| `created_at` | `DATETIME` |  |  |

## Table: `products` (Model: `Product`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `project_id` | `UUID` |  | projects.id |
| `name` | `VARCHAR(255)` |  |  |
| `description` | `TEXT` |  |  |
| `sku` | `VARCHAR(100)` |  |  |
| `price` | `FLOAT` |  |  |
| `currency` | `VARCHAR(3)` |  |  |
| `stock_quantity` | `INTEGER` |  |  |
| `in_stock` | `BOOLEAN` |  |  |
| `storage_locations` | `JSONB` |  |  |
| `reorder_point` | `INTEGER` |  |  |
| `safety_stock` | `INTEGER` |  |  |
| `storage_notes` | `TEXT` |  |  |
| `storage_attachments` | `JSONB` |  |  |
| `images` | `JSONB` |  |  |
| `category` | `VARCHAR(100)` |  |  |
| `tags` | `JSONB` |  |  |
| `specifications` | `JSONB` |  |  |
| `faq` | `JSONB` |  |  |
| `keywords` | `JSONB` |  |  |
| `extra_data` | `JSONB` |  |  |
| `is_active` | `BOOLEAN` |  |  |
| `created_at` | `DATETIME` |  |  |
| `updated_at` | `DATETIME` |  |  |

## Table: `orders` (Model: `Order`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `project_id` | `UUID` |  | projects.id |
| `customer_id` | `UUID` |  | customer_profiles.id |
| `external_id` | `VARCHAR(255)` |  |  |
| `provider` | `VARCHAR(50)` |  |  |
| `status` | `VARCHAR(50)` |  |  |
| `items` | `JSONB` |  |  |
| `total` | `FLOAT` |  |  |
| `currency` | `VARCHAR(3)` |  |  |
| `extra_data` | `JSONB` |  |  |
| `tags` | `JSONB` |  |  |
| `order_date` | `DATETIME` |  |  |
| `fulfilled_date` | `DATETIME` |  |  |
| `updated_at` | `DATETIME` |  |  |
| `created_at` | `DATETIME` |  |  |

## Table: `project_members` (Model: `ProjectMember`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `project_id` | `UUID` |  | projects.id |
| `user_id` | `UUID` |  | users.id |
| `role` | `VARCHAR(9)` |  |  |
| `created_at` | `DATETIME` |  |  |
| `updated_at` | `DATETIME` |  |  |

## Table: `knowledge_base` (Model: `KnowledgeBase`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `project_id` | `UUID` |  | projects.id |
| `title` | `VARCHAR(255)` |  |  |
| `content` | `TEXT` |  |  |
| `source_type` | `VARCHAR(50)` |  |  |
| `source_url` | `VARCHAR(500)` |  |  |
| `is_active` | `BOOLEAN` |  |  |
| `tags` | `JSONB` |  |  |
| `metadata_info` | `JSONB` |  |  |
| `created_at` | `DATETIME` |  |  |
| `updated_at` | `DATETIME` |  |  |

## Table: `integrations` (Model: `Integration`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `project_id` | `UUID` |  | projects.id |
| `provider` | `VARCHAR(50)` |  |  |
| `status` | `VARCHAR(12)` |  |  |
| `config` | `JSONB` |  |  |
| `extra_data` | `JSONB` |  |  |
| `last_sync` | `DATETIME` |  |  |
| `error_message` | `TEXT` |  |  |
| `created_at` | `DATETIME` |  |  |
| `updated_at` | `DATETIME` |  |  |

## Table: `product_images` (Model: `ProductImage`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `key` | `VARCHAR(500)` | Yes |  |
| `data` | `BLOB` |  |  |
| `content_type` | `VARCHAR(100)` |  |  |
| `size` | `INTEGER` |  |  |
| `created_at` | `DATETIME` |  |  |
| `updated_at` | `DATETIME` |  |  |

## Table: `pipeline_stages` (Model: `PipelineStage`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `project_id` | `UUID` |  | projects.id |
| `name` | `VARCHAR(100)` |  |  |
| `index` | `INTEGER` |  |  |
| `color` | `VARCHAR(50)` |  |  |
| `is_active` | `BOOLEAN` |  |  |
| `created_at` | `DATETIME` |  |  |
| `updated_at` | `DATETIME` |  |  |

## Table: `refresh_tokens` (Model: `RefreshToken`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `user_id` | `UUID` |  | users.id |
| `token` | `VARCHAR(500)` |  |  |
| `expires_at` | `DATETIME` |  |  |
| `created_at` | `DATETIME` |  |  |

## Table: `subscriptions` (Model: `Subscription`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `user_id` | `UUID` |  | users.id |
| `tier` | `VARCHAR(12)` |  |  |
| `status` | `VARCHAR(9)` |  |  |
| `price_monthly` | `FLOAT` |  |  |
| `price_annually` | `FLOAT` |  |  |
| `billing_cycle` | `VARCHAR(50)` |  |  |
| `currency` | `VARCHAR(10)` |  |  |
| `started_at` | `DATETIME` |  |  |
| `expires_at` | `DATETIME` |  |  |
| `trial_ends_at` | `DATETIME` |  |  |
| `cancelled_at` | `DATETIME` |  |  |
| `next_billing_date` | `DATETIME` |  |  |
| `stripe_customer_id` | `VARCHAR(255)` |  |  |
| `stripe_subscription_id` | `VARCHAR(255)` |  |  |
| `stripe_payment_method_id` | `VARCHAR(255)` |  |  |
| `limit_messages` | `INTEGER` |  |  |
| `limit_orders` | `INTEGER` |  |  |
| `limit_ai_requests` | `INTEGER` |  |  |
| `limit_projects` | `INTEGER` |  |  |
| `limit_integrations` | `INTEGER` |  |  |
| `limit_storage_gb` | `FLOAT` |  |  |
| `limit_team_members` | `INTEGER` |  |  |
| `features` | `JSONB` |  |  |
| `total_paid` | `FLOAT` |  |  |
| `invoices` | `JSONB` |  |  |
| `extra_data` | `JSONB` |  |  |
| `created_at` | `DATETIME` |  |  |
| `updated_at` | `DATETIME` |  |  |

## Table: `reports` (Model: `Report`)
| Column | Type | PK | Foreign Keys |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes |  |
| `project_id` | `UUID` |  | projects.id |
| `report_type` | `VARCHAR(50)` |  |  |
| `payload` | `JSONB` |  |  |
| `summary` | `TEXT` |  |  |
| `start_date` | `DATETIME` |  |  |
| `end_date` | `DATETIME` |  |  |
| `file_url` | `VARCHAR(500)` |  |  |
| `generated_at` | `DATETIME` |  |  |

