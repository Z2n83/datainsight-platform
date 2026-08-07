import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Table, Tag, Card, Row, Col, Statistic, Select, Empty, Spin, Typography } from 'antd';
import { WarningOutlined, AlertOutlined, InfoCircleOutlined, CheckCircleOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { getAlerts } from '@/api/alerts';
import type { Alert, AlertStats } from '@/types';

const { Title, Text } = Typography;
const S = 1.5;

const levelColors: Record<string, string> = { critical: '#ff4d4f', high: '#fa8c16', medium: '#faad14', low: '#52c41a' };
const levelIcons: Record<string, React.ReactNode> = {
  critical: <AlertOutlined />,
  high: <WarningOutlined />,
  medium: <InfoCircleOutlined />,
  low: <CheckCircleOutlined />,
};
const levelLabels: Record<string, string> = { critical: '严重', high: '高', medium: '中', low: '低' };
const statusLabels: Record<string, string> = { pending: '待处理', processing: '处理中', closed: '已关闭' };
const statusColors: Record<string, string> = { pending: '#ff4d4f', processing: '#1677ff', closed: '#52c41a' };

export default function AlertsPage() {
  const [page, setPage] = useState(1);
  const [levelFilter, setLevelFilter] = useState<string | undefined>();
  const [statusFilter, setStatusFilter] = useState<string | undefined>();

  const { data, isLoading, isError } = useQuery({
    queryKey: ['alerts', page, levelFilter, statusFilter],
    queryFn: () => getAlerts({ page, page_size: 20, level: levelFilter, status: statusFilter || 'pending' }),
  });

  const stats: AlertStats = (data as { statistics?: AlertStats })?.statistics || { critical: 0, high: 0, medium: 0, low: 0 };

  const columns: ColumnsType<Alert> = [
    { title: '标题', dataIndex: 'title', key: 'title', ellipsis: true, width: 260 * S },
    {
      title: '等级', dataIndex: 'level', key: 'level', width: 80 * S,
      render: (l: string) => <Tag color={levelColors[l]} icon={levelIcons[l]}>{levelLabels[l]}</Tag>,
    },
    {
      title: '状态', dataIndex: 'status', key: 'status', width: 90 * S,
      render: (s: string) => <Tag color={statusColors[s]}>{statusLabels[s] || s}</Tag>,
    },
    {
      title: '当前值', dataIndex: 'current_value', key: 'current_value', width: 100 * S,
      render: (v: number) => v > 0 ? v.toFixed(1) : '-',
    },
    {
      title: '阈值', dataIndex: 'threshold_value', key: 'threshold_value', width: 100 * S,
      render: (v: number) => v > 0 ? v.toFixed(1) : '-',
    },
    {
      title: '触发时间', dataIndex: 'triggered_at', key: 'triggered_at', width: 170 * S,
      render: (t: string) => t ? new Date(t).toLocaleString('zh-CN') : '-',
      sorter: (a: Alert, b: Alert) => new Date(a.triggered_at).getTime() - new Date(b.triggered_at).getTime(),
      defaultSortOrder: 'descend',
    },
    {
      title: '负责人', dataIndex: 'assignee', key: 'assignee', width: 100 * S,
      render: (a: { real_name: string } | null) => a?.real_name || '-',
    },
    {
      title: '规则', dataIndex: 'rule', key: 'rule', width: 160 * S, ellipsis: true,
      render: (r: { name: string } | null) => r?.name || '-',
    },
  ];

  return (
    <div>
      <div className="page-header">
        <Title level={4}>预警中心</Title>
        <Text type="secondary">实时监控异常指标，处理预警事件</Text>
      </div>

      <Row gutter={[16 * S, 16 * S]} style={{ marginBottom: 16 * S }}>
        {[
          { label: '严重', value: stats.critical, color: '#ff4d4f' },
          { label: '高', value: stats.high, color: '#fa8c16' },
          { label: '中', value: stats.medium, color: '#faad14' },
          { label: '低', value: stats.low, color: '#52c41a' },
        ].map((item) => (
          <Col xs={12} sm={6} key={item.label}>
            <Card size="small">
              <Statistic
                title={item.label}
                value={item.value}
                valueStyle={{ color: item.color, fontSize: 28 * S }}
                prefix={<WarningOutlined />}
              />
            </Card>
          </Col>
        ))}
      </Row>

      <div className="filter-bar">
        <Select
          placeholder="等级筛选" allowClear
          style={{ width: 120 * S }}
          value={levelFilter}
          onChange={(v) => { setLevelFilter(v); setPage(1); }}
          options={[
            { value: 'critical', label: '严重' },
            { value: 'high', label: '高' },
            { value: 'medium', label: '中' },
            { value: 'low', label: '低' },
          ]}
        />
        <Select
          placeholder="状态筛选" allowClear
          style={{ width: 120 * S }}
          value={statusFilter}
          onChange={(v) => { setStatusFilter(v); setPage(1); }}
          options={[
            { value: 'pending', label: '待处理' },
            { value: 'processing', label: '处理中' },
            { value: 'closed', label: '已关闭' },
          ]}
        />
      </div>

      {isLoading ? (
        <div style={{ textAlign: 'center', padding: 80 * S }}><Spin size="large" /></div>
      ) : isError ? (
        <Empty description="加载失败，请检查后端服务" />
      ) : (
        <Table<Alert>
          dataSource={data?.list || []}
          columns={columns}
          rowKey="id"
          size="middle"
          pagination={{
            current: page,
            pageSize: 20,
            total: data?.total || 0,
            showTotal: (t) => `共 ${t} 条`,
            onChange: (p) => setPage(p),
          }}
          scroll={{ x: 'max-content' }}
        />
      )}
    </div>
  );
}
