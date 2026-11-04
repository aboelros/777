/// Centralized verified API endpoint definitions for Automind backend.
class ApiEndpoints {
  ApiEndpoints._();

  static const String apiVersion = '/api/v1';

  // Auth endpoints
  static const String login = '$apiVersion/auth/login';
  static const String register = '$apiVersion/auth/register';
  static const String refresh = '$apiVersion/auth/refresh';
  static const String logout = '$apiVersion/auth/logout';
  static const String me = '$apiVersion/auth/me';

  // Projects endpoints
  static const String projects = '$apiVersion/projects';
  static String project(String projectId) => '$projects/$projectId';
  static String projectMembers(String projectId) =>
      '$projects/$projectId/members';

  // Messages & Inbox endpoints
  static String conversations(String projectId) =>
      '$apiVersion/messages/$projectId/conversations';
  static String conversationMessages(String projectId, String conversationId) =>
      '$apiVersion/messages/$projectId/conversations/$conversationId/messages';
  static String sendMessage(String projectId) =>
      '$apiVersion/messages/$projectId/send';
  static String toggleCustomerAi(String projectId, String profileId) =>
      '$apiVersion/messages/$projectId/customers/$profileId/toggle-ai';
  static String markConversationRead(String projectId, String conversationId) =>
      '$apiVersion/messages/$projectId/conversations/$conversationId/read';
  static String customerProfile(String projectId, String profileId) =>
      '$apiVersion/messages/$projectId/customers/$profileId';

  // Real-Time WebSocket endpoint
  static String projectWs(String projectId) => '/ws/$projectId';

  // Orders endpoints
  static String orders(String projectId) => '$apiVersion/orders/$projectId';
  static String order(String projectId, String orderId) =>
      '$apiVersion/orders/$projectId/$orderId';
  static String ordersRequiringAttention(String projectId) =>
      '$apiVersion/order-management/$projectId/orders/requiring-attention';

  // Dashboard & Analytics endpoints
  static String dashboardSummary(String projectId) =>
      '$apiVersion/reports/$projectId/dashboard-summary';
  static String reports(String projectId) => '$apiVersion/reports/$projectId';

  // Bot Training & AI endpoints
  static String botInstructions(String projectId) =>
      '$apiVersion/bot-training/$projectId/instructions';
  static String botInstruction(String projectId, String instructionId) =>
      '$apiVersion/bot-training/$projectId/instructions/$instructionId';
  static String botTemplates(String projectId) =>
      '$apiVersion/bot-training/$projectId/templates';

  // Products catalog endpoints
  static String products(String projectId) => '$apiVersion/products/$projectId';
  static String product(String projectId, String productId) =>
      '$apiVersion/products/$projectId/$productId';

  // Integrations endpoints
  static String integrations(String projectId) =>
      '$apiVersion/integrations/$projectId';

  // Subscriptions & Usage endpoints
  static const String mySubscription =
      '$apiVersion/subscriptions/my-subscription';
  static const String subscriptionUsage = '$apiVersion/subscriptions/usage';
  static const String subscriptionPlans = '$apiVersion/subscriptions/plans';

  // CRM & Deals endpoints
  static String deals(String projectId) => '$apiVersion/deals/$projectId/deals';
  static String dealStages(String projectId) =>
      '$apiVersion/deals/$projectId/stages';

  // Drip Campaigns endpoints
  static String campaigns(String projectId) =>
      '$apiVersion/drip-campaigns/$projectId/campaigns';

  // Social Media endpoints
  static String socialAccounts(String projectId) =>
      '$apiVersion/social-media-accounts/$projectId';
  static String socialPosts(String projectId) =>
      '$apiVersion/social-media/$projectId/posts';
}
