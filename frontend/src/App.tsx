import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { Toaster } from 'sonner';
import { useEffect, useState } from 'react';

import { AppShell } from '@/components/layout/AppShell';
import { DashboardPage } from '@/pages/DashboardPage';
import { QueuePage } from '@/pages/QueuePage';
import { DisputeDetailPage } from '@/pages/DisputeDetailPage';
import { LoginPage } from '@/pages/LoginPage';
import { useAuth } from '@/hooks/useAuth';
import './styles.css';

const queryClient = new QueryClient();

function EnvironmentBanner() {
  const [integrations, setIntegrations] = useState<any>(null);
  
  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/v1/health/integrations")
      .then(res => res.json())
      .then(data => setIntegrations(data))
      .catch(() => {});
  }, []);

  if (!integrations) return null;

  return (
    <div className="bg-warning/20 text-warning px-4 py-2 text-xs font-semibold text-center flex items-center justify-center gap-4 border-b border-warning/30">
      <span>Safe Mode: {integrations.razorpay_live_actions ? "LIVE ACTIONS ENABLED" : "LIVE ACTIONS DISABLED"}</span>
      <span>Upload: {integrations.razorpay_upload_evidence ? "ENABLED" : "DISABLED"}</span>
    </div>
  );
}

function ProtectedLayout() {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  
  return (
    <>
      <EnvironmentBanner />
      <AppShell title="DisputeSentinel" description="AI Autopilot for Chargebacks">
        <Outlet />
      </AppShell>
    </>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<ProtectedLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/queue" element={<QueuePage />} />
            <Route path="/disputes/:id" element={<DisputeDetailPage />} />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
      <Toaster />
    </QueryClientProvider>
  );
}

export default App;
