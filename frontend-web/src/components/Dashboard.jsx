import React, { useEffect, useState } from 'react';
import api, { getDashboard, getHistory, uploadFile, deleteUpload } from '../services/api';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend, Filler, ArcElement } from 'chart.js';
import { Bar, Line, Doughnut } from 'react-chartjs-2';
import {
  Upload, Download, Clock, Activity, Thermometer,
  Gauge, Droplets, BarChart3, FileText, ChevronRight,
  Loader2, AlertTriangle, Database, Trash2, X
} from 'lucide-react';

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, ArcElement, Title, Tooltip, Legend, Filler);

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        padding: 20,
        usePointStyle: true,
        pointStyleWidth: 10,
        font: { size: 12, family: "'Inter', sans-serif" }
      }
    },
    tooltip: {
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      titleFont: { size: 13, family: "'Inter', sans-serif" },
      bodyFont: { size: 12, family: "'Inter', sans-serif" },
      padding: 12,
      cornerRadius: 8,
      boxPadding: 6,
    }
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { font: { size: 11, family: "'Inter', sans-serif" }, color: '#94a3b8' }
    },
    y: {
      grid: { color: 'rgba(148, 163, 184, 0.1)' },
      ticks: { font: { size: 11, family: "'Inter', sans-serif" }, color: '#94a3b8' }
    }
  }
};

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '65%',
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        padding: 16,
        usePointStyle: true,
        pointStyleWidth: 10,
        font: { size: 12, family: "'Inter', sans-serif" }
      }
    },
    tooltip: {
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      padding: 12,
      cornerRadius: 8,
    }
  }
};

const COLORS = [
  'rgba(99, 102, 241, 0.8)',
  'rgba(16, 185, 129, 0.8)',
  'rgba(245, 158, 11, 0.8)',
  'rgba(239, 68, 68, 0.8)',
  'rgba(14, 165, 233, 0.8)',
  'rgba(168, 85, 247, 0.8)',
  'rgba(236, 72, 153, 0.8)',
];

