import React, { useState, useRef, useEffect } from 'react';

const API_BASE = "https://job-intelligence-engine-nu.vercel.app";

function CopyIcon({ size = 14 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
    </svg>
  );
}

function CheckIcon({ size = 14 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12"/>
    </svg>
  );
}

function DownloadIcon({ size = 14 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
    </svg>
  );
}

function CopyInput({ label, value, onChange, type = 'text', multiline = false }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!value) return;
    navigator.clipboard.writeText(value).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    });
  };

  const sharedInputStyle = {
    fontFamily: multiline ? 'inherit' : "'DM Mono', monospace",
    minHeight: multiline ? 160 : undefined,
  };

  return (
    <div className="flex flex-col gap-1.5 flex-1 min-h-0">
      <div className="flex items-center justify-between">
        <label
          className="text-[10px] font-medium tracking-[0.1em] text-zinc-500 uppercase"
          style={{ fontFamily: "'DM Mono', monospace" }}>
          {label}
        </label>
        <button
          onClick={handleCopy}
          title={`Copiar ${label.toLowerCase()}`}
          className="flex items-center gap-1 text-[10px] px-2 py-1 rounded-lg transition-all cursor-pointer"
          style={{
            fontFamily: "'DM Mono', monospace",
            color: copied ? '#4edea3' : '#52525b',
            background: copied ? 'rgba(78,222,163,0.08)' : 'transparent',
            border: copied ? '1px solid rgba(78,222,163,0.2)' : '1px solid transparent',
          }}
          onMouseEnter={e => { if (!copied) e.currentTarget.style.color = '#a1a1aa'; }}
          onMouseLeave={e => { if (!copied) e.currentTarget.style.color = '#52525b'; }}>
          {copied ? <CheckIcon /> : <CopyIcon />}
          <span>{copied ? 'Copiado' : 'Copiar'}</span>
        </button>
      </div>

      {multiline ? (
        <textarea
          value={value}
          onChange={e => onChange(e.target.value)}
          className="flex-1 bg-[#1a1a1d] border border-white/[0.07] rounded-xl p-3.5 text-[13px] text-zinc-300 outline-none focus:border-[#4edea3]/30 transition-colors resize-none w-full leading-relaxed"
          style={sharedInputStyle}
        />
      ) : (
        <input
          type={type}
          value={value}
          onChange={e => onChange(e.target.value)}
          className="bg-[#1a1a1d] border border-white/[0.07] rounded-xl px-3.5 py-2.5 text-[13px] text-white outline-none focus:border-[#4edea3]/30 transition-colors w-full"
          style={sharedInputStyle}
        />
      )}
    </div>
  );
}

