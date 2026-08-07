import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Table, Tag, Button, Input, Select, Space, Empty, Spin, message, Typography } from 'antd';
import { PlusOutlined, ReloadOutlined, LinkOutlined, SyncOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { getDataSources, testConnection, triggerSync } from '@/api/dataSources';
import type { DataSource } from '@/types';

const { Title, Text } = Typography;
const S = 1.5;

const typeLabels: Record<string, string> = { mysql: 'MySQL', csv: 'CSV', postgresql: 'PostgreSQL', api: 'API' };
const statusColors: Record<string, string> = { connected: '#52c41a', disconnected: '#bfbfbf', error: '#ff4d4f' };
const statusLabels: Record<string, string> = { connected: '已连接', disconnected: '未连接', error: '异常' };

export default function DataSourcesPage() {
  const [page, setPage] = useState(1);
  const [keyword, setKeyword] = useState('');
  const [typeFilter, setTypeFilter] = useState<string | undefined>();
  const [statusFilter, setStatusFilter] = useState<string | undefined>();

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['dataSources', page, keyword, typeFilter, statusFilter],
    queryFn: () => getDataSources({ page, page_size: 20, keyword: keyword || undefined, type: typeFilter, status: statusFilter }),
  });

  const handleTest = async (id: string) => {
    try {
      const result = await testConnection(id);
      message.success(result.message);
    } catch {
      message.error('连接测试失败');
    }
  };

  const handleSync = async (id: string) => {
    try {
      const result = await triggerSync(id);
      message.success(result.message);
      refetch();
    } catch {
      message.error('同步失败');
    }
  };

  const columns: ColumnsType<DataSource> = [
    { title: '名称', dataIndex: 'name', key: 'name', ellipsis: true, width: 200 * S },
    {
      title: '类型', dataIndex: 'type', key: 'type', width: 100 * S,
      render: (t: string) => <Tag>{typeLabels[t] || t}</Tag>,
    },
    {
      title: '状态', dataIndex: 'status', key: 'status', width: 100 * S,
      render: (s: string) => <Tag color={statusColors[s]}>{statusLabels[s] || s}</Tag>,
    },
    {
      title: '数据量', dataIndex: 'data_volume', key: 'data_volume', width: 120 * S,
      render: (v: number) => v > 0 ? v.toLocaleString() : '-',
    },
    {
      title: '同步方式', dataIndex: 'sync_method', key: 'sync_method', width: 100 * S,
      render: (m: string) => m === 'incremental' ? '增量' : '全量',
    },
    {
      title: '最近同步', dataIndex: 'last_sync_at', key: 'last_sync_at', width: 170 * S,
      render: (t: string | null) => t ? new Date(t).toLocaleString('zh-CN') : '从未',
    },
    {
      title: '负责人', dataIndex: 'owner', key: 'owner', width: 100 * S,
      render: (o: { real_name: string } | null) => o?.real_name || '-',
    },
    {
      title: '操作', key: 'actions', width: 200 * S,
      render: (_, record) => (
        <Space size={4 * S}>
          <Button size="small" icon={<LinkOutlined />} onClick={() => handleTest(record.id)}>测试</Button>
          <Button size="small" icon={<SyncOutlined />} onClick={() => handleSync(record.id)}>同步</Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div className="page-header">
        <Title level={4}>数据源管理</Title>
        <Text type="secondary">管理企业数据源连接与同步</Text>
      </div>

      <div className="filter-bar">
        <Input.Search
          placeholder="搜索数据源名称"
          allowClear
          style={{ width: 240 * S }}
          onSearch={(v) => { setKeyword(v); setPage(1); }}
        />
        <Select
          placeholder="类型筛选"
          allowClear
          style={{ width: 140 * S }}
          value={typeFilter}
          onChange={(v) => { setTypeFilter(v); setPage(1); }}
          options={[
            { value: 'mysql', label: 'MySQL' },
            { value: 'csv', label: 'CSV' },
          ]}
        />
        <Select
          placeholder="状态筛选"
          allowClear
          style={{ width: 140 * S }}
          value={statusFilter}
          onChange={(v) => { setStatusFilter(v); setPage(1); }}
          options={[
            { value: 'connected', label: '已连接' },
            { value: 'disconnected', label: '未连接' },
            { value: 'error', label: '异常' },
          ]}
        />
        <Button icon={<ReloadOutlined />} onClick={() => refetch()}>刷新</Button>
        <Button type="primary" icon={<PlusOutlined />} disabled>新建数据源</Button>
      </div>

      {isLoading ? (
        <div style={{ textAlign: 'center', padding: 80 * S }}><Spin size="large" /></div>
      ) : isError ? (
        <Empty description="加载失败，请检查后端服务" />
      ) : (
        <Table<DataSource>
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
        />
      )}
    </div>
  );
}
