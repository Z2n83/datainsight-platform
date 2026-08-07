"""
Analysis engine using Pandas for data aggregation.
"""
import time
import random
from datetime import datetime, timezone, timedelta
from typing import Optional

import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset import Dataset
from app.models.metric import MetricValue


class AnalysisService:
    """Execute data analysis using Pandas DataFrames."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self, dataset: Dataset, params: dict) -> dict:
        """
        Execute analysis on a dataset.

        Args:
            dataset: The Dataset model instance with fields loaded.
            params: Analysis parameters from AnalysisRequest schema.

        Returns:
            AnalysisResult-compatible dict.
        """
        start_time = time.time()

        analysis_type = params.get("analysis_type", "trend")
        metrics = params.get("metrics", [])
        granularity = params.get("granularity", "day")
        time_range = params.get("time_range")

        # Build a DataFrame from metric_values (simulated if data is sparse)
        df = await self._build_dataframe(dataset, params)

        # Execute analysis based on type
        if analysis_type == "trend":
            result = self._trend_analysis(df, metrics, granularity)
        elif analysis_type == "compare":
            result = self._compare_analysis(df, metrics, granularity)
        elif analysis_type == "anomaly":
            result = self._anomaly_analysis(df, metrics)
        elif analysis_type == "ranking":
            result = self._ranking_analysis(df, metrics, params.get("limit", 10))
        else:
            result = self._trend_analysis(df, metrics, granularity)

        execution_time = int((time.time() - start_time) * 1000)

        # Build chart data from the result DataFrame
        chart_data = self._to_chart_data(result, granularity)

        # Build summary
        summary = self._build_summary(result, metrics)

        # Generate insights
        insights = self._generate_insights(result, metrics, analysis_type)

        # Build table data
        table_data = self._to_table_data(result)

        return {
            "chart_data": chart_data,
            "summary": summary,
            "insights": insights,
            "table_data": table_data,
            "execution_time_ms": execution_time,
        }

    async def _build_dataframe(self, dataset: Dataset, params: dict) -> pd.DataFrame:
        """Build a Pandas DataFrame from metric_values table or generate simulated data."""
        metric_ids = []
        for field in dataset.fields:
            if field.is_metric:
                metric_ids.append(field.id)

        # Try loading from metric_values table
        if metric_ids:
            # For MVP, generate simulated data based on dataset info
            pass

        # Generate realistic simulated data
        return self._generate_simulated_data(dataset, params)

    def _generate_simulated_data(self, dataset: Dataset, params: dict) -> pd.DataFrame:
        """Generate realistic simulated time-series data for demonstration."""
        time_range = params.get("time_range", {})
        granularity = params.get("granularity", "day")
        metrics = params.get("metrics", [])

        # Determine date range
        now = datetime.now(timezone.utc)
        if time_range and time_range.get("preset"):
            preset = time_range["preset"]
            if preset == "last_7_days":
                days = 7
            elif preset == "last_30_days":
                days = 30
            elif preset == "last_90_days":
                days = 90
            else:
                days = 30
        elif time_range and time_range.get("start"):
            start = time_range["start"]
            end = time_range.get("end", now)
            days = (end - start).days or 1
        else:
            days = 30

        # Generate time buckets
        dates = pd.date_range(end=now, periods=days, freq="D")

        # Build data
        data = {"time": dates}
        np.random.seed(42)
        for metric in metrics:
            field_name = metric.get("field_name", "value")
            base = random.uniform(50, 150)
            noise = np.random.normal(0, base * 0.1, days)
            trend_line = np.linspace(0, base * 0.2, days)
            data[field_name] = base + trend_line + noise

        df = pd.DataFrame(data)
        # Add dimension columns for grouping
        for dim in params.get("dimensions", []):
            if dim != "time" and dim not in df.columns:
                # Add a mock dimension
                dimension_field = next(
                    (f for f in dataset.fields if f.field_name == dim), None
                )
                if dimension_field:
                    categories = ["类型A", "类型B", "类型C"]
                    df[dim] = np.random.choice(categories, days)

        return df

    def _trend_analysis(self, df: pd.DataFrame, metrics: list, granularity: str) -> pd.DataFrame:
        """Trend analysis: group by time bucket."""
        if "time" not in df.columns:
            return df

        df = df.copy()
        df["time"] = pd.to_datetime(df["time"])

        if granularity == "day":
            df["time_bucket"] = df["time"].dt.date
        elif granularity == "week":
            df["time_bucket"] = df["time"].dt.to_period("W").apply(lambda r: r.start_time.date())
        elif granularity == "month":
            df["time_bucket"] = df["time"].dt.to_period("M").apply(lambda r: r.start_time.date())
        else:
            df["time_bucket"] = df["time"].dt.date

        metric_cols = [m.get("field_name", "value") for m in metrics]
        agg_map = {}
        for m in metrics:
            col = m.get("field_name", "value")
            agg = m.get("aggregation", "avg")
            if agg == "sum":
                agg_map[col] = "sum"
            elif agg == "max":
                agg_map[col] = "max"
            elif agg == "min":
                agg_map[col] = "min"
            elif agg == "count":
                agg_map[col] = "count"
            else:
                agg_map[col] = "mean"

        result = df.groupby("time_bucket", as_index=False).agg(agg_map)
        result["time_bucket"] = result["time_bucket"].astype(str)
        return result

    def _compare_analysis(self, df: pd.DataFrame, metrics: list, granularity: str) -> pd.DataFrame:
        """Compare analysis: same as trend with period-over-period change."""
        result = self._trend_analysis(df, metrics, granularity)
        for m in metrics:
            col = m.get("field_name", "value")
            if col in result.columns:
                result[f"{col}_change"] = result[col].pct_change() * 100
        return result

    def _anomaly_analysis(self, df: pd.DataFrame, metrics: list) -> pd.DataFrame:
        """Anomaly analysis: detect values outside 2 standard deviations."""
        result = df.copy()
        for m in metrics:
            col = m.get("field_name", "value")
            if col in result.columns and result[col].dtype in ('float64', 'int64'):
                mean = result[col].mean()
                std = result[col].std()
                upper = mean + 2 * std
                lower = mean - 2 * std
                result[f"{col}_is_anomaly"] = (result[col] > upper) | (result[col] < lower)
                result[f"{col}_expected"] = mean
        return result

    def _ranking_analysis(self, df: pd.DataFrame, metrics: list, limit: int) -> pd.DataFrame:
        """Ranking analysis: top N by metric value."""
        result = df.copy()
        for m in metrics:
            col = m.get("field_name", "value")
            if col in result.columns:
                result = result.sort_values(col, ascending=False).head(limit)
        return result

    def _to_chart_data(self, df: pd.DataFrame, granularity: str) -> list[dict]:
        """Convert DataFrame to ECharts-compatible data."""
        records = df.to_dict(orient="records")
        for r in records:
            for k, v in r.items():
                if isinstance(v, (np.integer,)):
                    r[k] = int(v)
                elif isinstance(v, (np.floating,)):
                    r[k] = round(float(v), 2)
                elif isinstance(v, (np.bool_,)):
                    r[k] = bool(v)
                elif pd.isna(v):
                    r[k] = None
        return records

    def _build_summary(self, df: pd.DataFrame, metrics: list) -> dict:
        """Build statistical summary from analysis results."""
        summary = {}
        if df.empty:
            return {"avg": None, "max": None, "min": None, "trend": "stable", "change_rate": 0}

        for m in metrics:
            col = m.get("field_name", "value")
            if col in df.columns and df[col].dtype in ('float64', 'int64'):
                values = df[col].dropna()
                if len(values) > 0:
                    summary["avg"] = round(float(values.mean()), 2)
                    summary["max"] = round(float(values.max()), 2)
                    summary["min"] = round(float(values.min()), 2)

                    if len(values) >= 2:
                        first_half = values[:len(values)//2].mean()
                        second_half = values[len(values)//2:].mean()
                        if second_half > first_half * 1.02:
                            summary["trend"] = "up"
                            summary["change_rate"] = round(float((second_half - first_half) / first_half * 100), 1)
                        elif second_half < first_half * 0.98:
                            summary["trend"] = "down"
                            summary["change_rate"] = round(float((first_half - second_half) / first_half * 100), 1)
                        else:
                            summary["trend"] = "stable"
                            summary["change_rate"] = 0
                break  # Only summarize the first metric for now
        return summary

    def _generate_insights(self, df: pd.DataFrame, metrics: list, analysis_type: str) -> list[str]:
        """Generate human-readable insights from analysis results."""
        insights = []
        for m in metrics:
            col = m.get("field_name", "value")
            if col not in df.columns or df[col].dtype not in ('float64', 'int64'):
                continue
            values = df[col].dropna()
            if len(values) < 2:
                continue

            current = values.iloc[-1]
            avg = values.mean()
            if current > avg * 1.1:
                insights.append(f"{col} 当前值 {round(float(current), 1)} 高于平均值 {round(float(avg), 1)}，超出约 {round(float((current - avg) / avg * 100), 1)}%")
            elif current < avg * 0.9:
                insights.append(f"{col} 当前值 {round(float(current), 1)} 低于平均值 {round(float(avg), 1)}，降幅约 {round(float((avg - current) / avg * 100), 1)}%")

            # Check for recent trend change
            if len(values) >= 5:
                recent = values.iloc[-5:]
                if recent.is_monotonic_increasing:
                    insights.append(f"{col} 最近 5 个周期呈持续上升趋势，建议关注")
                elif recent.is_monotonic_decreasing:
                    insights.append(f"{col} 最近 5 个周期呈持续下降趋势，建议排查原因")
        return insights[:3]  # Limit to 3 insights

    def _to_table_data(self, df: pd.DataFrame) -> dict:
        """Convert DataFrame to table format for API response."""
        if df.empty:
            return {"columns": [], "rows": []}

        columns = list(df.columns)
        rows = []
        for _, row in df.iterrows():
            row_list = []
            for col in columns:
                val = row[col]
                if isinstance(val, (np.integer,)):
                    val = int(val)
                elif isinstance(val, (np.floating,)):
                    val = round(float(val), 2)
                elif isinstance(val, (np.bool_,)):
                    val = bool(val)
                elif pd.isna(val):
                    val = None
                else:
                    val = str(val)
                row_list.append(val)
            rows.append(row_list)

        return {"columns": columns, "rows": rows}
