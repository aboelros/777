import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ErrorBoundary } from 'react-error-boundary';
import { Toaster } from 'sonner';
import { Plus } from 'lucide-react';
import ErrorFallback from './components/ErrorBoundary';
import { PageLoader } from './components/LoadingSpinner';
import { useAuthStore } from './store/authStore';
import { useProjectStore } from './store/projectStore';
import useThemeStore from './store/themeStore';
import CreateProjectModal from './components/CreateProjectModal';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import CommandPalette from './components/CommandPalette';
import Dashboard from './pages/Dashboard';
import Projects from './pages/Projects';
import Assistant from './pages/Assistant';
import Deals from './pages/Deals';
import Integrations from './pages/Integrations';
import IntegrationsManagement from './pages/IntegrationsManagement';
import MetaCallback from './pages/MetaCallback';
import PrivacyPolicy from './pages/PrivacyPolicy';
import Messages from './pages/Messages';
import Orders from './pages/Orders';
import OrderTracking from './pages/OrderTracking';
import Products from './pages/Products';
import BotTraining from './pages/BotTraining';
import SocialMedia from './pages/SocialMedia';
import DripCampaigns from './pages/DripCampaigns';
import Payments from './pages/Payments';
import Reports from './pages/Reports';
import Subscription from './pages/Subscription';
import UsageDashboard from './pages/UsageDashboard';
import Settings from './pages/Settings';
import About from './pages/About';
import Login from './pages/Login';

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
function MainLayout({ children }) {
  const testingMode = import.meta.env.VITE_TESTING_MODE === 'true';
  const [showCreateProject, setShowCreateProject] = useState(false);
  const { currentProject, projects, loadProjects } = useProjectStore();

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  return (
    <div className="flex h-screen bg-dark-950 overflow-hidden selection:bg-accent-500/30 selection:text-white">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 relative overflow-hidden bg-dark-900/40 backdrop-blur-xl border-l border-white/5">
        <Header />
        {testingMode && (
          <div className="bg-yellow-500/10 border-b border-yellow-500/30 px-6 py-2 text-yellow-400 text-sm font-medium">
            🧪 Testing Mode Active - Authentication Disabled
          </div>
        )}
        <main className="flex-1 min-h-0 overflow-y-auto overflow-x-hidden custom-scrollbar">
          {children}
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
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/privacy-policy" element={<PrivacyPolicy />} />

          {/* Protected Routes */}
          <Route
            path="/*"
            element={
              <ErrorBoundary FallbackComponent={ErrorFallback}>
                <ProtectedRoute>
                  <MainLayout>
                    <ErrorBoundary FallbackComponent={ErrorFallback}>
                      <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/projects" element={<Projects />} />
                        <Route path="/assistant" element={<Assistant />} />
                        <Route path="/integrations" element={<Integrations />} />
                        <Route path="/deals" element={<Deals />} />
                        <Route path="/integrations/manage" element={<IntegrationsManagement />} />
                        <Route path="/integrations/meta/callback" element={<MetaCallback />} />
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
                        <Route path="/settings" element={<Settings />} />
                        <Route path="/" element={<Dashboard />} />
                        <Route path="*" element={<Navigate to="/" replace />} />
                      </Routes>
                    </ErrorBoundary>
                  </MainLayout>
                </ProtectedRoute>
              </ErrorBoundary>
            }
          />
        </Routes>
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
