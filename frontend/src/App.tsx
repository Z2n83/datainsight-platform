import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, App as AntApp } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from '@/stores/authStore';
import MainLayout from '@/layouts/MainLayout';
import LoginPage from '@/pages/LoginPage';
import DashboardPage from '@/pages/DashboardPage';
import DataSourcesPage from '@/pages/DataSourcesPage';
import DatasetsPage from '@/pages/DatasetsPage';
import DataAnalysisPage from '@/pages/DataAnalysisPage';
import AlertsPage from '@/pages/AlertsPage';

const S = 1.5;


const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
    },
  },
});

function AuthGuard({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.token);
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function AppInit({ children }: { children: React.ReactNode }) {
  const initialize = useAuthStore((s) => s.initialize);
  useEffect(() => {
    initialize();
  }, [initialize]);
  return <>{children}</>;
}

export default function App() {
  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          colorPrimary: '#1677ff',

          // ── font sizes ──
          fontSize:           14 * S,
          fontSizeSM:         12 * S,
          fontSizeLG:         16 * S,
          fontSizeXL:         20 * S,
          fontSizeHeading1:   38 * S,
          fontSizeHeading2:   30 * S,
          fontSizeHeading3:   24 * S,
          fontSizeHeading4:   20 * S,
          fontSizeHeading5:   16 * S,

          // ── spacing ──
          lineHeight:         1.5715,
          borderRadius:       6 * S,
          borderRadiusSM:     4 * S,
          borderRadiusLG:     8 * S,
          padding:            16 * S,
          paddingSM:          12 * S,
          paddingXS:          8 * S,
          paddingLG:          24 * S,
          paddingXL:          32 * S,
          paddingContentHorizontal: 16 * S,
          paddingContentVertical:   8 * S,
          margin:             16 * S,
          marginSM:           12 * S,
          marginXS:           8 * S,
          marginLG:           24 * S,
          marginXL:           48 * S,

          // ── control sizes ──
          controlHeight:      32 * S,
          controlHeightSM:    24 * S,
          controlHeightLG:    40 * S,
          controlHeightXS:    16 * S,
          sizeStep:           4 * S,
          sizeUnit:           4 * S,

        },
      }}
    >
      <AntApp>
        <QueryClientProvider client={queryClient}>
          <AppInit>
            <BrowserRouter>
              <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route
                  path="/"
                  element={
                    <AuthGuard>
                      <MainLayout />
                    </AuthGuard>
                  }
                >
                  <Route index element={<Navigate to="/dashboard" replace />} />
                  <Route path="dashboard" element={<DashboardPage />} />
                  <Route path="data-sources" element={<DataSourcesPage />} />
                  <Route path="datasets" element={<DatasetsPage />} />
                  <Route path="data-analysis" element={<DataAnalysisPage />} />
                  <Route path="alerts" element={<AlertsPage />} />
                </Route>
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </BrowserRouter>
          </AppInit>
        </QueryClientProvider>
      </AntApp>
    </ConfigProvider>
  );
}
