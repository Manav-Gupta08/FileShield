import { useEffect, useRef, useState } from 'react';
import {
  ArrowDownToLine,
  ArrowRight,
  Check,
  CheckCircle2,
  ChevronRight,
  Copy,
  File,
  FileImage,
  FileSearch,
  Fingerprint,
  Layers,
  LockKeyhole,
  LogOut,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  Trash2,
  Upload,
  UserRound,
  X,
  AlertTriangle,
} from 'lucide-react';
import { api, type Job } from './api';

const modes = [
  { name: 'Analyze', icon: FileSearch, operation: 'release' },
  { name: 'Sanitize', icon: Sparkles, operation: 'sanitize' },
  { name: 'Convert', icon: RefreshCw, operation: 'images' },
  { name: 'Protect', icon: LockKeyhole, operation: 'protect' },
  { name: 'Security Scan', icon: ShieldCheck, operation: 'scan' },
  { name: 'Batch Tools', icon: Layers, operation: 'batch' },
];
type RecordValue = Record<string, any>;

function record(value: unknown): RecordValue {
  return value && typeof value === 'object' && !Array.isArray(value) ? (value as RecordValue) : {};
}

export default function App() {
  const [mode, setMode] = useState(0);
  const [files, setFiles] = useState<File[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [job, setJob] = useState<Job | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [ready, setReady] = useState(false);
  const [scanning, setScanning] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);
  const [authOpen, setAuthOpen] = useState(false);
  const [authRegister, setAuthRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [accountPassword, setAccountPassword] = useState('');
  const [authError, setAuthError] = useState('');
  const [format, setFormat] = useState('png');
  const [width, setWidth] = useState('');
  const [height, setHeight] = useState('');
  const [quality, setQuality] = useState(85);
  const [rotation, setRotation] = useState(0);
  const [password, setPassword] = useState('');
  const [decrypt, setDecrypt] = useState(false);
  const [pdf, setPdf] = useState(false);
  const [pages, setPages] = useState('');
  const [tab, setTab] = useState('Findings');
  const [preview, setPreview] = useState('');
  const [copied, setCopied] = useState(false);
  const picker = useRef<HTMLInputElement>(null);
  const active = modes[mode];

  async function refresh() {
    setJobs(await api<Job[]>('/jobs'));
  }

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const session = await api<{ authenticated: boolean }>('/session', { method: 'POST' });
        const health = await api<{ antivirus_required: boolean }>('/health');
        const history = await api<Job[]>('/jobs');
        if (mounted) {
          setAuthenticated(session.authenticated);
          setScanning(health.antivirus_required);
          setJobs(history);
          setReady(true);
        }
      } catch (failure) {
        if (mounted) setError(String(failure));
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    const file = files[0];
    if (!file || !['image/jpeg', 'image/png', 'image/webp', 'image/tiff'].includes(file.type)) {
      setPreview('');
      return;
    }
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [files]);

  useEffect(() => {
    if (!job || !['queued', 'processing'].includes(job.status)) return;
    let disposed = false;
    const controller = new AbortController();
    const timer = window.setInterval(async () => {
      try {
        const updated = await api<Job>(`/jobs/${job.job_id}`, { signal: controller.signal });
        if (!disposed) setJob(updated);
        if (!['queued', 'processing'].includes(updated.status) && !disposed) {
          setBusy(false);
          await refresh();
        }
      } catch (failure) {
        if (!disposed) {
          setError(String(failure));
          setBusy(false);
        }
      }
    }, 2000);
    return () => {
      disposed = true;
      controller.abort();
      window.clearInterval(timer);
    };
  }, [job?.job_id, job?.status]);

  function selectFiles(selected: File[]) {
    if (busy) return;
    const totalSize = selected.reduce((sum, file) => sum + file.size, 0);
    if (selected.length > 10 || totalSize > 25 * 1024 * 1024) {
      setError('Select up to 10 files, totaling no more than 25 MiB.');
      return;
    }
    setFiles(selected);
    setError('');
    setJob(null);
  }

  async function submit(operation?: string) {
    setError('');
    setBusy(true);
    setTab('Findings');

    try {
      const options: RecordValue = { output_format: format, quality, rotation };
      if (width || height) {
        options.width = Number(width);
        options.height = Number(height);
      }
      if (mode === 3) options.password = password;
      if (pdf && pages.trim()) {
        options.pages = pages.split(',').map((value) => Number(value.trim()) - 1);
      }

      const form = new FormData();
      files.forEach((file) => form.append('files', file));
      form.append('options', JSON.stringify(options));

      let selectedOperation = operation ?? active.operation;
      if (operation == null) {
        if (mode === 3 && decrypt) selectedOperation = 'decrypt';
        else if (mode === 2 && pdf) selectedOperation = 'pdf';
      }

      const created = await api<{ job_id: string }>(`/jobs/${selectedOperation}`, {
        method: 'POST',
        body: form,
      });
      setPassword('');
      const updated = await api<Job>(`/jobs/${created.job_id}`);
      setJob(updated);
      await refresh();
      if (updated.status === 'completed' || updated.status === 'failed') setBusy(false);
    } catch (failure) {
      setError(String(failure));
      setBusy(false);
    }
  }

  async function authenticate(event: React.FormEvent) {
    event.preventDefault();
    setAuthError('');
    try {
      await api(`/auth/${authRegister ? 'register' : 'login'}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password: accountPassword }),
      });
      setAuthenticated(true);
      setAccountPassword('');
      setAuthOpen(false);
      setJob(null);
      await refresh();
    } catch (failure) {
      setAuthError(String(failure));
    }
  }

  async function signOut() {
    try {
      await api('/auth/logout', { method: 'POST' });
      setAuthenticated(false);
      setJob(null);
      await api('/session', { method: 'POST' });
      await refresh();
    } catch (failure) {
      setError(String(failure));
    }
  }

  async function deleteJob() {
    if (!job) return;
    try {
      await api(`/files/${job.job_id}`, { method: 'DELETE' });
      setJob(null);
      await refresh();
    } catch (failure) {
      setError(String(failure));
    }
  }

  const result = record(job?.result);
  const reports: RecordValue[] = Array.isArray(result.files) ? result.files.map(record) : [];
  const report = reports[0] ?? {};
  const metadata = record(report.metadata ?? report.after ?? report.before);
  const privacy = record(metadata.privacy);
  const fileInfo = record(report.file);
  const hashes = record(report.hashes ?? result.output_hashes ?? report);
  const scans: RecordValue[] = Array.isArray(result.scans) ? result.scans.map(record) : [];
  const warnings: string[] = [
    ...(Array.isArray(fileInfo.warnings) ? fileInfo.warnings : []),
    ...(Array.isArray(record(report.pdf).findings) ? record(report.pdf).findings : []),
    ...(Array.isArray(record(report.archive).warnings) ? record(report.archive).warnings : []),
  ];
  const findingGroups = [
    { label: 'Location data', level: 'high', found: privacy.high },
    { label: 'Identity & device', level: 'medium', found: privacy.medium },
    { label: 'Time & technical data', level: 'low', found: privacy.low },
  ];

  return (
    <div className="app">
      <header className="topbar">
        <a className="brand" href="/" aria-label="FileShield workspace">
          <ShieldCheck size={28} strokeWidth={1.6} />
          <span>
            FileShield<span className="brand-dot">.</span>
          </span>
        </a>
        <div className="top-actions">
          <span className="local-badge">
            <span className="status-dot" /> {ready ? 'Workspace connected' : 'Connecting'}
          </span>
          <button className="quiet" onClick={() => (authenticated ? signOut() : setAuthOpen(true))}>
            {authenticated ? <LogOut size={16} /> : <UserRound size={16} />}
            {authenticated ? 'Sign out' : 'Sign in'}
          </button>
        </div>
      </header>
      <div className="workspace">
        <aside className="sidebar">
          <p className="label">FILE WORKSPACE</p>
          <nav aria-label="File operations">
            {modes.map((item, index) => (
              <button
                key={item.name}
                className={`nav-item ${mode === index ? 'selected' : ''}`}
                onClick={() => {
                  setMode(index);
                  setError('');
                }}
              >
                <item.icon size={19} />
                <span>{item.name}</span>
                {mode === index && <ChevronRight size={15} />}
              </button>
            ))}
          </nav>
          <div className="recent">
            <div className="section-line">
              <span className="label">RECENT JOBS</span>
              <button
                className="icon"
                title="Refresh history"
                aria-label="Refresh history"
                onClick={() => refresh().catch((failure) => setError(String(failure)))}
              >
                <RefreshCw size={14} />
              </button>
            </div>
            {jobs.length === 0 && <p className="muted small">No recent jobs</p>}
            {jobs.slice(0, 8).map((item) => (
              <button
                className="job-row"
                disabled={busy}
                key={item.job_id}
                onClick={() => {
                  setFiles([]);
                  api<Job>(`/jobs/${item.job_id}`)
                    .then(setJob)
                    .catch((failure) => setError(String(failure)));
                }}
              >
                <File size={15} />
                <span>
                  {item.operation}
                  <small>{item.job_id.slice(0, 8)}</small>
                </span>
                <span className={`job-dot ${item.status}`} title={item.status} />
              </button>
            ))}
          </div>
          <div className="sidebar-footer">
            <LockKeyhole size={16} />
            <span>
              Private by default
              <br />
              <small>Temporary file retention</small>
            </span>
          </div>
        </aside>
        <main>
          <div className="page-heading">
            <div>
              <p className="label">WORKSPACE / {active.name.toUpperCase()}</p>
              <h1>
                {mode === 0
                  ? 'Prepare for public release'
                  : active.name === 'Security Scan'
                    ? 'Security scan'
                    : `${active.name} files`}
              </h1>
            </div>
            <span className="phase-badge">LOCAL PROCESSING</span>
          </div>
          {!scanning && ready && (
            <div className="notice">
              <AlertTriangle size={17} />
              <span>
                Development mode: antivirus scanning is disabled. Results are not security
                clearance.
              </span>
            </div>
          )}
          {error && (
            <div className="error" role="alert">
              <AlertTriangle size={17} />
              <span>{error}</span>
              <button className="icon" aria-label="Dismiss error" onClick={() => setError('')}>
                <X size={16} />
              </button>
            </div>
          )}
          <section className="input-section">
            <div className="section-line">
              <h2>Input files</h2>
              <span className="muted small">25 MiB total limit</span>
            </div>
            <div
              className={`dropzone ${files.length ? 'has-files' : ''}`}
              onDragOver={(event) => event.preventDefault()}
              onDrop={(event) => {
                event.preventDefault();
                selectFiles(Array.from(event.dataTransfer.files));
              }}
            >
              <input
                ref={picker}
                type="file"
                multiple={mode === 5 || pdf}
                hidden
                onChange={(event) => selectFiles(Array.from(event.target.files ?? []))}
              />
              {preview ? (
                <img className="file-preview" src={preview} alt="Selected input preview" />
              ) : (
                <div className="upload-symbol">
                  <Upload size={27} strokeWidth={1.4} />
                </div>
              )}
              <div className="drop-copy">
                <h3>
                  {files.length
                    ? `${files.length} file${files.length > 1 ? 's' : ''} selected`
                    : 'Drop your file here'}
                </h3>
                <p>
                  {files.length
                    ? files.map((file) => file.name).join(', ')
                    : 'Images, PDFs, archives, or files to protect'}
                </p>
              </div>
              <button className="secondary" disabled={busy} onClick={() => picker.current?.click()}>
                <FileImage size={16} />
                {files.length ? 'Change files' : 'Choose file'}
              </button>
            </div>
            {(mode === 1 || mode === 2 || mode === 5) && (
              <div className="controls">
                {mode === 2 && (
                  <label className="checkbox">
                    <input
                      type="checkbox"
                      checked={pdf}
                      onChange={(event) => setPdf(event.target.checked)}
                    />
                    PDF pages / merge
                  </label>
                )}
                {!pdf && (
                  <>
                    <label>
                      Output format
                      <select value={format} onChange={(event) => setFormat(event.target.value)}>
                        <option value="png">PNG</option>
                        <option value="jpeg">JPEG</option>
                        <option value="webp">WebP</option>
                        <option value="tiff">TIFF</option>
                      </select>
                    </label>
                    <label>
                      Maximum width
                      <input
                        type="number"
                        min="1"
                        max="10000"
                        placeholder="Original"
                        value={width}
                        onChange={(event) => setWidth(event.target.value)}
                      />
                    </label>
                    <label>
                      Maximum height
                      <input
                        type="number"
                        min="1"
                        max="10000"
                        placeholder="Original"
                        value={height}
                        onChange={(event) => setHeight(event.target.value)}
                      />
                    </label>
                    <label>
                      Quality <span>{quality}</span>
                      <input
                        type="range"
                        min="1"
                        max="100"
                        value={quality}
                        onChange={(event) => setQuality(Number(event.target.value))}
                      />
                    </label>
                  </>
                )}
                {pdf && (
                  <label className="wide">
                    Pages (1-based, comma separated)
                    <input
                      value={pages}
                      onChange={(event) => setPages(event.target.value)}
                      placeholder="All pages"
                    />
                  </label>
                )}
                <label>
                  Rotation
                  <select
                    value={rotation}
                    onChange={(event) => setRotation(Number(event.target.value))}
                  >
                    {[0, 90, 180, 270].map((value) => (
                      <option key={value} value={value}>
                        {value} degrees
                      </option>
                    ))}
                  </select>
                </label>
              </div>
            )}
            {mode === 3 && (
              <div className="controls">
                <label className="checkbox">
                  <input
                    type="checkbox"
                    checked={decrypt}
                    onChange={(event) => setDecrypt(event.target.checked)}
                  />
                  Remove known protection
                </label>
                <label className="wide">
                  {decrypt ? 'Existing password' : 'Encryption password'}
                  <input
                    type="password"
                    autoComplete="off"
                    minLength={12}
                    maxLength={256}
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                  />
                </label>
              </div>
            )}
            <div className="action-line">
              <span className="muted small">
                <LockKeyhole size={13} />
                Inputs deleted after processing; results expire after one hour by default.
              </span>
              <button
                className="primary"
                disabled={!files.length || busy || !ready}
                onClick={() => submit()}
              >
                {busy
                  ? 'Processing'
                  : mode === 0
                    ? 'Analyze file'
                    : mode === 3 && decrypt
                      ? 'Remove protection'
                      : active.name}
                <ArrowRight size={17} />
              </button>
            </div>
          </section>
          <section className="results-section" aria-live="polite">
            <div className="section-line">
              <h2>Release report</h2>
              {job && <span className={`state ${job.status}`}>{job.status}</span>}
            </div>
            {!job ? (
              <div className="empty-results">
                <Fingerprint size={38} strokeWidth={1.1} />
                <div>
                  <h3>No report yet</h3>
                  <p className="muted">Awaiting file analysis</p>
                </div>
                <div className="empty-columns">
                  <span>File identity</span>
                  <span>Privacy findings</span>
                  <span>Integrity</span>
                </div>
              </div>
            ) : (
              <>
                <div className="report-title">
                  <FileSearch size={21} />
                  <div>
                    <h3>{job.filenames?.join(', ') ?? job.operation}</h3>
                    <p className="muted small">
                      Expires {new Date(job.expires * 1000).toLocaleString()}
                    </p>
                  </div>
                  <button
                    className="icon danger"
                    aria-label="Delete files and report"
                    title="Delete files and report"
                    disabled={['queued', 'processing'].includes(job.status)}
                    onClick={deleteJob}
                  >
                    <Trash2 size={17} />
                  </button>
                </div>
                {job.error && (
                  <div className="error" role="alert">
                    {job.error}
                  </div>
                )}
                {['queued', 'processing'].includes(job.status) && (
                  <div className="processing">
                    <RefreshCw className="spin" size={22} />
                    {job.status === 'queued'
                      ? 'Waiting for a worker'
                      : 'Analyzing in isolated process'}
                  </div>
                )}
                {job.status === 'completed' && (
                  <>
                    <div className="tabs" role="tablist">
                      {['Findings', 'Metadata', 'Integrity'].map((name) => (
                        <button
                          key={name}
                          role="tab"
                          aria-selected={tab === name}
                          className={tab === name ? 'active' : ''}
                          onClick={() => setTab(name)}
                        >
                          {name}
                        </button>
                      ))}
                    </div>
                    {tab === 'Findings' && (
                      <div className="findings-layout">
                        <div className="finding-list">
                          <div className="finding-row">
                            <span>File identification</span>
                            <strong>{fileInfo.detected_mime ?? job.operation}</strong>
                          </div>
                          {findingGroups.map((group) => (
                            <div className="finding-row" key={group.label}>
                              <span>{group.label}</span>
                              <span
                                className={group.found?.length ? `risk ${group.level}` : 'muted'}
                              >
                                {group.found
                                  ? group.found.length
                                    ? `${group.found.length} found`
                                    : 'Not found'
                                  : 'Not assessed'}
                              </span>
                            </div>
                          ))}
                          {scans.map((scan, index) => (
                            <div className="finding-row" key={index}>
                              <span>Malware scan {scans.length > 1 ? index + 1 : ''}</span>
                              <span className={scan.status === 'clean' ? 'success' : 'risk medium'}>
                                {scan.status === 'clean' ? 'No detection' : scan.status}
                              </span>
                            </div>
                          ))}
                          {warnings.map((warning, index) => (
                            <div className="warning-row" key={index}>
                              <AlertTriangle size={16} />
                              <span>{warning}</span>
                            </div>
                          ))}
                          {Array.isArray(report.removed_exif_fields) && (
                            <div className="warning-row success">
                              <CheckCircle2 size={16} />
                              <span>{report.removed_exif_fields.length} EXIF fields removed</span>
                            </div>
                          )}
                        </div>
                        <div className="score-panel">
                          <p className="label">PRIVACY RISK</p>
                          <div className="score">
                            {privacy.score ?? '--'}
                            <span>/ 100</span>
                          </div>
                          <div className="score-track">
                            <span style={{ width: `${privacy.score ?? 0}%` }} />
                          </div>
                          <p className="muted small">
                            {privacy.score == null
                              ? 'Not assessed for this operation'
                              : 'EXIF-based heuristic, not a safety verdict'}
                          </p>
                        </div>
                      </div>
                    )}
                    {tab === 'Metadata' && (
                      <div className="metadata-table">
                        {Object.entries(record(metadata.exif)).length ? (
                          Object.entries(record(metadata.exif)).map(([key, value]) => (
                            <div className="finding-row" key={key}>
                              <span>{key}</span>
                              <code>
                                {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                              </code>
                            </div>
                          ))
                        ) : (
                          <p className="muted">No image EXIF reported for this operation.</p>
                        )}
                        <details>
                          <summary>Full analysis record</summary>
                          <pre>{JSON.stringify(result, null, 2)}</pre>
                        </details>
                      </div>
                    )}
                    {tab === 'Integrity' && (
                      <div className="hashes">
                        {['sha256', 'sha512'].map((name) => (
                          <div key={name}>
                            <p className="label">{name.toUpperCase()}</p>
                            <div className="hash-value">
                              <code>{hashes[name] ?? 'Not reported'}</code>
                              <button
                                className="icon"
                                aria-label={`Copy ${name}`}
                                title={`Copy ${name}`}
                                disabled={!hashes[name]}
                                onClick={() =>
                                  navigator.clipboard
                                    .writeText(hashes[name])
                                    .then(() => {
                                      setCopied(true);
                                      window.setTimeout(() => setCopied(false), 1500);
                                    })
                                    .catch((failure) => setError(String(failure)))
                                }
                              >
                                {copied ? <Check size={17} /> : <Copy size={17} />}
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                    <div className="report-actions">
                      <span className="muted small">
                        <ShieldCheck size={14} />
                        No analysis can guarantee a file is safe.
                      </span>
                      {job.download_available ? (
                        <a className="primary" href={`/api/v1/files/${job.job_id}`}>
                          <ArrowDownToLine size={16} />
                          Download result
                        </a>
                      ) : (
                        mode === 0 &&
                        files.length === 1 && (
                          <button
                            className="primary"
                            onClick={() => {
                              setMode(1);
                              submit('sanitize');
                            }}
                            disabled={busy}
                          >
                            <Sparkles size={16} />
                            Sanitize for release
                          </button>
                        )
                      )}
                    </div>
                  </>
                )}
              </>
            )}
          </section>
          <footer className="footer">
            <span>FileShield / File privacy workspace</span>
            <a href="/api/v1/health" target="_blank" rel="noreferrer">
              Service status <ArrowRight size={12} />
            </a>
          </footer>
        </main>
      </div>
      {authOpen && (
        <div className="modal-backdrop">
          <section
            className="auth-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="auth-heading"
          >
            <button
              className="icon close-modal"
              aria-label="Close sign in"
              onClick={() => {
                setAuthOpen(false);
                setAccountPassword('');
              }}
            >
              <X size={18} />
            </button>
            <h2 id="auth-heading">{authRegister ? 'Create account' : 'Sign in'}</h2>
            <form onSubmit={authenticate}>
              <label>
                Username
                <input
                  autoComplete="username"
                  required
                  minLength={3}
                  maxLength={64}
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                />
              </label>
              <label>
                Password
                <input
                  type="password"
                  autoComplete={authRegister ? 'new-password' : 'current-password'}
                  required
                  minLength={12}
                  maxLength={256}
                  value={accountPassword}
                  onChange={(event) => setAccountPassword(event.target.value)}
                />
              </label>
              {authError && (
                <p className="error" role="alert">
                  {authError}
                </p>
              )}
              <button className="primary" type="submit">
                {authRegister ? 'Create account' : 'Sign in'}
                <ArrowRight size={16} />
              </button>
            </form>
            <button className="quiet" onClick={() => setAuthRegister(!authRegister)}>
              {authRegister ? 'Use existing account' : 'Create account'}
            </button>
          </section>
        </div>
      )}
    </div>
  );
}