export default function ChatBot() {
  const [messages, setMessages] = useState([
    { role: 'bot', text: '¡Hola! Pegá la URL de una oferta de empleo y genero el mail y el CV personalizado.' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [analysisCount, setAnalysisCount] = useState(0);
  const [emailPreview, setEmailPreview] = useState({ to: '', asunto: '', cuerpo: '' });
  const [scrapedData, setScrapedData] = useState(null);
  const [hasPreview, setHasPreview] = useState(false);
  const [copied, setCopied] = useState(false);
  const [pdfBase64, setPdfBase64] = useState(null);
  const [downloadState, setDownloadState] = useState('idle'); // idle | loading | done | error
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const addMsg = (text, role) => setMessages(prev => [...prev, { role, text }]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;
    const url = input.trim();
    addMsg(url, 'user');
    setInput('');
    setIsLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/process-job`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Error del servidor');

      if (data.email_preview) {
        const parsed = typeof data.email_preview === 'string'
          ? JSON.parse(data.email_preview)
          : data.email_preview;

        setEmailPreview({
          to: data.contact_email || '',
          asunto: parsed.asunto || `Postulación — ${data.job_title || 'Vacante'}`,
          cuerpo: parsed.cuerpo || parsed
        });

        setScrapedData({
          title: data.job_title || 'Vacante',
          company: data.company || 'No especificada',
          description: data.description || 'No especificada',
          email: data.contact_email || ''
        });

        setPdfBase64(data.cv_pdf_base64 || null);
        setHasPreview(true);
        setDownloadState('idle');
        setAnalysisCount(c => c + 1);
        addMsg(`✓ Oferta analizada: ${data.job_title || 'Sin título'}`, 'bot');
      } else {
        addMsg(data.message || 'Análisis completado.', 'bot');
      }
    } catch (e) {
      addMsg(`Error: ${e.message}`, 'bot');
    } finally {
      setIsLoading(false);
    }
  };

  const copyEmail = () => {
    const full = `Asunto: ${emailPreview.asunto}\n\n${emailPreview.cuerpo}`;
    navigator.clipboard.writeText(full).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const downloadCV = async () => {
    if (!scrapedData || !scrapedData.title || isLoading) {
      alert("Primero debés procesar una oferta válida para poder adaptar tu CV.");
      return;
    }

    try {
      setDownloadState('loading');

      const response = await fetch(`${API_BASE}/api/generate-pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scraped_data: {
            title: scrapedData.title,
            company: scrapedData.company,
            description: scrapedData.description,
            email: scrapedData.email
          }
        })
      });

      if (!response.ok) throw new Error('No se pudo generar el PDF en el servidor');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;

      const empresaClean = scrapedData.company
        .trim()
        .replace(/\s+/g, '_')
        .replace(/[^a-zA-Z0-9_]/g, '');

      a.download = `CV_Timoteo_Pereyra_${empresaClean}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      setDownloadState('done');
      setTimeout(() => setDownloadState('idle'), 2500);
    } catch (error) {
      console.error(`❌ Error al descargar el PDF: ${error.message}`);
      setDownloadState('error');
      setTimeout(() => setDownloadState('idle'), 2500);
    }
  };

  const dlConfig = {
    idle: {
      label: 'Descargar CV',
      icon: <DownloadIcon />,
      style: {
        background: 'linear-gradient(135deg, #1e1e22 0%, #252529 100%)',
        border: '1px solid rgba(255,255,255,0.1)',
        color: '#a1a1aa',
        cursor: 'pointer',
        boxShadow: 'none',
      }
    },
    loading: {
      label: 'Generando...',
      icon: null,
      style: {
        background: 'linear-gradient(135deg, #1e1e22 0%, #252529 100%)',
        border: '1px solid rgba(78,222,163,0.2)',
        color: '#4edea3',
        cursor: 'wait',
        boxShadow: '0 0 12px rgba(78,222,163,0.08)',
      }
    },
    done: {
      label: 'Descargado',
      icon: <CheckIcon />,
      style: {
        background: 'linear-gradient(135deg, rgba(78,222,163,0.12) 0%, rgba(78,222,163,0.06) 100%)',
        border: '1px solid rgba(78,222,163,0.3)',
        color: '#4edea3',
        cursor: 'default',
        boxShadow: '0 0 16px rgba(78,222,163,0.1)',
      }
    },
    error: {
      label: 'Error — reintentar',
      icon: null,
      style: {
        background: 'linear-gradient(135deg, rgba(239,68,68,0.1) 0%, rgba(239,68,68,0.05) 100%)',
        border: '1px solid rgba(239,68,68,0.25)',
        color: '#f87171',
        cursor: 'pointer',
        boxShadow: 'none',
      }
    }
  };

  const dl = dlConfig[downloadState];

  return (
    <div className="flex flex-col h-screen max-w-[1280px] mx-auto w-full p-4 gap-3"
         style={{ fontFamily: "'Syne', sans-serif" }}>

      {/* TOPBAR */}
      <div className="flex items-center justify-between px-1">
        <div className="flex items-center gap-2.5">
          <div className="w-2 h-2 rounded-full bg-[#4edea3]"
               style={{ boxShadow: '0 0 10px #4edea3' }} />
          <span className="text-[15px] font-semibold tracking-wide text-white">
            Bot<span className="text-[#4edea3]">Jobs</span>
          </span>
        </div>
        <div className="flex items-center gap-1.5 text-[11px] text-zinc-500"
             style={{ fontFamily: "'DM Mono', monospace" }}>
          <div className="w-1.5 h-1.5 rounded-full bg-[#4edea3]" />
          sistema activo
        </div>
      </div>

      {/* MAIN GRID */}
      <div className="grid gap-3 flex-1 min-h-0">

        {/* CHAT PANEL */}
        <div className="flex flex-col bg-[#141416] border border-white/[0.07] rounded-2xl overflow-hidden min-h-0">
          <div className="flex items-center justify-between px-4 py-3 border-b border-white/[0.07]">
            <span className="text-[11px] font-medium tracking-[0.08em] text-zinc-500 uppercase">Chat</span>
            <span className="text-[10px] text-[#4edea3] bg-[#4edea3]/10 border border-[#4edea3]/25 px-2 py-1 rounded-md"
                  style={{ fontFamily: "'DM Mono', monospace" }}>
              {analysisCount} análisis
            </span>
          </div>

          <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-2.5 min-h-0">
            {messages.map((m, i) => (
              <div key={i} className={`max-w-[82%] px-3.5 py-2.5 rounded-xl text-[13px] leading-relaxed
                ${m.role === 'user'
                  ? 'bg-[#4edea3]/10 border border-[#4edea3]/25 text-[#4edea3] self-end rounded-br-sm'
                  : 'bg-[#1a1a1d] border border-white/[0.07] text-zinc-300 self-start rounded-bl-sm'
                }`}
                style={{ fontFamily: m.role === 'user' ? "'DM Mono', monospace" : 'inherit', fontSize: m.role === 'user' ? 12 : 13 }}>
                {m.text}
              </div>
            ))}
            {isLoading && (
              <div className="flex gap-1.5 items-center px-3.5 py-3 bg-[#1a1a1d] border border-white/[0.07] rounded-xl rounded-bl-sm w-fit">
                {[0, 200, 400].map(d => (
                  <div key={d} className="w-1.5 h-1.5 rounded-full bg-zinc-600 animate-pulse"
                       style={{ animationDelay: `${d}ms` }} />
                ))}
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="flex gap-2 p-3 border-t border-white/[0.07]">
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && sendMessage()}
              disabled={isLoading}
              placeholder="https://oferta.com/empleo..."
              className="flex-1 bg-[#1a1a1d] border border-white/[0.07] rounded-xl px-3.5 py-2.5 text-[13px] text-white outline-none focus:border-[#4edea3]/30 transition-colors disabled:opacity-40 placeholder-zinc-600"
              style={{ fontFamily: "'DM Mono', monospace" }}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading}
              className="bg-[#4edea3] text-[#003824] font-semibold text-[12px] px-5 py-2.5 rounded-xl disabled:opacity-40 hover:opacity-85 transition-opacity tracking-wide whitespace-nowrap"
              style={{ cursor: isLoading ? 'wait' : 'pointer' }}>
              {isLoading ? 'Analizando...' : 'Analizar'}
            </button>
          </div>
        </div>

        {/* PREVIEW PANEL */}
        <div className="flex flex-col bg-[#141416] border border-white/[0.07] rounded-2xl overflow-hidden min-h-0">
          <div className="flex items-center justify-between px-4 py-3 border-b border-white/[0.07]">
            <span className="text-[11px] font-medium tracking-[0.08em] text-zinc-500 uppercase">Preview del email</span>
            {hasPreview && (
              <span className="text-[10px] text-[#4edea3] bg-[#4edea3]/10 border border-[#4edea3]/25 px-2 py-1 rounded-md"
                    style={{ fontFamily: "'DM Mono', monospace" }}>
                editable
              </span>
            )}
          </div>

          {!hasPreview ? (
            <div className="flex-1 flex flex-col items-center justify-center gap-2 text-zinc-600 p-6 text-center">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 5L2 7"/>
              </svg>
              <p className="text-[13px] text-zinc-600 mt-1">El mail generado aparece acá</p>
              <p className="text-[11px] text-zinc-700" style={{ fontFamily: "'DM Mono', monospace" }}>
                Ingresá una URL en el chat
              </p>
            </div>
          ) : (
            <>
              <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3.5 min-h-0">
                <CopyInput
                  label="Para"
                  type="email"
                  value={emailPreview.to}
                  onChange={v => setEmailPreview({ ...emailPreview, to: v })}
                />
                <CopyInput
                  label="Asunto"
                  value={emailPreview.asunto}
                  onChange={v => setEmailPreview({ ...emailPreview, asunto: v })}
                />
                <CopyInput
                  label="Mensaje"
                  value={emailPreview.cuerpo}
                  onChange={v => setEmailPreview({ ...emailPreview, cuerpo: v })}
                  multiline
                />
              </div>

              <div className="flex gap-2 p-3 border-t border-white/[0.07]">
                {/* Copy full email */}
                <button
                  onClick={copyEmail}
                  className={`flex-1 font-semibold text-[12px] py-2.5 rounded-xl transition-all tracking-wide flex items-center justify-center gap-2 cursor-pointer
                    ${copied
                      ? 'bg-[#4edea3] text-[#003824]'
                      : 'bg-[#4edea3]/10 border border-[#4edea3]/25 text-[#4edea3] hover:bg-[#4edea3]/20'
                    }`}>
                  {copied ? <CheckIcon /> : <CopyIcon />}
                  {copied ? 'Email copiado' : 'Copiar email completo'}
                </button>

                {/* Download CV */}
                <button
                  onClick={downloadCV}
                  disabled={downloadState === 'loading' || downloadState === 'done'}
                  style={{
                    ...dl.style,
                    transition: 'all 0.25s ease',
                    fontFamily: "'DM Mono', monospace",
                  }}
                  className="flex items-center justify-center gap-2 font-medium text-[12px] px-5 py-2.5 rounded-xl tracking-wide whitespace-nowrap min-w-[148px]">
                  {downloadState === 'loading' ? (
                    <>
                      <div style={{
                        width: 13, height: 13, borderRadius: '50%',
                        border: '2px solid rgba(78,222,163,0.25)',
                        borderTopColor: '#4edea3',
                        animation: 'spin 0.7s linear infinite',
                        flexShrink: 0,
                      }} />
                      Generando...
                    </>
                  ) : (
                    <>
                      {dl.icon}
                      {dl.label}
                    </>
                  )}
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}