const Dashboard = ({ onLogout, username }) => {
  const [data, setData] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [selectedUploadId, setSelectedUploadId] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [deleteModal, setDeleteModal] = useState({ open: false, uploadId: null, filename: '' });

  useEffect(() => {
    fetchHistory();
    fetchDashboard(null);
  }, []);

  useEffect(() => {
    if (selectedUploadId) {
      fetchDashboard(selectedUploadId);
    }
  }, [selectedUploadId]);

  const fetchDashboard = async (id) => {
    setLoading(true);
    try {
      const response = await getDashboard(id);
      setData(response.data);
    } catch (error) {
      console.error('Failed to fetch dashboard', error);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await getHistory();
      setHistory(response.data);
    } catch (error) {
      console.error('Failed to fetch history', error);
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploadLoading(true);
    setUploadError('');
    try {
      const res = await uploadFile(file);
      fetchHistory();
      fetchDashboard(res.data.id);
      setSelectedUploadId(res.data.id);
    } catch (error) {
      setUploadError('Upload failed: ' + (error.response?.data?.error || error.message));
    } finally {
      setUploadLoading(false);
      e.target.value = '';
    }
  };

  const handleDownloadPDF = () => {
    if (data?.upload_id) {
      api.get(`report/${data.upload_id}/`, { responseType: 'blob' })
        .then((response) => {
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', `report_${data.upload_id}.pdf`);
          document.body.appendChild(link);
          link.click();
          link.remove();
        })
        .catch((err) => console.error(err));
    }
  };

  const handleDelete = async (e, uploadId) => {
    e.stopPropagation();
    const item = history.find(h => h.id === uploadId);
    setDeleteModal({ open: true, uploadId, filename: item?.original_filename || `Upload #${uploadId}` });
  };

  const confirmDelete = async () => {
    const { uploadId } = deleteModal;
    setDeleteModal({ open: false, uploadId: null, filename: '' });
    try {
      await deleteUpload(uploadId);
      const res = await getHistory();
      const updatedHistory = res.data;
      setHistory(updatedHistory);

      if (selectedUploadId === uploadId) {
        if (updatedHistory.length > 0) {
          const nextId = updatedHistory[0].id;
          setSelectedUploadId(nextId);
          fetchDashboard(nextId);
        } else {
          setSelectedUploadId(null);
          setData(null);
        }
      }
    } catch (error) {
      console.error('Failed to delete upload', error);
    }
  };

  const StatCard = ({ icon: Icon, label, value, color, bgColor }) => (
    <div className="stat-card">
      <div className="stat-card-icon" style={{ backgroundColor: bgColor, color: color }}>
        <Icon size={22} />
      </div>
      <div className="stat-card-content">
        <span className="stat-label">{label}</span>
        <span className="stat-value">{value}</span>
      </div>
    </div>
  );

  return (
    <div className="dashboard-layout">
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : 'collapsed'}`}>
        <div className="sidebar-header">
          <h3>Uploads</h3>
          <span className="badge">{history.length}</span>
        </div>

        <label className="upload-zone">
          <input type="file" onChange={handleUpload} accept=".csv" disabled={uploadLoading} hidden />
          {uploadLoading ? (
            <Loader2 size={20} className="spin" />
          ) : (
            <Upload size={20} />
          )}
          <span>{uploadLoading ? 'Uploading...' : 'Upload CSV'}</span>
        </label>

        {uploadError && (
          <div className="upload-error">
            <AlertTriangle size={14} />
            <span>{uploadError}</span>
          </div>
        )}

        <div className="sidebar-list">
          {history.length === 0 ? (
            <div className="sidebar-empty">
              <Database size={32} />
              <span>No uploads yet</span>
            </div>
          ) : (
            history.map((item) => (
              <div
                key={item.id}
                className={`sidebar-item ${selectedUploadId === item.id ? 'active' : ''}`}
                onClick={() => setSelectedUploadId(item.id)}
              >
                <div className="sidebar-item-icon">
                  <FileText size={16} />
                </div>
                <div className="sidebar-item-content">
                  <span className="sidebar-item-title">{item.original_filename || `Upload #${item.id}`}</span>
                  <span className="sidebar-item-meta">
                    <Clock size={12} />
                    {new Date(item.uploaded_at).toLocaleDateString('en-US', {
                      month: 'short', day: 'numeric', year: 'numeric',
                      hour: '2-digit', minute: '2-digit'
                    })}
                  </span>
                </div>
                <button
                  className="sidebar-item-delete"
                  onClick={(e) => handleDelete(e, item.id)}
                  title="Delete upload"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main className="dashboard-main">
        {loading && !data ? (
          <div className="dashboard-loading">
            <Loader2 size={40} className="spin" />
            <p>Loading dashboard data...</p>
          </div>
        ) : data ? (
          <>
            {/* Page Header */}
            <div className="dashboard-header">
              <div>
                <h1>Dashboard</h1>
                <p className="dashboard-subtitle">Upload #{data.upload_id} overview</p>
              </div>
              <button className="btn-pdf" onClick={handleDownloadPDF}>
                <Download size={16} />
                <span>Export PDF</span>
              </button>
            </div>

            {/* Stats Row */}
            <div className="stats-grid">
              <StatCard
                icon={Database}
                label="Total Equipment"
                value={data.summary.count}
                color="#6366f1"
                bgColor="rgba(99, 102, 241, 0.1)"
              />
              <StatCard
                icon={Droplets}
                label="Avg. Flowrate"
                value={data.summary.avg_flowrate?.toFixed(2)}
                color="#10b981"
                bgColor="rgba(16, 185, 129, 0.1)"
              />
              <StatCard
                icon={Gauge}
                label="Avg. Pressure"
                value={data.summary.avg_pressure?.toFixed(2)}
                color="#0ea5e9"
                bgColor="rgba(14, 165, 233, 0.1)"
              />
              <StatCard
                icon={Thermometer}
                label="Avg. Temperature"
                value={data.summary.avg_temperature?.toFixed(2)}
                color="#f59e0b"
                bgColor="rgba(245, 158, 11, 0.1)"
              />
            </div>

            {/* Charts Row */}
            <div className="charts-grid">
              <div className="chart-card">
                <div className="chart-card-header">
                  <BarChart3 size={18} />
                  <h3>Equipment Type Distribution</h3>
                </div>
                <div className="chart-container">
                  <Doughnut
                    data={{
                      labels: data.summary.type_distribution.map(d => d.equipment_type),
                      datasets: [{
                        data: data.summary.type_distribution.map(d => d.count),
                        backgroundColor: COLORS,
                        borderWidth: 0,
                        hoverOffset: 6,
                      }]
                    }}
                    options={doughnutOptions}
                  />
                </div>
              </div>
              <div className="chart-card">
                <div className="chart-card-header">
                  <Activity size={18} />
                  <h3>Parameter Trends</h3>
                </div>
                <div className="chart-container">
                  <Line
                    data={{
                      labels: data.data.map((d, i) => d.equipment_name || `#${i + 1}`),
                      datasets: [
                        {
                          label: 'Flowrate',
                          data: data.data.map(d => d.flowrate),
                          borderColor: 'rgba(16, 185, 129, 1)',
                          backgroundColor: 'rgba(16, 185, 129, 0.1)',
                          fill: true,
                          tension: 0.4,
                          pointRadius: 2,
                          pointHoverRadius: 5,
                        },
                        {
                          label: 'Pressure',
                          data: data.data.map(d => d.pressure),
                          borderColor: 'rgba(239, 68, 68, 1)',
                          backgroundColor: 'rgba(239, 68, 68, 0.1)',
                          fill: true,
                          tension: 0.4,
                          pointRadius: 2,
                          pointHoverRadius: 5,
                        },
                        {
                          label: 'Temperature',
                          data: data.data.map(d => d.temperature),
                          borderColor: 'rgba(245, 158, 11, 1)',
                          backgroundColor: 'rgba(245, 158, 11, 0.1)',
                          fill: true,
                          tension: 0.4,
                          pointRadius: 2,
                          pointHoverRadius: 5,
                        }
                      ]
                    }}
                    options={chartOptions}
                  />
                </div>
              </div>
            </div>

            {/* Equipment Bar Chart */}
            <div className="chart-card full-width">
              <div className="chart-card-header">
                <BarChart3 size={18} />
                <h3>Equipment Count by Type</h3>
              </div>
              <div className="chart-container-bar">
                <Bar
                  data={{
                    labels: data.summary.type_distribution.map(d => d.equipment_type),
                    datasets: [{
                      label: 'Count',
                      data: data.summary.type_distribution.map(d => d.count),
                      backgroundColor: COLORS,
                      borderRadius: 8,
                      borderSkipped: false,
                      maxBarThickness: 60,
                    }]
                  }}
                  options={chartOptions}
                />
              </div>
            </div>

            {/* Data Table */}
            <div className="table-card">
              <div className="table-card-header">
                <div>
                  <h3>Equipment Data</h3>
                  <p>{data.data.length} records</p>
                </div>
              </div>
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Type</th>
                      <th>Flowrate</th>
                      <th>Pressure</th>
                      <th>Temperature</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.data.map((row) => (
                      <tr key={row.id}>
                        <td className="td-name">{row.equipment_name}</td>
                        <td>
                          <span className="type-badge">{row.equipment_type}</span>
                        </td>
                        <td>{row.flowrate}</td>
                        <td>{row.pressure}</td>
                        <td>{row.temperature}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        ) : (
          <div className="dashboard-empty">
            <div className="empty-illustration">
              <Upload size={64} strokeWidth={1} />
            </div>
            <h2>No Data Available</h2>
            <p>Upload a CSV file from the sidebar to get started with your equipment analytics.</p>
          </div>
        )}
      </main>

      {/* Delete Confirmation Modal */}
      {deleteModal.open && (
        <div className="modal-overlay" onClick={() => setDeleteModal({ open: false, uploadId: null, filename: '' })}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setDeleteModal({ open: false, uploadId: null, filename: '' })}>
              <X size={18} />
            </button>
            <div className="modal-icon">
              <Trash2 size={28} />
            </div>
            <h3>Delete Upload</h3>
            <p>Are you sure you want to delete <strong>{deleteModal.filename}</strong>? This action cannot be undone.</p>
            <div className="modal-actions">
              <button className="modal-btn cancel" onClick={() => setDeleteModal({ open: false, uploadId: null, filename: '' })}>Cancel</button>
              <button className="modal-btn delete" onClick={confirmDelete}>Delete</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
