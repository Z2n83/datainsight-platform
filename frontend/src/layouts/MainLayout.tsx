import { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Button, Dropdown, Avatar, Space, theme } from 'antd';
import {
  DashboardOutlined,
  DatabaseOutlined,
  TableOutlined,
  LineChartOutlined,
  AlertOutlined,
  UserOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '@/stores/authStore';

const { Header, Sider, Content } = Layout;

const S = 1.5;

const menuItems = [
  { key: '/dashboard', icon: <DashboardOutlined />, label: '运营工作台' },
  { key: '/data-sources', icon: <DatabaseOutlined />, label: '数据源管理' },
  { key: '/datasets', icon: <TableOutlined />, label: '数据集管理' },
  { key: '/data-analysis', icon: <LineChartOutlined />, label: '数据分析' },
  { key: '/alerts', icon: <AlertOutlined />, label: '预警中心' },
];

export default function MainLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const { token: themeToken } = theme.useToken();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const selectedKey = '/' + location.pathname.split('/')[1];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        theme="dark"
        width={220 * S}
        collapsedWidth={80 * S}
        style={{
          borderRight: `${7 * S}px solid ${themeToken.colorBorderSecondary}`,
        }}
      >
        <div
          style={{
            height: 64 * S,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontSize: collapsed ? 16 * S : 20 * S,
            fontWeight: 700,
            letterSpacing: 2 * S,
            borderBottom: `${7 * S}px solid rgba(255,255,255,0.1)`,
          }}
        >
          {collapsed ? 'DI' : 'DataInsight'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            padding: `0 ${24 * S}px`,
            height: 64 * S,
            lineHeight: `${64 * S}px`,
            background: themeToken.colorBgContainer,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: `${7 * S}px solid ${themeToken.colorBorderSecondary}`,
          }}
        >
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
          />
          <Dropdown
            menu={{
              items: [
                { key: 'role', label: `角色: ${user?.roles?.map((r) => r.name).join(', ') || '-'}`, disabled: true },
                { type: 'divider' },
                { key: 'logout', icon: <LogoutOutlined />, label: '退出登录', danger: true, onClick: handleLogout },
              ],
            }}
          >
            <Space style={{ cursor: 'pointer', fontSize: 14 * S }}>
              <Avatar size={32 * S} icon={<UserOutlined />} />
              <span>{user?.real_name || user?.username || '用户'}</span>
            </Space>
          </Dropdown>
        </Header>
        <Content
          style={{
            margin: 16 * S,
            padding: 24 * S,
            background: themeToken.colorBgContainer,
            borderRadius: themeToken.borderRadiusLG,
            minHeight: 280,
            overflow: 'auto',
          }}
        >
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
