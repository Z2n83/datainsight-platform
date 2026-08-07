import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Row, Col, Card, Statistic, Table, Tag, Spin, Empty, Select, Typography } from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  DatabaseOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  ToolOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { getDashboardOverview } from '@/api/dashboard';
import type { KpiItem, RecentAlert } from '@/types';

const { Title, Text } = Typography;
const S = 1.5;

const kpiIcons: Record<string, React.ReactNode> = {
  '数据总量': <DatabaseOutlined />,
  '今日新增': <ThunderboltOutlined />,
  '正常运行率': <CheckCircleOutlined />,
  '异常数量': <WarningOutlined />,
  '设备利用率': <ToolOutlined />,
};

const levelColors: Record<string, string> = {
  critical: '#ff4d4f',
  high: '#fa8c16',
  medium: '#faad14',
  low: '#52c41a',
};

const levelLabels: Record<string, string> = {
  critical: '严重',
  high: '高',
  medium: '中',
  low: '低',
};

export default function DashboardPage() {
  const [timeRange, setTimeRange] = useState('7d');

  const { data, isLoading, isError } = useQuery({
    queryKey: ['dashboard', timeRange],
    queryFn: () => getDashboardOverview(timeRange),
  });

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: 120 * S }}>
        <Spin size="large" tip="加载运营数据中..." />
      </div>
    );
  }

  if (isError || !data) {
    return <Empty description="无法加载运营数据，请检查后端服务" />;
  }

  const volumeOption = {
    tooltip: { trigger: 'axis', textStyle: { fontSize: 12 * S } },
    grid: { left: 6 * S, right: 2 * S, top: 2 * S, bottom: 3 * S },
    xAxis: { type: 'category', data: data.data_volume_trend.map((p) => p.date.slice(5)), axisLabel: { fontSize: 11 * S } },
    yAxis: { type: 'value', axisLabel: { fontSize: 11 * S, formatter: (v: number) => `${(v / 10000).toFixed(0)}万` } },
    series: [{ data: data.data_volume_trend.map((p) => p.value), type: 'line', smooth: true, areaStyle: { opacity: 0.15 }, lineStyle: { color: '#1677ff', width: 3 * S }, itemStyle: { color: '#1677ff' }, symbolSize: 6 * S }],
  };

  const anomalyOption = {
    tooltip: { trigger: 'axis', textStyle: { fontSize: 12 * S } },
    grid: { left: 4 * S, right: 2 * S, top: 2 * S, bottom: 3 * S },
    xAxis: { type: 'category', data: data.anomaly_trend.map((p) => p.date.slice(5)), axisLabel: { fontSize: 11 * S } },
    yAxis: { type: 'value', minInterval: 1, axisLabel: { fontSize: 11 * S } },
    series: [{ data: data.anomaly_trend.map((p) => p.count ?? 0), type: 'bar', itemStyle: { color: '#ff7a45', borderRadius: [4 * S, 4 * S, 0, 0] } }],
  };

  const statusOption = {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)', textStyle: { fontSize: 12 * S } },
    legend: { bottom: 0, textStyle: { fontSize: 12 * S } },
    series: [{
      type: 'pie',
      radius: ['50%', '75%'],
      center: ['50%', '45%'],
      label: { show: false },
      data: data.device_status_distribution.map((d) => ({
        name: statusLabel(d.status),
        value: d.count,
        itemStyle: { color: statusColor(d.status) },
      })),
    }],
  };

  const alertColumns = [
    { title: '标题', dataIndex: 'title', key: 'title', ellipsis: true, width: 260 * S },
    {
      title: '等级', dataIndex: 'level', key: 'level', width: 80 * S,
      render: (level: string) => <Tag color={levelColors[level]}>{levelLabels[level]}</Tag>,
    },
    {
      title: '触发时间', dataIndex: 'triggered_at', key: 'triggered_at', width: 170 * S,
      render: (t: string) => t ? new Date(t).toLocaleString('zh-CN') : '-',
    },
  ];

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <Title level={4} style={{ marginBottom: 4 }}>运营工作台</Title>
          <Text type="secondary">企业运营数据总览</Text>
        </div>
        <Select
          value={timeRange}
          onChange={setTimeRange}
          style={{ width: 120 * S, marginTop: 4 }}
          options={[
            { value: '7d', label: '最近7天' },
            { value: '30d', label: '最近30天' },
            { value: '90d', label: '最近90天' },
          ]}
        />
      </div>

      {/* KPI Cards */}
      <Row gutter={[16 * S, 16 * S]} style={{ marginBottom: 16 * S }}>
        {data.kpi.map((item: KpiItem) => (
          <Col xs={24} sm={12} md={Math.floor(24 / 5)} key={item.label}>
            <Card size="small">
              <Statistic
                title={item.label}
                value={item.value}
                precision={item.value % 1 === 0 ? 0 : 1}
                suffix={item.unit}
                prefix={kpiIcons[item.label]}
                valueStyle={{ fontSize: 28 * S, fontWeight: 700 }}
              />
              <div style={{ marginTop: 4 * S }}>
                <Text
                  type={item.trend >= 0 ? 'success' : 'danger'}
                  style={{ fontSize: 13 * S }}
                >
                  {item.trend >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                  {' '}{item.trend_label}
                </Text>
                <Text type="secondary" style={{ fontSize: 12 * S, marginLeft: 4 * S }}>环比</Text>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Trend Charts */}
      <Row gutter={[16 * S, 16 * S]} style={{ marginBottom: 16 * S }}>
        <Col xs={24} lg={12}>
          <Card title="数据量趋势" size="small">
            <ReactECharts option={volumeOption} style={{ height: 280 * S }} />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="异常趋势" size="small">
            <ReactECharts option={anomalyOption} style={{ height: 280 * S }} />
          </Card>
        </Col>
      </Row>

      {/* Bottom row */}
      <Row gutter={[16 * S, 16 * S]}>
        <Col xs={24} lg={8}>
          <Card title="设备状态分布" size="small">
            <ReactECharts option={statusOption} style={{ height: 260 * S }} />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="待办事项" size="small">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 * S }}>
              <TodoItem label="待处理预警" count={data.todos.pending_alerts} color="#ff4d4f" />
              <TodoItem label="待巡检设备" count={data.todos.pending_inspections} color="#fa8c16" />
              <TodoItem label="数据源异常" count={data.todos.data_source_errors} color="#ff7a45" />
              <TodoItem label="数据质量问题" count={data.todos.data_quality_issues} color="#faad14" />
            </div>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="最近预警" size="small">
            <Table<RecentAlert>
              dataSource={data.recent_alerts}
              columns={alertColumns}
              rowKey="id"
              size="small"
              pagination={false}
              scroll={{ y: 200 * S }}
              locale={{ emptyText: '暂无活跃预警' }}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
}

function TodoItem({ label, count, color }: { label: string; count: number; color: string }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <Text>{label}</Text>
      <Tag color={color} style={{ fontSize: 16 * S, fontWeight: 700, padding: `${2 * S}px ${12 * S}px` }}>{count}</Tag>
    </div>
  );
}

function statusLabel(status: string): string {
  const map: Record<string, string> = { normal: '正常', abnormal: '异常', offline: '离线', maintenance: '维护' };
  return map[status] || status;
}

function statusColor(status: string): string {
  const map: Record<string, string> = { normal: '#52c41a', abnormal: '#ff4d4f', offline: '#bfbfbf', maintenance: '#faad14' };
  return map[status] || '#1677ff';
}
