import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Row, Col, Card, Select, Button, Table, Spin, Empty, Typography, Statistic, Alert } from 'antd';
import { PlayCircleOutlined } from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { getDatasets } from '@/api/datasets';
import { executeAnalysis } from '@/api/analysis';
import type { Dataset, AnalysisResult, DatasetField } from '@/types';

const { Title, Text } = Typography;
const S = 1.5;

export default function DataAnalysisPage() {
  const [selectedDatasetId, setSelectedDatasetId] = useState<string | undefined>();
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([]);
  const [analysisType, setAnalysisType] = useState('trend');
  const [granularity, setGranularity] = useState('day');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { data: dsData } = useQuery({
    queryKey: ['datasetsForAnalysis'],
    queryFn: () => getDatasets({ page: 1, page_size: 50 }),
  });

  const datasets = dsData?.list || [];
  const selectedDs = datasets.find((d) => d.id === selectedDatasetId);
  const metricFields = (selectedDs?.fields || []).filter((f: DatasetField) => f.is_metric);

  const handleExecute = async () => {
    if (!selectedDatasetId || selectedMetrics.length === 0) return;
    setLoading(true);
    setError(null);
    try {
      const res = await executeAnalysis({
        dataset_id: selectedDatasetId,
        metrics: selectedMetrics.map((fn) => ({ field_name: fn, aggregation: 'avg' })),
        analysis_type: analysisType,
        granularity,
      });
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : '分析执行失败');
    } finally {
      setLoading(false);
    }
  };

  const chartOption = result ? buildChartOption(result, analysisType) : null;

  return (
    <div>
      <div className="page-header">
        <Title level={4}>数据分析</Title>
        <Text type="secondary">选择数据集、指标和分析方式，执行数据分析</Text>
      </div>

      {/* Configuration Panel */}
      <Card size="small" style={{ marginBottom: 16 * S }}>
        <Row gutter={[16 * S, 12 * S]} align="middle">
          <Col xs={24} sm={6}>
            <Text strong style={{ display: 'block', marginBottom: 4 * S, fontSize: 14 * S }}>1. 选择数据集</Text>
            <Select
              placeholder="选择数据集"
              value={selectedDatasetId}
              onChange={(v) => { setSelectedDatasetId(v); setSelectedMetrics([]); setResult(null); }}
              style={{ width: '100%' }}
              options={datasets.map((d: Dataset) => ({ value: d.id, label: `${d.name} (${d.data_volume.toLocaleString()}条)` }))}
            />
          </Col>
          <Col xs={24} sm={6}>
            <Text strong style={{ display: 'block', marginBottom: 4 * S, fontSize: 14 * S }}>2. 选择指标</Text>
            <Select
              mode="multiple"
              placeholder="选择分析指标"
              value={selectedMetrics}
              onChange={setSelectedMetrics}
              style={{ width: '100%' }}
              disabled={!selectedDatasetId}
              options={metricFields.map((f: DatasetField) => ({ value: f.field_name, label: `${f.field_alias || f.field_name} (${f.unit || '-'})` }))}
            />
          </Col>
          <Col xs={12} sm={4}>
            <Text strong style={{ display: 'block', marginBottom: 4 * S, fontSize: 14 * S }}>3. 分析方式</Text>
            <Select value={analysisType} onChange={setAnalysisType} style={{ width: '100%' }}
              options={[
                { value: 'trend', label: '趋势分析' },
                { value: 'compare', label: '对比分析' },
                { value: 'anomaly', label: '异常分析' },
                { value: 'ranking', label: '排名分析' },
              ]}
            />
          </Col>
          <Col xs={12} sm={4}>
            <Text strong style={{ display: 'block', marginBottom: 4 * S, fontSize: 14 * S }}>4. 时间粒度</Text>
            <Select value={granularity} onChange={setGranularity} style={{ width: '100%' }}
              options={[
                { value: 'hour', label: '小时' },
                { value: 'day', label: '天' },
                { value: 'week', label: '周' },
                { value: 'month', label: '月' },
              ]}
            />
          </Col>
          <Col xs={24} sm={4} style={{ display: 'flex', alignItems: 'flex-end', paddingTop: 20 * S }}>
            <Button type="primary" icon={<PlayCircleOutlined />} onClick={handleExecute}
              loading={loading} disabled={!selectedDatasetId || selectedMetrics.length === 0} block>
              开始分析
            </Button>
          </Col>
        </Row>
      </Card>

      {error && <Alert type="error" message={error} closable style={{ marginBottom: 16 * S }} onClose={() => setError(null)} />}
      {loading && <div style={{ textAlign: 'center', padding: 80 * S }}><Spin size="large" tip="分析中..." /></div>}
      {!result && !loading && <Empty description="请配置分析参数后点击「开始分析」" style={{ padding: 60 * S }} />}

      {result && !loading && (
        <>
          <Row gutter={[16 * S, 16 * S]} style={{ marginBottom: 16 * S }}>
            <Col xs={12} sm={6}><Card size="small"><Statistic title="平均值" value={result.summary.avg ?? '-'} precision={2} /></Card></Col>
            <Col xs={12} sm={6}><Card size="small"><Statistic title="最大值" value={result.summary.max ?? '-'} precision={2} /></Card></Col>
            <Col xs={12} sm={6}><Card size="small"><Statistic title="最小值" value={result.summary.min ?? '-'} precision={2} /></Card></Col>
            <Col xs={12} sm={6}>
              <Card size="small">
                <Statistic
                  title="趋势"
                  value={result.summary.trend === 'up' ? '上升' : result.summary.trend === 'down' ? '下降' : '稳定'}
                  valueStyle={{ color: result.summary.trend === 'up' ? '#cf1322' : result.summary.trend === 'down' ? '#3f8600' : '#1677ff' }}
                  suffix={result.summary.change_rate != null ? `${result.summary.change_rate}%` : ''}
                />
              </Card>
            </Col>
          </Row>

          {chartOption && (
            <Card title="分析图表" size="small" style={{ marginBottom: 16 * S }}>
              <ReactECharts option={chartOption} style={{ height: 360 * S }} />
            </Card>
          )}

          {result.insights.length > 0 && (
            <Card title="数据洞察" size="small" style={{ marginBottom: 16 * S }}>
              <ul style={{ paddingLeft: 20 * S, margin: 0, fontSize: 14 * S }}>
                {result.insights.map((insight, i) => (
                  <li key={i} style={{ marginBottom: 4 * S }}>{insight}</li>
                ))}
              </ul>
            </Card>
          )}

          <Card title="数据明细" size="small">
            <Table
              dataSource={result.table_data.rows.map((row, i) => {
                const obj: Record<string, unknown> = { _key: i };
                result.table_data.columns.forEach((col, j) => { obj[col] = row[j]; });
                return obj;
              })}
              columns={result.table_data.columns.map((col) => ({ title: col, dataIndex: col, key: col, ellipsis: true, width: 120 * S }))}
              rowKey="_key"
              size="small"
              pagination={{ pageSize: 20, showTotal: (t: number) => `共 ${t} 条` }}
              scroll={{ x: 'max-content' }}
            />
          </Card>

          <div style={{ textAlign: 'right', marginTop: 8 * S }}>
            <Text type="secondary" style={{ fontSize: 12 * S }}>执行耗时: {result.execution_time_ms}ms</Text>
          </div>
        </>
      )}
    </div>
  );
}

