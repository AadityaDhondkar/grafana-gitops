import { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, Download, RotateCcw } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE_URL;

type Version = {
  hash: string;
  label: string;
};

function App() {
  const [versions, setVersions] = useState<Version[]>([]);
  const [selectedVersion, setSelectedVersion] = useState('');
  const [currentVersion, setCurrentVersion] = useState<string | null>(null);

  const [status, setStatus] = useState<{
    type: 'success' | 'error' | '';
    message: string;
  }>({ type: '', message: '' });

  const [isExporting, setIsExporting] = useState(false);
  const [isRollingBack, setIsRollingBack] = useState(false);
  const [isLoadingVersions, setIsLoadingVersions] = useState(true);

  useEffect(() => {
    fetchVersions();
    fetchCurrent();
  }, []);

  // ======================
  // Fetch versions
  // ======================
  const fetchVersions = async () => {
    setIsLoadingVersions(true);
    try {
      const res = await fetch(`${API_BASE}/api/versions`);
      if (!res.ok) throw new Error('Failed to fetch versions');
      const data: Version[] = await res.json();

      setVersions(data);
      if (data.length > 0) setSelectedVersion(data[0].hash);
      setStatus({ type: '', message: '' });
    } catch (err) {
      setStatus({
        type: 'error',
        message: err instanceof Error ? err.message : 'Unknown error'
      });
    } finally {
      setIsLoadingVersions(false);
    }
  };

  // ======================
  // Fetch current version
  // ======================
  const fetchCurrent = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/current`);
      const data = await res.json();
      setCurrentVersion(data.current);
    } catch {
      setCurrentVersion(null);
    }
  };

  // ======================
  // Export
  // ======================
  const handleExport = async () => {
    setIsExporting(true);
    setStatus({ type: '', message: '' });

    try {
      const res = await fetch(`${API_BASE}/api/export`, { method: 'POST' });
      const data = await res.json();

      if (!res.ok) throw new Error(data.message);

      setStatus({
        type: 'success',
        message: data.message
      });

      fetchVersions();
      fetchCurrent();
    } catch (err) {
      setStatus({
        type: 'error',
        message: err instanceof Error ? err.message : 'Export failed'
      });
    } finally {
      setIsExporting(false);
    }
  };

  // ======================
  // Rollback
  // ======================
  const handleRollback = async () => {
    setIsRollingBack(true);
    setStatus({ type: '', message: '' });

    try {
      const res = await fetch(`${API_BASE}/api/rollback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ version: selectedVersion })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.message);

      setCurrentVersion(data.current);
      setStatus({ type: 'success', message: data.message });
    } catch (err) {
      setStatus({
        type: 'error',
        message: err instanceof Error ? err.message : 'Rollback failed'
      });
    } finally {
      setIsRollingBack(false);
    }
  };

  const isSameVersion = selectedVersion === currentVersion;

  // ======================
  // UI
  // ======================
  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-2xl mx-auto bg-white p-6 rounded border">
        <h1 className="text-2xl font-semibold mb-1">
          Grafana GitOps Dashboard Manager
        </h1>
        <p className="text-gray-600 mb-6">
          One-click dashboard versioning & rollback
        </p>

        <button
          onClick={handleExport}
          disabled={isExporting}
          className="mb-6 px-4 py-2 bg-blue-600 text-white rounded"
        >
          <Download size={16} className="inline mr-2" />
          {isExporting ? 'Exporting...' : 'Export Dashboard'}
        </button>

        <select
          className="w-full mb-4 p-2 border rounded"
          value={selectedVersion}
          onChange={(e) => setSelectedVersion(e.target.value)}
          disabled={isLoadingVersions}
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

        <button
          onClick={handleRollback}
          disabled={isRollingBack || isSameVersion}
          className="px-4 py-2 bg-green-600 text-white rounded"
        >
          <RotateCcw size={16} className="inline mr-2" />
          {isSameVersion ? 'Already Applied' : 'Apply Selected Version'}
        </button>

        {currentVersion && (
          <p className="mt-3 text-xs text-gray-500">
            Current version: <b>{currentVersion}</b>
          </p>
        )}

        {status.message && (
          <div
            className={`mt-6 p-3 rounded border ${
              status.type === 'success'
                ? 'bg-green-50 text-green-800'
                : 'bg-red-50 text-red-800'
            }`}
          >
            {status.type === 'success' ? (
              <CheckCircle size={18} className="inline mr-2" />
            ) : (
              <AlertCircle size={18} className="inline mr-2" />
            )}
            {status.message}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
