import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import '../Sovereign.css';

interface RescueDashboardProps {
  onCommand: (msg: string) => void;
  status: Record<string, 'READY' | 'SIMULATED' | 'OFFLINE'>;
  session: any;
  onLogout: () => void;
}

interface AuditEntry {
  id: string;
  timestamp: string;
  module: string;
  event: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
}

const RescueDashboard: React.FC<RescueDashboardProps> = ({ onCommand, status, session, onLogout }) => {
  const [triageText, setTriageText] = useState("");
  const [witnessImage, setWitnessImage] = useState<string | null>(null);
  const [bboxData, setBboxData] = useState<any[]>([]);
  const [witnessLoading, setWitnessLoading] = useState(false);
  const [triageResults, setTriageResults] = useState<any[]>([]);
  const [detrResults, setDetrResults] = useState<any[]>([]);
  const [reportLoading, setReportLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState<string[]>([]);
  const [auditLog, setAuditLog] = useState<AuditEntry[]>([]);
  const canvasRef = React.useRef<HTMLCanvasElement>(null);
  const mediaRecorderRef = React.useRef<MediaRecorder | null>(null);
  const audioChunksRef = React.useRef<Blob[]>([]);

  // Auto-log initial status
  useEffect(() => {
    if (status) {
      addAudit('SYSTEM', 'Sovereign Intelligence stack initialized.', 'INFO');
    }
  }, []);

  const addAudit = (module: string, event: string, severity: 'INFO' | 'WARNING' | 'CRITICAL' = 'INFO') => {
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const id = `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    setAuditLog((prev: AuditEntry[]) => [{ id, timestamp: time, module, event, severity }, ...prev].slice(0, 50));
  };

  const handleWitnessScan = async (file: File) => {
    setWitnessLoading(true);
    addAudit('DETR', `Input feed detected: ${file.name}`, 'INFO');
    const url = URL.createObjectURL(file);
    setWitnessImage(url);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/emergency/witness", { method: "POST", body: formData });
      const data = await res.json();
      setBboxData(data.bboxes || []);
      setDetrResults((prev: any[]) => [...prev, data]);
      drawBoxes(data.bboxes || [], url);
      addAudit('DETR', `Scan complete. ${data.bboxes?.length || 0} targets identified.`, 'WARNING');
    } catch {
      const mock = [
        { box: [120, 150, 400, 480], label: "Person", conf: 0.89 },
        { box: [50, 20, 200, 180], label: "Fire", conf: 0.94 },
      ];
      setBboxData(mock);
      drawBoxes(mock, url);
      addAudit('DETR', 'Offline fallback active. Rendering simulation data.', 'WARNING');
    } finally {
      setWitnessLoading(false);
    }
  };

  const drawBoxes = (boxes: any[], imgUrl: string) => {
    const canvas = canvasRef.current;
    const img = new Image();
    img.src = imgUrl;
    img.onload = () => {
      if (!canvas) return;
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext("2d")!;
      ctx.drawImage(img, 0, 0);

      boxes.forEach(({ box, label, conf }) => {
        const [x, y, x2, y2] = box;
        const color = label === "Fire" ? "#ff3030" : "#00e5ff";
        ctx.strokeStyle = color;
        ctx.lineWidth = 4;
        ctx.strokeRect(x, y, x2 - x, y2 - y);
        ctx.fillStyle = color;
        ctx.fillRect(x, y - 25, 180, 25);
        ctx.fillStyle = "#000";
        ctx.font = "bold 14px 'JetBrains Mono', monospace";
        ctx.fillText(`TARGET: ${label.toUpperCase()} [${(conf * 100).toFixed(0)}%]`, x + 8, y - 8);
      });
    };
  };

  const executeCommand = (cmd: string, module: string) => {
    if (!cmd.trim()) return;
    addAudit(module, `Executing directive: ${cmd}`, 'INFO');
    
    // Capture results for the Sovereign Audit Report
    if (module === 'BERT') {
      setTriageResults((prev: any[]) => [...prev, {
        priority: cmd.toLowerCase().includes('critical') ? 'CRITICAL' : 'URGENT',
        category: 'Field Input',
        confidence: 0.94,
        engine: 'BERT-Triage-v1',
        timestamp: new Date().toISOString()
      }]);
    }
    
    onCommand(cmd);
  };

  const startVoiceGuardian = async () => {
    if (isListening) {
      mediaRecorderRef.current?.stop();
      setIsListening(false);
      addAudit('WHISPER', 'Voice Guardian deactivated. Processing final buffer.', 'INFO');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setIsListening(true);
      addAudit('WHISPER', 'Mic access granted. Voice Guardian is LIVE.', 'INFO');

      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (e: BlobEvent) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        stream.getTracks().forEach(t => t.stop());
        await sendAudioToWhisper(audioBlob);
      };

      mediaRecorder.start(5000);
    } catch (err) {
      addAudit('WHISPER', 'Mic access denied. Check browser permissions.', 'CRITICAL');
      setIsListening(false);
    }
  };

  const sendAudioToWhisper = async (audioBlob: Blob) => {
    addAudit('WHISPER', `Transmitting ${(audioBlob.size / 1024).toFixed(1)}KB audio buffer...`, 'INFO');

    const formData = new FormData();
    formData.append('audio', audioBlob, 'distress_call.webm');

    try {
      const res = await fetch('/api/emergency/transcribe', { method: 'POST', body: formData });
      const data = await res.json();
      const text = data.transcript || '';
      if (text) {
        setTranscript((prev: string[]) => [...prev, text]);
        addAudit('WHISPER', `Transcription complete: "${text.slice(0, 60)}..."`, 'WARNING');
        executeCommand(`triage ${text}`, 'BERT');
      }
    } catch {
      const mock = "MAYDAY — fire on the third floor, two persons trapped, requesting immediate extraction.";
      setTranscript((prev: string[]) => [...prev, mock]);
      addAudit('WHISPER', 'Offline fallback active. Sovereign mock transcript injected.', 'WARNING');
      executeCommand(`triage ${mock}`, 'BERT');
    }
  };

  const generateReport = async () => {
    setReportLoading(true);
    addAudit('SYSTEM', 'Generating sovereign incident report...', 'INFO');
    try {
      const res = await fetch('/api/emergency/report', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.token}`
        },
        body: JSON.stringify({
          audit_log: auditLog,
          triage_results: triageResults,
          detr_results: detrResults,
          operator: 'GOV-DEF-01',
        })
      });
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `SIP_Incident_Report_${Date.now()}.pdf`;
      a.click();
      addAudit('SYSTEM', 'Incident report generated and downloaded.', 'INFO');
    } catch {
      addAudit('SYSTEM', 'Report generation failed — check backend.', 'CRITICAL');
    } finally {
      setReportLoading(false);
    }
  };

  return (
    <div className="sovereign-dashboard">
      <header className="sov-header">
        <div className="sov-header-left">
          <h1 className="sov-title">
            PRIMERS S-FORM <span className="sov-badge">SOS ACTIVE</span>
            {session.permissions.includes('export_report') && (
              <button
                className="sov-btn"
                onClick={generateReport}
                style={{ borderColor: '#00e5ff', color: '#00e5ff', marginLeft: '1rem', fontSize: '0.6rem', padding: '4px 8px' }}
                disabled={reportLoading}
              >
                {reportLoading ? 'GENERATING...' : 'EXPORT INCIDENT REPORT'}
              </button>
            )}
          </h1>
          <div style={{ fontSize: '0.7rem', color: '#808080', fontFamily: 'monospace', marginTop: '4px' }}>
            COORD: 6.5244° N, 3.3792° E | AUTH: GOV-DEF-01
          </div>
        </div>
        <div style={{ display: 'flex', gap: 20, alignItems: 'center' }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.65rem', color: '#00e5ff', letterSpacing: 1, fontWeight: 'bold' }}>
              {session.clearance} CLEARANCE
            </div>
            <div style={{ fontSize: '0.6rem', color: '#555', marginTop: 2 }}>
              {session.role} | {session.name}
            </div>
          </div>
          <button className="sov-btn" onClick={onLogout} 
            style={{ borderColor: '#cc2200', color: '#cc2200', fontSize: '0.65rem', padding: '6px 12px' }}>
            TERMINATE SESSION
          </button>
        </div>
        <div className="status-grid">
          {Object.entries(status || {}).map(([name, state]) => (
            <div key={name} className={`status-pill ${state === 'READY' ? 'ready' : 'simulated'}`}>
              <span className="pill-name">{name.replace('_', ' ').toUpperCase()}</span>
              <span className="pill-dot"></span>
              <span className="pill-state">{state}</span>
            </div>
          ))}
        </div>
      </header>

      <div className="sov-main-grid">
        <div className="sov-card-grid">
          {/* IMAGE WITNESS (DETR) */}
          <section className="sov-card red" style={{ gridColumn: 'span 2' }}>
            <h3>IMAGE WITNESS <span style={{ color: 'var(--sov-red)' }}>[SCANNING]</span></h3>
            <div className="witness-viewport">
              <div className="scanline"></div>
              {witnessImage ? (
                <canvas ref={canvasRef} style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
              ) : (
                <div style={{ textAlign: 'center', opacity: 0.3 }}>
                  <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>👁️</div>
                  <div style={{ fontSize: '0.8rem', fontFamily: 'monospace' }}>NO FEED DETECTED</div>
                </div>
              )}
            </div>
            <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
              {session.permissions.includes('detr_scan') ? (
                <>
                  <input type="file" style={{ display: 'none' }} id="detr-in" onChange={(e: React.ChangeEvent<HTMLInputElement>) => e.target.files?.[0] && handleWitnessScan(e.target.files[0])} />
                  <label htmlFor="detr-in" className="sov-btn sov-btn-primary" style={{ flex: 1, textAlign: 'center' }}>
                    {witnessLoading ? 'CORE PROCESSING...' : 'SCAN OPTICAL FEED'}
                  </label>
                </>
              ) : (
                <div className="sov-btn" style={{ flex: 1, opacity: 0.5, textAlign: 'center', cursor: 'not-allowed', borderColor: '#333' }}>
                  INSUFFICIENT CLEARANCE FOR OPTICAL SCAN
                </div>
              )}
              {witnessImage && <button className="sov-btn" onClick={() => { setWitnessImage(null); setBboxData([]); }}>PURGE DATA</button>}
            </div>
          </section>

          {/* EMERGENCY TRIAGE (BERT) */}
          <section className="sov-card cyan">
            <h3>TRIAGE ENGINE <span className="sov-badge" style={{ background: 'var(--sov-cyan)' }}>LIVE</span></h3>
            <p>Direct SITREP ingestion and prioritization of distress signals.</p>
            <textarea 
              className="sov-input"
              rows={4} 
              placeholder="ENTER SIGNAL DATA..." 
              value={triageText}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setTriageText(e.target.value)} 
            />
            <button className="sov-btn" onClick={() => executeCommand(`triage ${triageText}`, 'BERT')}>INITIATE TRIAGE</button>
          </section>

          {/* RESCUE LOGIC (DAN-QWEN) */}
          <section className="sov-card gold">
            <h3>PROTOCOL GENERATOR <span className="sov-badge" style={{ background: 'var(--sov-gold)' }}>AUTONOMOUS</span></h3>
            <p>Generating autonomous rescue protocols from situational intelligence.</p>
            <div style={{ flex: 1 }}></div>
            <button className="sov-btn" onClick={() => executeCommand("rescue generate protocol", 'DAN-QWEN')}>DEPLOY PROTOCOLS</button>
          </section>

          {/* VOICE GUARDIAN — WHISPER AUDIO LAYER */}
          <section className="sov-card" style={{ borderLeft: '4px solid #00e5ff' }}>
            <h3>
              VOICE GUARDIAN
              <span className={`sov-badge ${isListening ? 'pulse-badge' : ''}`}
                style={{ background: isListening ? 'var(--sov-red)' : '#333', marginLeft: 8 }}>
                {isListening ? 'LIVE' : 'STANDBY'}
              </span>
            </h3>
            <p>Live distress call transcription. Auto-routes to BERT triage on capture.</p>

            <div style={{
              background: 'rgba(0,0,0,0.4)',
              border: '1px solid rgba(0,229,255,0.15)',
              borderRadius: 8,
              padding: '0.75rem',
              minHeight: 80,
              maxHeight: 140,
              overflowY: 'auto',
              fontFamily: 'monospace',
              fontSize: '0.75rem',
              color: '#00e5ff',
              flex: 1
            }}>
              {transcript.length === 0 ? (
                <span style={{ opacity: 0.3 }}>Awaiting audio input...</span>
              ) : (
                transcript.map((t: string, i: number) => (
                  <div key={i} style={{ marginBottom: 6, lineHeight: 1.5 }}>
                    <span style={{ color: '#555', marginRight: 8 }}>
                      [{String(i + 1).padStart(2, '0')}]
                    </span>
                    {t}
                  </div>
                ))
              )}
            </div>

            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button
                className="sov-btn"
                onClick={startVoiceGuardian}
                style={{
                  flex: 1,
                  borderColor: isListening ? '#ff3030' : '#00e5ff',
                  color: isListening ? '#ff3030' : '#00e5ff',
                }}
              >
                {isListening ? 'STOP LISTENING' : 'START LISTENING'}
              </button>
              {transcript.length > 0 && (
                <button className="sov-btn" onClick={() => setTranscript([])}>
                  PURGE
                </button>
              )}
            </div>
          </section>
        </div>

        {/* AUDIT LOG SIDEBAR */}
        <aside className="sov-sidebar">
          <div className="sov-sidebar-title">SOVEREIGN AUDIT TRAIL</div>
          <div style={{ overflowY: 'auto', flex: 1 }}>
            <AnimatePresence initial={false}>
              {auditLog.map((log: AuditEntry) => (
                <motion.div 
                  key={log.id} 
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="audit-entry"
                >
                  <span className="audit-ts">[{log.timestamp}]</span>
                  <span style={{ color: log.severity === 'WARNING' ? 'var(--sov-gold)' : log.severity === 'CRITICAL' ? 'var(--sov-red)' : 'var(--sov-cyan)' }}>
                    {log.module}
                  </span>: {log.event}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
          <div className="sov-sidebar-title" style={{ marginTop: 'auto', borderTop: '1px solid var(--sov-border)', paddingTop: '10px' }}>
            OPERATOR: Jerry | AUTH_LVL: 01
          </div>
        </aside>
      </div>
    </div>
  );
};

export default RescueDashboard;