function buildChartOption(result: AnalysisResult, type: string) {
  if (!result.chart_data.length) return null;
  const data = result.chart_data;
  const keys = Object.keys(data[0]).filter((k) => k !== 'time_bucket' && !k.endsWith('_is_anomaly') && !k.endsWith('_expected') && !k.endsWith('_change'));
  const xKey = data[0].time_bucket !== undefined ? 'time_bucket' : keys[0];

  if (type === 'anomaly') {
    const valKey = keys.find(k => !k.endsWith('_is_anomaly')) || keys[0];
    return {
      tooltip: { trigger: 'axis', textStyle: { fontSize: 12 * S } },
      grid: { left: 6 * S, right: 2 * S, top: 2 * S, bottom: 3 * S },
      xAxis: { type: 'category', data: data.map((d) => String(d[xKey]).slice(0, 10)), axisLabel: { fontSize: 11 * S } },
      yAxis: { type: 'value', axisLabel: { fontSize: 11 * S } },
      series: [
        { name: '实际值', data: data.map((d) => Number(d[valKey] || 0)), type: 'line', smooth: true, symbolSize: 4 * S, lineStyle: { width: 2 * S } },
        { name: '异常点', data: data.map((d) => d[valKey + '_is_anomaly'] ? Number(d[valKey] || 0) : null), type: 'scatter', symbolSize: 12 * S, itemStyle: { color: '#ff4d4f' } },
      ],
      legend: { textStyle: { fontSize: 12 * S } },
    };
  }

  return {
    tooltip: { trigger: 'axis', textStyle: { fontSize: 12 * S } },
    grid: { left: 6 * S, right: 2 * S, top: 2 * S, bottom: 3 * S },
    xAxis: { type: 'category', data: data.map((d) => String(d[xKey]).slice(0, 10)), axisLabel: { rotate: 30, fontSize: 11 * S } },
    yAxis: { type: 'value', axisLabel: { fontSize: 11 * S } },
    series: keys.map((k) => ({
      name: k,
      data: data.map((d) => Number(d[k] || 0)),
      type: 'line',
      smooth: true,
      areaStyle: { opacity: 0.08 },
      symbolSize: 4 * S,
      lineStyle: { width: 2 * S },
    })),
    legend: { bottom: 0, textStyle: { fontSize: 12 * S } },
  };
}
