import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Table, Tag, Button, Input, Space, Empty, Spin, Drawer, Descriptions, Typography } from 'antd';
import { ReloadOutlined, EyeOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { getDatasets, getDataset } from '@/api/datasets';
import type { Dataset, DatasetField } from '@/types';

const { Title, Text } = Typography;
const S = 1.5;

export default function DatasetsPage() {
  const [page, setPage] = useState(1);
  const [keyword, setKeyword] = useState('');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
  const [drawerLoading, setDrawerLoading] = useState(false);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['datasets', page, keyword],
    queryFn: () => getDatasets({ page, page_size: 20, keyword: keyword || undefined }),
  });

  const handleView = async (id: string) => {
    setDrawerOpen(true);
    setDrawerLoading(true);
    try {
      const ds = await getDataset(id);
      setSelectedDataset(ds);
    } catch {
      // ignore
    } finally {
      setDrawerLoading(false);
    }
  };

  const columns: ColumnsType<Dataset> = [
    { title: '名称', dataIndex: 'name', key: 'name', ellipsis: true, width: 200 * S },
    {
      title: '数据源', dataIndex: 'source', key: 'source', width: 160 * S,
      render: (s: { name: string } | null) => s?.name || '-',
    },
    { title: '字段数', dataIndex: 'field_count', key: 'field_count', width: 80 * S },
    {
      title: '数据量', dataIndex: 'data_volume', key: 'data_volume', width: 120 * S,
      render: (v: number) => v.toLocaleString(),
    },
    {
      title: '更新时间', dataIndex: 'updated_at', key: 'updated_at', width: 170 * S,
      render: (t: string) => new Date(t).toLocaleString('zh-CN'),
    },
    {
      title: '负责人', dataIndex: 'owner', key: 'owner', width: 100 * S,
      render: (o: { real_name: string } | null) => o?.real_name || '-',
    },
    {
      title: '操作', key: 'actions', width: 120 * S,
      render: (_, record) => (
        <Button size="small" icon={<EyeOutlined />} onClick={() => handleView(record.id)}>详情</Button>
      ),
    },
  ];

  const fieldColumns: ColumnsType<DatasetField> = [
    { title: '字段名', dataIndex: 'field_name', key: 'field_name', width: 120 * S },
    { title: '别名', dataIndex: 'field_alias', key: 'field_alias', width: 100 * S, render: (v: string | null) => v || '-' },
    { title: '类型', dataIndex: 'field_type', key: 'field_type', width: 80 * S, render: (t: string) => <Tag>{t}</Tag> },
    { title: '维度', dataIndex: 'is_dimension', key: 'is_dimension', width: 80 * S, render: (v: boolean) => v ? <Tag color="blue">是</Tag> : '-' },
    { title: '指标', dataIndex: 'is_metric', key: 'is_metric', width: 80 * S, render: (v: boolean) => v ? <Tag color="green">是</Tag> : '-' },
    { title: '聚合', dataIndex: 'aggregation', key: 'aggregation', width: 80 * S, render: (v: string | null) => v || '-' },
    { title: '单位', dataIndex: 'unit', key: 'unit', width: 60 * S, render: (v: string | null) => v || '-' },
  ];

  return (
    <div>
      <div className="page-header">
        <Title level={4}>数据集管理</Title>
        <Text type="secondary">管理可供分析的数据集</Text>
      </div>

      <div className="filter-bar">
        <Input.Search
          placeholder="搜索数据集名称"
          allowClear
          style={{ width: 240 * S }}
          onSearch={(v) => { setKeyword(v); setPage(1); }}
        />
        <Button icon={<ReloadOutlined />} onClick={() => refetch()}>刷新</Button>
      </div>

      {isLoading ? (
        <div style={{ textAlign: 'center', padding: 80 * S }}><Spin size="large" /></div>
      ) : isError ? (
        <Empty description="加载失败，请检查后端服务" />
      ) : (
        <Table<Dataset>
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

      <Drawer
        title={selectedDataset?.name || '数据集详情'}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        width={720 * S}
        loading={drawerLoading}
      >
        {selectedDataset && (
          <>
            <Descriptions column={2} size="small" bordered style={{ marginBottom: 24 * S }}>
              <Descriptions.Item label="描述">{selectedDataset.description || '-'}</Descriptions.Item>
              <Descriptions.Item label="数据源">{selectedDataset.source?.name || '-'}</Descriptions.Item>
              <Descriptions.Item label="源表">{selectedDataset.source_table}</Descriptions.Item>
              <Descriptions.Item label="数据量">{selectedDataset.data_volume.toLocaleString()}</Descriptions.Item>
              <Descriptions.Item label="字段数">{selectedDataset.field_count}</Descriptions.Item>
              <Descriptions.Item label="负责人">{selectedDataset.owner?.real_name || '-'}</Descriptions.Item>
            </Descriptions>
            <Title level={5}>字段列表</Title>
            <Table<DatasetField>
              dataSource={selectedDataset.fields}
              columns={fieldColumns}
              rowKey="id"
              size="small"
              pagination={false}
              scroll={{ x: 'max-content' }}
            />
          </>
        )}
      </Drawer>
    </div>
  );
}
