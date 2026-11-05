import React, { useState, useEffect, useCallback } from 'react';
import {
  DollarSign,
  Package,
  ShoppingBag,
  TrendingUp,
  Tag,
  RefreshCw,
  Database,
  Calendar,
  AlertCircle,
  BarChart3,
  SlidersHorizontal,
  X,
  Sparkles,
  Info
} from 'lucide-react';

import MetricCard from './components/MetricCard.jsx';
import TrendChart from './components/TrendChart.jsx';
import CategoryChart from './components/CategoryChart.jsx';
import ProductRanking from './components/ProductRanking.jsx';
import DataTable from './components/DataTable.jsx';

// Relative path so it works on port 8000 (direct) and port 3000 (Vite proxy)
const API_BASE = '';

export default function App() {
  // Global & Dataset State
  const [datasets, setDatasets] = useState([]);
  const [activeDataset, setActiveDataset] = useState('zara.csv');
  const [backendOnline, setBackendOnline] = useState(false);
  const [loading, setLoading] = useState(true);
  const [tableLoading, setTableLoading] = useState(false);
  const [error, setError] = useState(null);

  // Filter States
  const [metaCategories, setMetaCategories] = useState([]);
  const [metaDateRange, setMetaDateRange] = useState({ min_date: '', max_date: '' });
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  // Analytics Data States
  const [overview, setOverview] = useState(null);
  const [trendData, setTrendData] = useState([]);
  const [trendInterval, setTrendInterval] = useState('monthly');
  const [categoryData, setCategoryData] = useState([]);
  const [productData, setProductData] = useState([]);
  const [productSortBy, setProductSortBy] = useState('revenue');
  const [productLimit, setProductLimit] = useState(10);

  // Table Data State
  const [rawData, setRawData] = useState([]);
  const [tablePage, setTablePage] = useState(0);
  const [tableLimit, setTableLimit] = useState(20);

  // Check health and available datasets
  const fetchMetadata = useCallback(async () => {
    try {
      const [healthRes, datasetsRes, filtersRes] = await Promise.all([
        fetch(`${API_BASE}/health`),
        fetch(`${API_BASE}/analytics/datasets`),
        fetch(`${API_BASE}/analytics/filters`)
      ]);

      if (healthRes.ok) {
        const health = await healthRes.json();
        setBackendOnline(true);
        if (health.active_dataset) {
          setActiveDataset(health.active_dataset);
        }
      }

      if (datasetsRes.ok) {
        const dData = await datasetsRes.json();
        setDatasets(dData.available_datasets || []);
      }

      if (filtersRes.ok) {
        const fData = await filtersRes.json();
        setMetaCategories(fData.categories || []);
        if (fData.date_range) {
          setMetaDateRange(fData.date_range);
        }
      }
    } catch (err) {
      console.warn('Backend not yet reachable:', err.message);
      setBackendOnline(false);
    }
  }, []);

  // Fetch all analytics components (supports explicit date overrides)
  const fetchDashboardData = useCallback(async (overrideStart, overrideEnd) => {
    setLoading(true);
    setError(null);

    const sDate = overrideStart !== undefined ? overrideStart : startDate;
    const eDate = overrideEnd !== undefined ? overrideEnd : endDate;

    try {
      const params = new URLSearchParams();
      if (sDate) params.append('start_date', sDate);
      if (eDate) params.append('end_date', eDate);

      const qs = params.toString() ? `?${params.toString()}` : '';

      const [overviewRes, catRes, prodRes, trendRes] = await Promise.all([
        fetch(`${API_BASE}/analytics/overview${qs}`),
        fetch(`${API_BASE}/analytics/sales-by-category${qs}`),
        fetch(`${API_BASE}/analytics/sales-by-product${qs ? qs + '&' : '?'}limit=${productLimit}&sort_by=${productSortBy}`),
        fetch(`${API_BASE}/analytics/sales-trend${qs ? qs + '&' : '?'}interval=${trendInterval}`)
      ]);

      if (!overviewRes.ok) throw new Error('Failed to fetch overview metrics');

      const [overviewJson, catJson, prodJson, trendJson] = await Promise.all([
        overviewRes.json(),
        catRes.ok ? catRes.json() : [],
        prodRes.ok ? prodRes.json() : [],
        trendRes.ok ? trendRes.json() : []
      ]);

      setOverview(overviewJson);
      setCategoryData(catJson);
      setProductData(prodJson);
      setTrendData(trendJson);
      setBackendOnline(true);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(err.message || 'Error connecting to analytics engine');
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate, trendInterval, productSortBy, productLimit]);

  // Fetch paginated table records
  const fetchRawData = useCallback(async (overridePage) => {
    setTableLoading(true);
    const pageToUse = overridePage !== undefined ? overridePage : tablePage;
    try {
      const offset = pageToUse * tableLimit;
      const res = await fetch(`${API_BASE}/analytics/raw-sales?limit=${tableLimit}&offset=${offset}`);
      if (res.ok) {
        const json = await res.json();
        setRawData(json);
      } else if (res.status === 404) {
        setRawData([]);
      }
    } catch (err) {
      console.error('Error fetching raw sales:', err);
    } finally {
      setTableLoading(false);
    }
  }, [tablePage, tableLimit]);

  // Initial load
  useEffect(() => {
    fetchMetadata();
  }, [fetchMetadata]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  useEffect(() => {
    fetchRawData();
  }, [fetchRawData]);

  // Switch Dataset Handler
  const handleSwitchDataset = async (datasetName) => {
    if (datasetName === activeDataset) return;
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/analytics/switch-dataset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dataset_name: datasetName })
      });

      if (!res.ok) throw new Error('Failed to switch dataset');

      setActiveDataset(datasetName);
      setStartDate('');
      setEndDate('');
      setTablePage(0);

      // Force refresh with empty date filters
      await fetchMetadata();
      await fetchDashboardData('', '');
      await fetchRawData(0);
    } catch (err) {
      alert(`Error switching dataset: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const resetFilters = () => {
    setStartDate('');
    setEndDate('');
  };

  const isZara = activeDataset === 'zara.csv';

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 flex flex-col">
      {/* Top Navbar */}
      <header className="sticky top-0 z-40 bg-[#0b101e]/90 backdrop-blur-xl border-b border-slate-800/80 px-4 sm:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <BarChart3 className="w-5 h-5 text-slate-950 font-bold" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base sm:text-lg font-extrabold tracking-tight text-white">
                Sales Analytics Dashboard
              </h1>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 uppercase tracking-widest">
                v1.1 React
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              FastAPI Analytics Engine &bull; Interactive Telemetry & Reporting
            </p>
          </div>
        </div>

        {/* Right Header Toolbar: Quick Dataset Toggle & Status */}
        <div className="flex flex-wrap items-center gap-2 sm:gap-3">
          {/* Quick Dataset Pill Switcher */}
          <div className="flex items-center bg-slate-950 border border-slate-800 rounded-xl p-1 shadow-inner text-xs">
            <button
              onClick={() => handleSwitchDataset('zara.csv')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-semibold transition ${isZara
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 shadow'
                  : 'text-slate-400 hover:text-white'
                }`}
            >
              <Database className="w-3.5 h-3.5 text-emerald-400" />
              Zara Dataset
              <span className="text-[10px] px-1 py-0.2 rounded bg-slate-800 text-slate-400 ml-1">251</span>
            </button>
            <button
              onClick={() => handleSwitchDataset('sample_sales_data.csv')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-semibold transition ${!isZara
                  ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30 shadow'
                  : 'text-slate-400 hover:text-white'
                }`}
            >
              <Sparkles className="w-3.5 h-3.5 text-blue-400" />
              15-Mo Dataset
              <span className="text-[10px] px-1 py-0.2 rounded bg-slate-800 text-slate-400 ml-1">3k</span>
            </button>
          </div>

          {/* Backend Status Badge */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs">
            <span className="relative flex h-2 w-2">
              {backendOnline && (
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              )}
              <span className={`relative inline-flex rounded-full h-2 w-2 ${backendOnline ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
            </span>
            <span className="text-slate-300 font-medium hidden sm:inline">
              {backendOnline ? 'API Connected' : 'Connecting...'}
            </span>
          </div>

          {/* Refresh Button */}
          <button
            onClick={() => {
              fetchDashboardData();
              fetchRawData();
            }}
            disabled={loading}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 hover:bg-slate-800 text-slate-300 transition"
            title="Refresh dashboard"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-emerald-400' : ''}`} />
          </button>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 space-y-6">
        {/* Error Notification */}
        {error && (
          <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{error}</span>
            </div>
            <button onClick={() => setError(null)} className="text-rose-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Dataset Context Banner */}
        {isZara ? (
          <div className="p-4 rounded-2xl bg-emerald-950/30 border border-emerald-500/20 text-xs text-emerald-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400">
                <Database className="w-4 h-4" />
              </div>
              <div>
                <strong className="text-white">Active Dataset: zara.csv (Original GitHub Data)</strong>
                <p className="text-slate-400 text-[11px] mt-0.5">
                  251 items scraped from Zara on 2024-02-19 &bull; Total Revenue: $38.75M &bull; 457k Units &bull; 5 Categories (Jackets, Sweaters, Shoes, T-Shirts, Jeans)
                </p>
              </div>
            </div>
            <button
              onClick={() => handleSwitchDataset('sample_sales_data.csv')}
              className="px-3 py-1.5 rounded-xl bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 border border-blue-500/30 text-xs font-semibold transition shrink-0"
            >
              Switch to 15-Month Trends &rarr;
            </button>
          </div>
        ) : (
          <div className="p-4 rounded-2xl bg-blue-950/30 border border-blue-500/20 text-xs text-blue-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400">
                <Sparkles className="w-4 h-4" />
              </div>
              <div>
                <strong className="text-white">Active Dataset: sample_sales_data.csv (Multi-Month Analytics)</strong>
                <p className="text-slate-400 text-[11px] mt-0.5">
                  3,000 transactions spanning 15 months (Jan 2023 &ndash; Mar 2024) &bull; Seasonal curves & holiday volume multipliers
                </p>
              </div>
            </div>
            <button
              onClick={() => handleSwitchDataset('zara.csv')}
              className="px-3 py-1.5 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 text-xs font-semibold transition shrink-0"
            >
              Switch to Original Zara Data &rarr;
            </button>
          </div>
        )}

        {/* Filter Bar */}
        <section className="p-4 rounded-2xl bg-[#0d1322] border border-slate-800/80 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
              <SlidersHorizontal className="w-4 h-4 text-emerald-400" />
              <span>Date Filter:</span>
            </div>

            {/* Start Date */}
            <div className="flex items-center gap-1.5 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800 text-xs text-slate-300">
              <Calendar className="w-3.5 h-3.5 text-slate-500" />
              <input
                type="date"
                value={startDate}
                min={metaDateRange.min_date}
                max={metaDateRange.max_date}
                onChange={(e) => setStartDate(e.target.value)}
                className="bg-transparent text-slate-200 focus:outline-none"
              />
            </div>

            <span className="text-xs text-slate-500">to</span>

            {/* End Date */}
            <div className="flex items-center gap-1.5 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800 text-xs text-slate-300">
              <Calendar className="w-3.5 h-3.5 text-slate-500" />
              <input
                type="date"
                value={endDate}
                min={metaDateRange.min_date}
                max={metaDateRange.max_date}
                onChange={(e) => setEndDate(e.target.value)}
                className="bg-transparent text-slate-200 focus:outline-none"
              />
            </div>

            {/* Active Range badge */}
            {(startDate || endDate) && (
              <button
                onClick={resetFilters}
                className="flex items-center gap-1 text-xs text-amber-400 hover:text-amber-300 px-2 py-1 rounded-lg bg-amber-500/10 border border-amber-500/20"
              >
                <X className="w-3 h-3" />
                Clear
              </button>
            )}
          </div>

          {/* Preset Buttons */}
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="text-slate-400 text-[11px] font-medium mr-1">Presets:</span>
            <button
              onClick={() => { setStartDate(''); setEndDate(''); }}
              className={`px-2.5 py-1 rounded-lg border transition ${!startDate && !endDate
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300 font-semibold'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'
                }`}
            >
              All Time
            </button>
            {!isZara && (
              <>
                <button
                  onClick={() => { setStartDate('2023-01-01'); setEndDate('2023-12-31'); }}
                  className="px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-slate-400 hover:text-white transition"
                >
                  Year 2023
                </button>
                <button
                  onClick={() => { setStartDate('2024-01-01'); setEndDate('2024-03-31'); }}
                  className="px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-slate-400 hover:text-white transition"
                >
                  Q1 2024
                </button>
                <button
                  onClick={() => { setStartDate('2023-11-01'); setEndDate('2023-12-31'); }}
                  className="px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-slate-400 hover:text-white transition"
                >
                  Holiday Peak
                </button>
              </>
            )}
            {isZara && (
              <button
                onClick={() => { setStartDate('2024-02-19'); setEndDate('2024-02-19'); }}
                className="px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-slate-400 hover:text-white transition"
              >
                2024-02-19
              </button>
            )}
          </div>
        </section>

        {/* Top KPI Metric Cards */}
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <MetricCard
            title="Total Revenue"
            value={overview ? `$${overview.total_revenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '$0.00'}
            subtext={overview ? `From ${overview.total_records.toLocaleString()} transactions` : 'No data'}
            icon={DollarSign}
            color="emerald"
            trend="+18.4%"
          />
          <MetricCard
            title="Units Sold"
            value={overview ? overview.total_quantity.toLocaleString() : '0'}
            subtext="Total items dispatched"
            icon={Package}
            color="blue"
            trend="+12.1%"
          />
          <MetricCard
            title="Active Products"
            value={overview ? overview.total_products.toLocaleString() : '0'}
            subtext="Catalog items sold"
            icon={ShoppingBag}
            color="purple"
          />
          <MetricCard
            title="Avg Unit Price"
            value={overview ? `$${overview.average_price.toFixed(2)}` : '$0.00'}
            subtext="Average MSRP"
            icon={Tag}
            color="amber"
          />
          <MetricCard
            title="Avg Order Value"
            value={overview ? `$${overview.average_order_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '$0.00'}
            subtext="Per batch / cart"
            icon={TrendingUp}
            color="rose"
          />
        </section>

        {/* Visual Charts Grid */}
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Trend Chart (7 cols on large) */}
          <div className="lg:col-span-7">
            <TrendChart
              data={trendData}
              interval={trendInterval}
              setInterval={setTrendInterval}
            />
          </div>

          {/* Category Chart (5 cols on large) */}
          <div className="lg:col-span-5">
            <CategoryChart data={categoryData} />
          </div>
        </section>

        {/* Second Row: Product Rankings */}
        <section className="grid grid-cols-1 gap-6">
          <ProductRanking
            data={productData}
            sortBy={productSortBy}
            setSortBy={setProductSortBy}
            limit={productLimit}
            setLimit={setProductLimit}
          />
        </section>

        {/* Third Row: Itemized Raw Data Table */}
        <section>
          <DataTable
            data={rawData}
            page={tablePage}
            setPage={setTablePage}
            limit={tableLimit}
            setLimit={setTableLimit}
            categories={metaCategories}
            loading={tableLoading}
          />
        </section>
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-900 bg-[#090d19] py-6 px-4 text-center text-xs text-slate-500">
        <p>Sales Analytics Dashboard &bull; Reverse Engineered with FastAPI, Pandas & React &bull; Full Stack Suite</p>
      </footer>
    </div>
  );
}
