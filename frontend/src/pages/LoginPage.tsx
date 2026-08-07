import { useState } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { Form, Input, Button, Card, Typography, message, Space } from 'antd';
import { UserOutlined, LockOutlined, DashboardOutlined } from '@ant-design/icons';
import { useAuthStore } from '@/stores/authStore';

const { Title, Text } = Typography;
const S = 1.5;

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const { login, token } = useAuthStore();
  const navigate = useNavigate();

  if (token) {
    return <Navigate to="/dashboard" replace />;
  }

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      await login(values.username, values.password);
      message.success('登录成功');
      navigate('/dashboard');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : '登录失败';
      message.error(msg || '用户名或密码错误');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Card
        style={{ width: 420 * S, boxShadow: `0 ${8 * S}px ${40 * S}px rgba(0,0,0,0.12)` }}
        styles={{ body: { padding: `${40 * S}px ${40 * S}px ${32 * S}px` } }}
      >
        <div style={{ textAlign: 'center', marginBottom: 32 * S }}>
          <Space size={14 * S}>
            <DashboardOutlined style={{ fontSize: 32 * S, color: '#1677ff' }} />
          </Space>
          <Title level={3} style={{ marginTop: 16 * S, marginBottom: 4 * S }}>
            DataInsight
          </Title>
          <Text type="secondary" style={{ fontSize: 14 * S }}>数据分析与可视化管理平台</Text>
        </div>

        <Form
          name="login"
          size="large"
          onFinish={onFinish}
          autoComplete="off"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>

          <Form.Item style={{ marginBottom: 16 * S }}>
            <Button type="primary" htmlType="submit" loading={loading} block>
              登 录
            </Button>
          </Form.Item>
        </Form>

        <div
          style={{
            background: '#f6f8fa',
            borderRadius: 8 * S,
            padding: `${12 * S}px ${16 * S}px`,
            fontSize: 12 * S,
            color: '#8c8c8c',
            lineHeight: 1.8,
          }}
        >
          <Text type="secondary" style={{ fontSize: 12 * S }}>
            Demo 账号：admin / admin123
          </Text>
          <br />
          <Text type="secondary" style={{ fontSize: 12 * S }}>
            运营经理：ops_manager / ops123
          </Text>
        </div>
      </Card>
    </div>
  );
}
