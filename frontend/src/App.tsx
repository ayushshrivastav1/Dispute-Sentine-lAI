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
    fetch("http://127.0.0.1:8000/api/v1/health")
      .then(res => res.json())
      .then(data => setIntegrations(data))
      .catch(() => {});
  }, []);

  return (
    <div className="bg-warning/15 text-warning px-4 py-2 text-xs font-semibold text-center flex items-center justify-center gap-4 border-b border-warning/30">
      <span className="bg-warning/20 px-2 py-0.5 rounded text-[11px] font-bold tracking-wide">
        DATA MODE: {(integrations?.data_mode || "SYNTHETIC").toUpperCase()} EVALUATION SET
      </span>
      <span>Policy Engine: v{integrations?.policy_version || "1.3"}</span>
      <span>LLM Model: {integrations?.llm_provider === "groq" ? "Groq / Llama 3.3 70B" : "OpenAI GPT-4o"}</span>
      <span>Safe Mode: {integrations?.live_razorpay_actions ? "LIVE ACTIONS ENABLED" : "LIVE ACTIONS DISABLED"}</span>
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
