import { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, Download, RotateCcw } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE_URL;
console.log("API_BASE:", API_BASE);

// Version shape coming from backend
type Version = {
  hash: string;
  label: string;
};

function App() {
  const [versions, setVersions] = useState<Version[]>([]);
  const [selectedVersion, setSelectedVersion] = useState<string>('');
  const [status, setStatus] = useState<{ type: 'success' | 'error' | ''; message: string }>({
    type: '',
    message: ''
  });

  const [isExporting, setIsExporting] = useState(false);
  const [isRollingBack, setIsRollingBack] = useState(false);
  const [isLoadingVersions, setIsLoadingVersions] = useState(true);

  useEffect(() => {
    fetchVersions();
  }, []);

  // =========================
  // Fetch versions from backend
  // =========================
  const fetchVersions = async () => {
    setIsLoadingVersions(true);
    try {
      const response = await fetch(`${API_BASE}/api/versions`);
      if (!response.ok) throw new Error('Failed to fetch versions');

      const raw: string[] = await response.json();

      // Convert "88e7c73 v4 Dashboard update"
      // into { hash: "88e7c73", label: "88e7c73 v4 Dashboard update" }
      const parsed: Version[] = raw.map((line) => {
        const [hash] = line.split(' ');
        return {
          hash,
          label: line
        };
      });

      setVersions(parsed);
      if (parsed.length > 0) {
        setSelectedVersion(parsed[0].hash);
      }

      setStatus({ type: '', message: '' });
    } catch (error) {
      setStatus({
        type: 'error',
        message: `Error fetching versions: ${
          error instanceof Error ? error.message : 'Unknown error'
        }`
      });
    } finally {
      setIsLoadingVersions(false);
    }
  };

  // =========================
  // Export dashboard
  // =========================
  const handleExport = async () => {
    setIsExporting(true);
    setStatus({ type: '', message: '' });

    try {
      const response = await fetch(`${API_BASE}/api/export`, { method: 'POST' });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Export failed');
      }

      setStatus({
        type: 'success',
        message: data.message || 'Dashboard exported successfully'
      });

      fetchVersions();
    } catch (error) {
      setStatus({
        type: 'error',
        message: `Export failed: ${
          error instanceof Error ? error.message : 'Unknown error'
        }`
      });
    } finally {
      setIsExporting(false);
    }
  };

  // =========================
  // Rollback dashboard
  // =========================
  const handleRollback = async () => {
    if (!selectedVersion) {
      setStatus({ type: 'error', message: 'Please select a version to rollback' });
      return;
    }

    setIsRollingBack(true);
    setStatus({ type: '', message: '' });

    try {
      const response = await fetch(`${API_BASE}/api/rollback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        // IMPORTANT: send only commit hash
        body: JSON.stringify({ version: selectedVersion })
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.details || data.message || 'Rollback failed');
      }

      setStatus({
        type: 'success',
        message: data.message || `Rolled back to ${selectedVersion}`
      });
    } catch (error) {
      setStatus({
        type: 'error',
        message: `Rollback failed: ${
          error instanceof Error ? error.message : 'Unknown error'
        }`
      });
    } finally {
      setIsRollingBack(false);
    }
  };

  // =========================
  // UI
  // =========================
  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="mb-8">
            <h1 className="text-2xl font-semibold text-gray-900 mb-1">
              Grafana GitOps Dashboard Manager
            </h1>
            <p className="text-gray-600">
              One-click dashboard versioning & rollback
            </p>
          </div>

          <div className="space-y-6">
            {/* Export */}
            <div className="border-b border-gray-200 pb-6">
              <h2 className="text-sm font-medium text-gray-700 mb-3">Export Dashboard</h2>
              <button
                onClick={handleExport}
                disabled={isExporting}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
              >
                <Download size={18} />
                {isExporting ? 'Exporting...' : 'Export Dashboard'}
              </button>
            </div>

            {/* Versions */}
            <div className="border-b border-gray-200 pb-6">
              <h2 className="text-sm font-medium text-gray-700 mb-3">
                Available Dashboard Versions
              </h2>
              <select
                value={selectedVersion}
                onChange={(e) => setSelectedVersion(e.target.value)}
                disabled={isLoadingVersions || versions.length === 0}
                className="w-full px-3 py-2 border border-gray-300 rounded"
              >
                {isLoadingVersions ? (
                  <option>Loading versions...</option>
                ) : versions.length === 0 ? (
                  <option>No versions available</option>
                ) : (
                  versions.map((v) => (
                    <option key={v.hash} value={v.hash}>
                      {v.label}
                    </option>
                  ))
                )}
              </select>
            </div>

            {/* Rollback */}
            <div className="border-b border-gray-200 pb-6">
              <h2 className="text-sm font-medium text-gray-700 mb-3">Rollback</h2>
              <button
                onClick={handleRollback}
                disabled={isRollingBack || !selectedVersion}
                className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400"
              >
                <RotateCcw size={18} />
                {isRollingBack ? 'Applying...' : 'Apply Selected Version'}
              </button>
            </div>

            {/* Status */}
            {status.message && (
              <div
                className={`p-4 rounded border ${
                  status.type === 'success'
                    ? 'bg-green-50 border-green-200 text-green-800'
                    : 'bg-red-50 border-red-200 text-red-800'
                }`}
              >
                <div className="flex gap-2">
                  {status.type === 'success' ? (
                    <CheckCircle size={20} />
                  ) : (
                    <AlertCircle size={20} />
                  )}
                  <p className="text-sm">{status.message}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
