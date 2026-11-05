import React from 'react';
import { Award, DollarSign, Package } from 'lucide-react';

export default function ProductRanking({
  data = [],
  sortBy,
  setSortBy,
  limit,
  setLimit
}) {
  if (!data || data.length === 0) {
    return (
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md flex flex-col items-center justify-center min-h-[340px] text-slate-500">
        <Award className="w-10 h-10 mb-2 stroke-1 opacity-40" />
        <p className="text-sm">No product ranking data available</p>
      </div>
    );
  }

  const maxVal = Math.max(
    ...data.map(d => (sortBy === 'revenue' ? d.revenue : d.quantity_sold)),
    1
  );

  return (
    <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md shadow-xl flex flex-col justify-between">
      {/* Header and Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Award className="w-5 h-5 text-amber-400" />
            Top Performing Products
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Ranked by {sortBy === 'revenue' ? 'total revenue generated' : 'total volume sold'}
          </p>
        </div>

        {/* Sort and Limit Controls */}
        <div className="flex items-center gap-2">
          {/* Sort By Toggle */}
          <div className="flex rounded-lg bg-slate-950 p-1 border border-slate-800 text-xs">
            <button
              onClick={() => setSortBy('revenue')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-medium transition ${
                sortBy === 'revenue' ? 'bg-amber-500/20 text-amber-400 shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              <DollarSign className="w-3.5 h-3.5" />
              Revenue
            </button>
            <button
              onClick={() => setSortBy('quantity_sold')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-medium transition ${
                sortBy === 'quantity_sold' ? 'bg-blue-500/20 text-blue-400 shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Package className="w-3.5 h-3.5" />
              Units
            </button>
          </div>

          {/* Limit dropdown */}
          <select
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            className="bg-slate-950 border border-slate-800 text-slate-300 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-slate-600"
          >
            <option value={5}>Top 5</option>
            <option value={10}>Top 10</option>
            <option value={20}>Top 20</option>
          </select>
        </div>
      </div>

      {/* Product List */}
      <div className="space-y-3 max-h-[380px] overflow-y-auto pr-1">
        {data.map((item, idx) => {
          const val = sortBy === 'revenue' ? item.revenue : item.quantity_sold;
          const pct = Math.min((val / maxVal) * 100, 100);

          const rankBadge =
            idx === 0
              ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
              : idx === 1
              ? 'bg-slate-300/20 text-slate-200 border-slate-300/40'
              : idx === 2
              ? 'bg-amber-800/30 text-amber-600 border-amber-700/40'
              : 'bg-slate-800 text-slate-400 border-slate-700';

          return (
            <div
              key={idx}
              className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-slate-700 transition"
            >
              <div className="flex items-center justify-between text-xs mb-1.5">
                <div className="flex items-center gap-2.5 truncate max-w-[70%]">
                  <span className={`w-6 h-6 flex items-center justify-center rounded-lg text-[11px] font-bold border ${rankBadge}`}>
                    {idx + 1}
                  </span>
                  <span className="font-semibold text-slate-200 truncate">{item.product_name}</span>
                </div>
                <div className="text-right">
                  <span className="font-bold text-white text-sm">
                    {sortBy === 'revenue'
                      ? `$${item.revenue.toLocaleString(undefined, { minimumFractionDigits: 2 })}`
                      : `${item.quantity_sold.toLocaleString()} units`}
                  </span>
                </div>
              </div>

              {/* Bar visualization */}
              <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    sortBy === 'revenue' ? 'bg-amber-400' : 'bg-blue-400'
                  }`}
                  style={{ width: `${pct}%` }}
                />
              </div>

              {/* Secondary stats */}
              <div className="mt-1.5 flex items-center justify-between text-[11px] text-slate-400">
                <span>Avg Price: ${item.average_price?.toFixed(2) || '0.00'}</span>
                <span>
                  {sortBy === 'revenue'
                    ? `${item.quantity_sold?.toLocaleString()} units sold`
                    : `Revenue: $${item.revenue?.toLocaleString()}`}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

