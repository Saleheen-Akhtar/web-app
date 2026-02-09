import React, { useEffect, useState } from 'react';
import api, { getDashboard, getHistory, uploadFile } from '../services/api';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend);

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [selectedUploadId, setSelectedUploadId] = useState(null);

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
      // Handle "No uploads found"
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
      // Refresh
      fetchHistory();
      fetchDashboard(res.data.id);
      setSelectedUploadId(res.data.id);
    } catch (error) {
      setUploadError('Upload failed: ' + (error.response?.data?.error || error.message));
    } finally {
      setUploadLoading(false);
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
            })
            .catch((err) => console.error(err));
    }
  };

  if (loading && !data) return <div>Loading...</div>;

  return (
    <div className="container mt-4">
      <div className="row mb-4">
        <div className="col-md-8">
          <h2>Dashboard {data ? `- Upload ${data.upload_id}` : ''}</h2>
        </div>
        <div className="col-md-4 text-end">
          <input type="file" onChange={handleUpload} className="form-control" accept=".csv" disabled={uploadLoading} />
          {uploadError && <div className="text-danger mt-1">{uploadError}</div>}
        </div>
      </div>

      <div className="row">
        <div className="col-md-3">
          <h4>History</h4>
          <ul className="list-group">
            {history.map((item) => (
              <li
                key={item.id}
                className={`list-group-item ${selectedUploadId === item.id ? 'active' : ''}`}
                onClick={() => setSelectedUploadId(item.id)}
                style={{ cursor: 'pointer' }}
              >
                Upload {item.id} <br/>
                <small>{new Date(item.uploaded_at).toLocaleString()}</small>
              </li>
            ))}
          </ul>
        </div>

        <div className="col-md-9">
          {data ? (
            <>
              <div className="row mb-4">
                <div className="col-md-3">
                    <div className="card text-white bg-primary mb-3">
                        <div className="card-body">
                            <h5 className="card-title">Count</h5>
                            <p className="card-text">{data.summary.count}</p>
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="card text-white bg-success mb-3">
                        <div className="card-body">
                            <h5 className="card-title">Avg Flow</h5>
                            <p className="card-text">{data.summary.avg_flowrate?.toFixed(2)}</p>
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="card text-white bg-info mb-3">
                        <div className="card-body">
                            <h5 className="card-title">Avg Press</h5>
                            <p className="card-text">{data.summary.avg_pressure?.toFixed(2)}</p>
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="card text-white bg-warning mb-3">
                        <div className="card-body">
                            <h5 className="card-title">Avg Temp</h5>
                            <p className="card-text">{data.summary.avg_temperature?.toFixed(2)}</p>
                        </div>
                    </div>
                </div>
              </div>

              <div className="row mb-4">
                <div className="col-md-6">
                    <h5>Equipment Types</h5>
                    <Bar
                        data={{
                            labels: data.summary.type_distribution.map(d => d.equipment_type),
                            datasets: [{
                                label: 'Count',
                                data: data.summary.type_distribution.map(d => d.count),
                                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                            }]
                        }}
                    />
                </div>
                <div className="col-md-6">
                    <h5>Parameters Overview</h5>
                    <Line
                        data={{
                            labels: data.data.map(d => d.equipment_name), // Or just indices if too many
                            datasets: [
                                {
                                    label: 'Flowrate',
                                    data: data.data.map(d => d.flowrate),
                                    borderColor: 'rgb(75, 192, 192)',
                                    tension: 0.1
                                },
                                {
                                    label: 'Pressure',
                                    data: data.data.map(d => d.pressure),
                                    borderColor: 'rgb(255, 99, 132)',
                                    tension: 0.1
                                },
                                {
                                    label: 'Temperature',
                                    data: data.data.map(d => d.temperature),
                                    borderColor: 'rgb(255, 205, 86)',
                                    tension: 0.1
                                }
                            ]
                        }}
                    />
                </div>
              </div>

              <div className="mb-4">
                <button className="btn btn-secondary mb-2" onClick={handleDownloadPDF}>Download PDF Report</button>
                <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                    <table className="table table-striped">
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
                                    <td>{row.equipment_name}</td>
                                    <td>{row.equipment_type}</td>
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
            <div className="alert alert-info">No data available. Please upload a CSV file.</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
