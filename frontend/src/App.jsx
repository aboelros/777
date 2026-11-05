import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ErrorBoundary } from 'react-error-boundary';
import { Toaster } from 'sonner';
import { Plus } from 'lucide-react';
import ErrorFallback from './components/ui/ErrorBoundary';
import { PageLoader } from './components/ui/LoadingSpinner';
import { useAuthStore } from './store/authStore';
import { useProjectStore } from './store/projectStore';
import useThemeStore from './store/themeStore';
import CreateProjectModal from './components/CreateProjectModal';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import CommandPalette from './components/CommandPalette';
import { lazy, Suspense } from 'react';

// Lazy loaded feature pages
const Dashboard = lazy(() => import('./features/analytics/pages/Dashboard'));
const Projects = lazy(() => import('./features/projects/pages/Projects'));
const Assistant = lazy(() => import('./features/ai/pages/Assistant'));
const Deals = lazy(() => import('./features/crm/pages/Deals'));
const Integrations = lazy(() => import('./features/integrations/pages/Integrations'));
const IntegrationsManagement = lazy(() => import('./features/integrations/pages/IntegrationsManagement'));
const MetaCallback = lazy(() => import('./features/social/pages/MetaCallback'));
const TikTokCallback = lazy(() => import('./features/integrations/pages/TikTokCallback'));
const ShopifyCallback = lazy(() => import('./features/integrations/pages/ShopifyCallback'));
const PrivacyPolicy = lazy(() => import('./features/common/pages/PrivacyPolicy'));
const Messages = lazy(() => import('./features/messages/pages/Messages'));
const Orders = lazy(() => import('./features/orders/pages/Orders'));
const OrderTracking = lazy(() => import('./features/orders/pages/OrderTracking'));
const Products = lazy(() => import('./features/products/pages/Products'));
const BotTraining = lazy(() => import('./features/ai/pages/BotTraining'));
const SocialMedia = lazy(() => import('./features/social/pages/SocialMedia'));
const DripCampaigns = lazy(() => import('./features/crm/pages/DripCampaigns'));
const Payments = lazy(() => import('./features/billing/pages/Payments'));
const Reports = lazy(() => import('./features/analytics/pages/Reports'));
const Subscription = lazy(() => import('./features/billing/pages/Subscription'));
const UsageDashboard = lazy(() => import('./features/analytics/pages/UsageDashboard'));
const FinancialCommandCenter = lazy(() => import('./features/finance/pages/FinancialCommandCenter'));
const Settings = lazy(() => import('./features/common/pages/Settings'));
const About = lazy(() => import('./features/common/pages/About'));

