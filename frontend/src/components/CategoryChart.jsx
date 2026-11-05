import React from 'react';
import { PieChart, Layers } from 'lucide-react';

const PALETTE = [
  { stroke: '#10b981', bg: 'bg-emerald-500', text: 'text-emerald-400', badge: 'bg-emerald-500/10 border-emerald-500/20' },
  { stroke: '#3b82f6', bg: 'bg-blue-500', text: 'text-blue-400', badge: 'bg-blue-500/10 border-blue-500/20' },
  { stroke: '#8b5cf6', bg: 'bg-purple-500', text: 'text-purple-400', badge: 'bg-purple-500/10 border-purple-500/20' },
  { stroke: '#f59e0b', bg: 'bg-amber-500', text: 'text-amber-400', badge: 'bg-amber-500/10 border-amber-500/20' },
  { stroke: '#ec4899', bg: 'bg-pink-500', text: 'text-pink-400', badge: 'bg-pink-500/10 border-pink-500/20' },
  { stroke: '#06b6d4', bg: 'bg-cyan-500', text: 'text-cyan-400', badge: 'bg-cyan-500/10 border-cyan-500/20' },
  { stroke: '#f97316', bg: 'bg-orange-500', text: 'text-orange-400', badge: 'bg-orange-500/10 border-orange-500/20' },
];

export default function CategoryChart({ data = [] }) {
  if (!data || data.length === 0) {
    return (
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md flex flex-col items-center justify-center min-h-[340px] text-slate-500">
        <PieChart className="w-10 h-10 mb-2 stroke-1 opacity-40" />
        <p className="text-sm">No category distribution available</p>
      </div>
    );
  }

  const totalRevenue = data.reduce((acc, cat) => acc + (cat.revenue || 0), 0);

  // SVG Donut calculation
  const radius = 64;
  const circumference = 2 * Math.PI * radius;
  let accumulatedOffset = 0;

  const slices = data.map((cat, idx) => {
    const pct = totalRevenue > 0 ? (cat.revenue / totalRevenue) : 0;
    const strokeDasharray = `${pct * circumference} ${circumference}`;
    const strokeDashoffset = -accumulatedOffset;
    accumulatedOffset += pct * circumference;
    const color = PALETTE[idx % PALETTE.length];
    return { ...cat, pct, strokeDasharray, strokeDashoffset, color };
  });

  return (
    <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md shadow-xl flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-purple-400" />
            Category Performance
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Revenue and volume distribution across {data.length} categories
          </p>
        </div>
      </div>

      {/* Donut & Stats Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
        {/* SVG Donut Centerpiece */}
        <div className="md:col-span-5 flex flex-col items-center justify-center relative">
          <svg className="w-48 h-48 -rotate-90 transform" viewBox="0 0 160 160">
            {slices.map((slice, i) => (
              <circle
                key={i}
                cx="80"
                cy="80"
                r={radius}
                fill="transparent"
                stroke={slice.color.stroke}
                strokeWidth="18"
                strokeDasharray={slice.strokeDasharray}
                strokeDashoffset={slice.strokeDashoffset}
                className="transition-all duration-500 hover:opacity-80"
              />
            ))}
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">Total</span>
            <span className="text-base font-extrabold text-white">
              ${totalRevenue >= 1_000_000 ? (totalRevenue / 1_000_000).toFixed(1) + 'M' : totalRevenue.toLocaleString()}
            </span>
          </div>
        </div>

        {/* Category List & Progress Bars */}
        <div className="md:col-span-7 space-y-3 max-h-[260px] overflow-y-auto pr-1">
          {slices.map((cat, idx) => (
            <div
              key={idx}
              className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-slate-700 transition"
            >
              <div className="flex items-center justify-between text-xs mb-1.5">
                <div className="flex items-center gap-2">
                  <span className={`w-2.5 h-2.5 rounded-full ${cat.color.bg}`} />
                  <span className="font-semibold text-slate-200">{cat.category}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-bold text-white">
                    ${cat.revenue.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
                  </span>
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${cat.color.badge} ${cat.color.text}`}>
                    {(cat.percentage_of_total || (cat.pct * 100)).toFixed(1)}%
                  </span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                <div
                  className={`h-full rounded-full ${cat.color.bg}`}
                  style={{ width: `${Math.min((cat.pct * 100), 100)}%` }}
                />
              </div>

              <div className="mt-1 flex items-center justify-between text-[11px] text-slate-400">
                <span>{cat.quantity_sold ? `${cat.quantity_sold.toLocaleString()} units sold` : ''}</span>
                <span>{cat.product_count ? `${cat.product_count} unique items` : ''}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

