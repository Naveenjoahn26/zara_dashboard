import React, { useState } from 'react';
import { TrendingUp, Calendar, DollarSign, Package, Info } from 'lucide-react';

export default function TrendChart({ data = [], interval, setInterval }) {
  const [metric, setMetric] = useState('revenue'); // 'revenue' | 'quantity_sold'
  const [hoveredIdx, setHoveredIdx] = useState(null);

  if (!data || data.length === 0) {
    return (
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md flex flex-col items-center justify-center min-h-[340px] text-slate-500">
        <TrendingUp className="w-10 h-10 mb-2 stroke-1 opacity-40" />
        <p className="text-sm">No trend data available for current date range</p>
        <p className="text-xs text-slate-600 mt-1">Try resetting the date filter</p>
      </div>
    );
  }

  const values = data.map(d => (metric === 'revenue' ? d.revenue : d.quantity_sold));
  const maxVal = Math.max(...values, 1);
  const minVal = Math.min(...values, 0);
  const valRange = maxVal - minVal || 1;

  // Chart dimensions
  const width = 800;
  const height = 260;
  const paddingX = 40;
  const paddingY = 30;
  const plotWidth = width - paddingX * 2;
  const plotHeight = height - paddingY * 2;

  const isSinglePoint = data.length === 1;

  const points = data.map((d, i) => {
    const x = isSinglePoint
      ? width / 2
      : paddingX + (i / Math.max(data.length - 1, 1)) * plotWidth;
    const val = metric === 'revenue' ? d.revenue : d.quantity_sold;
    const y = isSinglePoint
      ? height - paddingY - plotHeight * 0.65
      : height - paddingY - ((val - minVal) / valRange) * plotHeight;
    return { x, y, ...d, val };
  });

  // Construct SVG Path
  let pathD = '';
  let areaD = '';

  if (isSinglePoint) {
    const pt = points[0];
    pathD = `M ${paddingX} ${pt.y} L ${width - paddingX} ${pt.y}`;
    areaD = `M ${paddingX} ${pt.y} L ${width - paddingX} ${pt.y} L ${width - paddingX} ${height - paddingY} L ${paddingX} ${height - paddingY} Z`;
  } else {
    pathD = points.reduce((acc, pt, i) => {
      if (i === 0) return `M ${pt.x} ${pt.y}`;
      const prev = points[i - 1];
      const cpX = (prev.x + pt.x) / 2;
      return `${acc} C ${cpX} ${prev.y}, ${cpX} ${pt.y}, ${pt.x} ${pt.y}`;
    }, '');
    areaD = `${pathD} L ${points[points.length - 1].x} ${height - paddingY} L ${points[0].x} ${height - paddingY} Z`;
  }

  const totalRevenue = data.reduce((sum, d) => sum + (d.revenue || 0), 0);
  const totalVolume = data.reduce((sum, d) => sum + (d.quantity_sold || 0), 0);

  const hoveredPoint = hoveredIdx !== null ? points[hoveredIdx] : (isSinglePoint ? points[0] : null);

  return (
    <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md shadow-xl flex flex-col justify-between">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-emerald-400" />
              Sales & Volume Trends
            </h2>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 font-semibold">
              {isSinglePoint ? 'Single-day Snapshot' : `${data.length} ${interval === 'daily' ? 'Days' : 'Months'}`}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Total {metric === 'revenue' ? `$${totalRevenue.toLocaleString(undefined, { minimumFractionDigits: 2 })}` : `${totalVolume.toLocaleString()} units`}
            {isSinglePoint ? ' recorded on 2024-02-19' : ' over selected timeframe'}
          </p>
        </div>

        {/* Metric & Interval Toggles */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Revenue vs Volume */}
          <div className="flex rounded-lg bg-slate-950 p-1 border border-slate-800 text-xs">
            <button
              onClick={() => setMetric('revenue')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-medium transition ${
                metric === 'revenue' ? 'bg-emerald-500/20 text-emerald-400 shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              <DollarSign className="w-3.5 h-3.5" />
              Revenue
            </button>
            <button
              onClick={() => setMetric('quantity_sold')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-medium transition ${
                metric === 'quantity_sold' ? 'bg-blue-500/20 text-blue-400 shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Package className="w-3.5 h-3.5" />
              Volume
            </button>
          </div>

          {/* Daily vs Monthly */}
          <div className="flex rounded-lg bg-slate-950 p-1 border border-slate-800 text-xs">
            <button
              onClick={() => setInterval('daily')}
              className={`px-3 py-1.5 rounded-md font-medium transition ${
                interval === 'daily' ? 'bg-slate-800 text-white shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              Daily
            </button>
            <button
              onClick={() => setInterval('monthly')}
              className={`px-3 py-1.5 rounded-md font-medium transition ${
                interval === 'monthly' ? 'bg-slate-800 text-white shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              Monthly
            </button>
          </div>
        </div>
      </div>

      {/* Single-point notice if Zara dataset */}
      {isSinglePoint && (
        <div className="mb-3 px-3.5 py-2 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-300 text-xs flex items-center gap-2">
          <Info className="w-4 h-4 shrink-0 text-blue-400" />
          <span>
            <strong>Zara Catalog Snapshot:</strong> Scraped on 2024-02-19 (251 items, 457k units). For multi-month trend lines, switch to <em>sample_sales_data.csv</em> in the header.
          </span>
        </div>
      )}

      {/* SVG Chart Area */}
      <div className="relative w-full aspect-[21/9] sm:aspect-[24/9] max-h-[320px]">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-full overflow-visible"
          onMouseLeave={() => setHoveredIdx(null)}
        >
          <defs>
            <linearGradient id="trendAreaGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={metric === 'revenue' ? '#10b981' : '#3b82f6'} stopOpacity="0.4" />
              <stop offset="100%" stopColor={metric === 'revenue' ? '#10b981' : '#3b82f6'} stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Horizontal Gridlines */}
          {[0, 0.25, 0.5, 0.75, 1].map((pct, idx) => {
            const y = height - paddingY - pct * plotHeight;
            const val = minVal + pct * valRange;
            return (
              <g key={idx}>
                <line
                  x1={paddingX}
                  y1={y}
                  x2={width - paddingX}
                  y2={y}
                  stroke="#1e293b"
                  strokeDasharray="4 4"
                  strokeWidth="1"
                />
                <text
                  x={paddingX - 8}
                  y={y + 4}
                  textAnchor="end"
                  fontSize="10"
                  fill="#64748b"
                >
                  {metric === 'revenue'
                    ? `$${val >= 1000000 ? (val / 1000000).toFixed(1) + 'M' : val >= 1000 ? (val / 1000).toFixed(0) + 'k' : val.toFixed(0)}`
                    : val >= 1000 ? (val / 1000).toFixed(0) + 'k' : val.toFixed(0)}
                </text>
              </g>
            );
          })}

          {/* Area Fill */}
          <path d={areaD} fill="url(#trendAreaGradient)" />

          {/* Trend Line */}
          <path
            d={pathD}
            fill="none"
            stroke={metric === 'revenue' ? '#10b981' : '#3b82f6'}
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Single-point central beacon */}
          {isSinglePoint && (
            <g>
              <circle
                cx={points[0].x}
                cy={points[0].y}
                r="16"
                fill={metric === 'revenue' ? '#10b981' : '#3b82f6'}
                opacity="0.2"
                className="animate-ping"
              />
              <circle
                cx={points[0].x}
                cy={points[0].y}
                r="8"
                fill="#ffffff"
                stroke={metric === 'revenue' ? '#10b981' : '#3b82f6'}
                strokeWidth="4"
              />
            </g>
          )}

          {/* Interactive Hover Dots for multi-point */}
          {!isSinglePoint && points.map((pt, i) => (
            <g
              key={i}
              className="cursor-pointer"
              onMouseEnter={() => setHoveredIdx(i)}
            >
              <circle cx={pt.x} cy={pt.y} r="12" fill="transparent" />
              <circle
                cx={pt.x}
                cy={pt.y}
                r={hoveredIdx === i ? 6 : data.length > 25 ? 2.5 : 4}
                fill={metric === 'revenue' ? '#10b981' : '#3b82f6'}
                stroke="#0f172a"
                strokeWidth="2"
                className="transition-all duration-150"
              />
            </g>
          ))}

          {/* Active Crosshair */}
          {!isSinglePoint && hoveredPoint && (
            <g>
              <line
                x1={hoveredPoint.x}
                y1={paddingY}
                x2={hoveredPoint.x}
                y2={height - paddingY}
                stroke="#475569"
                strokeWidth="1.5"
                strokeDasharray="3 3"
              />
              <circle
                cx={hoveredPoint.x}
                cy={hoveredPoint.y}
                r="7"
                fill="#ffffff"
                stroke={metric === 'revenue' ? '#10b981' : '#3b82f6'}
                strokeWidth="3"
              />
            </g>
          )}

          {/* X Axis labels */}
          {isSinglePoint ? (
            <text
              x={width / 2}
              y={height - 10}
              textAnchor="middle"
              fontSize="12"
              fill="#94a3b8"
              className="font-bold"
            >
              {points[0].period} (Zara Full Scrape Day)
            </text>
          ) : (
            points
              .filter((_, idx) => {
                const step = Math.ceil(points.length / 6);
                return idx % step === 0 || idx === points.length - 1;
              })
              .map((pt, idx) => (
                <text
                  key={idx}
                  x={pt.x}
                  y={height - 10}
                  textAnchor="middle"
                  fontSize="11"
                  fill="#94a3b8"
                  className="font-medium"
                >
                  {pt.period}
                </text>
              ))
          )}
        </svg>

        {/* Hover Tooltip Box */}
        {hoveredPoint && (
          <div
            className="absolute pointer-events-none transform -translate-x-1/2 -translate-y-full mb-3 px-3 py-2 rounded-xl bg-slate-950/95 border border-slate-700 shadow-2xl text-xs z-20 backdrop-blur"
            style={{
              left: `${(hoveredPoint.x / width) * 100}%`,
              top: `${(hoveredPoint.y / height) * 100}%`,
            }}
          >
            <div className="font-semibold text-slate-200 border-b border-slate-800 pb-1 mb-1">
              {hoveredPoint.period}
            </div>
            <div className="flex items-center justify-between gap-4">
              <span className="text-slate-400">Revenue:</span>
              <span className="font-bold text-emerald-400">
                ${hoveredPoint.revenue.toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </span>
            </div>
            <div className="flex items-center justify-between gap-4">
              <span className="text-slate-400">Volume:</span>
              <span className="font-bold text-blue-400">
                {hoveredPoint.quantity_sold.toLocaleString()} units
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