const Login = lazy(() => import('./features/auth/pages/Login'));
// Create query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// Protected Route Component
function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuthStore();

  // Testing mode - bypass authentication
  const testingMode = import.meta.env.VITE_TESTING_MODE === 'true';

  if (testingMode) {
    return children;
  }

  if (isLoading) {
    return <PageLoader text="Authenticating..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

// Main Layout
function MainLayout() {
  const location = useLocation();
  const isInbox = location.pathname.startsWith('/inbox') || location.pathname.startsWith('/messages');
  const testingMode = import.meta.env.VITE_TESTING_MODE === 'true';
  const [showCreateProject, setShowCreateProject] = useState(false);
  const { currentProject, projects, loadProjects } = useProjectStore();

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  return (
    <div className="flex h-screen bg-[#030712] overflow-hidden selection:bg-sky-500/30 selection:text-white relative">
      {/* Liquid Ambient Auroras & Chromatic Light Leaks */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute -top-[12%] left-[12%] w-[700px] h-[700px] bg-gradient-to-br from-sky-500/20 via-blue-600/12 to-transparent rounded-full blur-[140px] animate-pulse" style={{ animationDuration: '9s' }} />
        <div className="absolute top-[30%] -right-[8%] w-[650px] h-[650px] bg-gradient-to-bl from-indigo-500/18 via-purple-600/10 to-transparent rounded-full blur-[150px] animate-pulse" style={{ animationDuration: '11s' }} />
        <div className="absolute -bottom-[15%] left-[25%] w-[800px] h-[800px] bg-gradient-to-tr from-cyan-500/14 via-emerald-600/8 to-transparent rounded-full blur-[160px]" />
      </div>

      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 h-full relative overflow-hidden bg-[#070b18]/65 backdrop-blur-2xl border-l border-white/10 z-10 shadow-[inset_0_1px_1px_rgba(255,255,255,0.08)]">
        <Header />
        <main className={`flex-1 min-h-0 h-full flex flex-col ${isInbox ? 'overflow-hidden' : 'overflow-y-auto overflow-x-hidden custom-scrollbar'}`}>
          <Outlet />
        </main>

        {/* Floating Action Button for Project Creation */}
        {(!currentProject || projects.length === 0) && (
          <button
            onClick={() => setShowCreateProject(true)}
            className="fixed bottom-10 right-10 w-16 h-16 bg-gradient-to-r from-accent-500 to-accent-600 hover:from-accent-600 hover:to-accent-700 text-white rounded-full shadow-neon-glow hover:shadow-[0_0_30px_rgba(14,165,233,0.6)] transition-all duration-300 flex items-center justify-center z-40 group border border-white/20"
            title="Create New Project"
          >
            <Plus className="w-8 h-8 group-hover:rotate-90 transition-transform duration-300" />
          </button>
        )}
      </div>

      {/* Create Project Modal */}
      <CreateProjectModal
        isOpen={showCreateProject}
        onClose={() => setShowCreateProject(false)}
      />

      {/* Global Command Palette */}
      <CommandPalette />
    </div>
  );
}

function App() {
  const initializeAuth = useAuthStore(state => state.initialize);
  const initializeTheme = useThemeStore(state => state.initialize);

  useEffect(() => {
    initializeAuth();
    initializeTheme();
  }, [initializeAuth, initializeTheme]);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/privacy-policy" element={<PrivacyPolicy />} />

            {/* Protected Routes */}
            <Route
              element={
                <ErrorBoundary FallbackComponent={ErrorFallback}>
                  <ProtectedRoute>
                    <MainLayout />
                  </ProtectedRoute>
                </ErrorBoundary>
              }
            >
              <Route path="/" element={<Dashboard />} />
              <Route path="/projects" element={<Projects />} />
              <Route path="/assistant" element={<Assistant />} />
              <Route path="/integrations" element={<Integrations />} />
              <Route path="/deals" element={<Deals />} />
              <Route path="/integrations/manage" element={<IntegrationsManagement />} />
              <Route path="/integrations/meta/callback" element={<MetaCallback />} />
              <Route path="/integrations/tiktok/callback" element={<TikTokCallback />} />
              <Route path="/integrations/shopify/callback" element={<ShopifyCallback />} />
              <Route path="/orders" element={<Orders />} />
              <Route path="/order-tracking" element={<OrderTracking />} />
              <Route path="/messages" element={<Messages />} />
              <Route path="/inbox" element={<Messages />} />
              <Route path="/products" element={<Products />} />
              <Route path="/bot-training" element={<BotTraining />} />
              <Route path="/social-media" element={<SocialMedia />} />
              <Route path="/campaigns" element={<DripCampaigns />} />
              <Route path="/payments" element={<Payments />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/subscription" element={<Subscription />} />
              <Route path="/usage" element={<UsageDashboard />} />
              <Route path="/finance" element={<FinancialCommandCenter />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/about" element={<About />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Routes>
        </Suspense>
      </BrowserRouter>

      {/* Toast Notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: 'rgba(15, 23, 42, 0.95)',
            border: '1px solid rgba(14, 165, 233, 0.3)',
            backdropFilter: 'blur(20px)',
            color: '#fff',
          },
        }}
      />
    </QueryClientProvider>
  );
}

export default App;
