import React, { useState, useRef, useEffect } from 'react';

const API_KEY = import.meta.env.VITE_INTERNAL_API_KEY || "";
const API_URL = import.meta.env.VITE_API_URL || "https://job-intelligence-engine-nu.vercel.app/";

export default function ChatBot() {
  const [messages, setMessages] = useState([
    { role: 'bot', text: '¡Hola! Pegá la URL de una oferta de empleo y genero el mail y el CV personalizado.' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [analysisCount, setAnalysisCount] = useState(0);
  const [emailPreview, setEmailPreview] = useState({ to: '', asunto: '', cuerpo: '' });
  const [scrapedData, setScrapedData] = useState(null); // <- Nuevo estado para guardar la data de la vacante
  const [hasPreview, setHasPreview] = useState(false);
  const [copied, setCopied] = useState(false);
  const [pdfBase64, setPdfBase64] = useState(null);
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
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${API_KEY}` },
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

        // Guardamos los datos estructurados para tenerlos listos para la descarga del PDF
        setScrapedData({
          title: data.job_title || 'Vacante',
          company: data.company || 'No especificada',
          description: data.description || 'No especificada',
          email: data.contact_email || ''
        });

        setPdfBase64(data.cv_pdf_base64 || null);
        setHasPreview(true);
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
    // Validamos usando el estado local que acabamos de persistir
    if (!scrapedData || !scrapedData.title || isLoading) {
      alert("Primero debés procesar una oferta válida para poder adaptar tu CV.");
      return;
    }

    try {
      setIsLoading(true);

      const response = await fetch(`${API_URL}/api/generate-pdf`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${API_KEY}`
        },
        body: JSON.stringify({
          scraped_data: {
            title: scrapedData.title,
            company: scrapedData.company,
            description: scrapedData.description,
            email: scrapedData.email
          }
        })
      });

      if (!response.ok) {
        throw new Error('No se pudo generar el PDF en el servidor');
      }

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

    } catch (error) {
      console.error(`❌ Error al descargar el PDF: ${error.message}`);
      alert(`No se pudo descargar el PDF: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

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
              className="bg-[#4edea3] text-[#003824] font-semibold text-[12px] px-5 py-2.5 rounded-xl disabled:opacity-40 hover:opacity-85 transition-opacity tracking-wide whitespace-nowrap">
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
                {/* Para */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-medium tracking-[0.1em] text-zinc-500 uppercase"
                         style={{ fontFamily: "'DM Mono', monospace" }}>Para</label>
                  <input
                    type="email"
                    value={emailPreview.to}
                    onChange={e => setEmailPreview({ ...emailPreview, to: e.target.value })}
                    className="bg-[#1a1a1d] border border-white/[0.07] rounded-xl px-3.5 py-2.5 text-[13px] text-white outline-none focus:border-[#4edea3]/30 transition-colors w-full"
                    style={{ fontFamily: "'DM Mono', monospace" }}
                  />
                </div>
                {/* Asunto */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-medium tracking-[0.1em] text-zinc-500 uppercase"
                         style={{ fontFamily: "'DM Mono', monospace" }}>Asunto</label>
                  <input
                    value={emailPreview.asunto}
                    onChange={e => setEmailPreview({ ...emailPreview, asunto: e.target.value })}
                    className="bg-[#1a1a1d] border border-white/[0.07] rounded-xl px-3.5 py-2.5 text-[13px] text-white outline-none focus:border-[#4edea3]/30 transition-colors w-full"
                  />
                </div>
                {/* Mensaje */}
                <div className="flex flex-col gap-1.5 flex-1 min-h-0">
                  <label className="text-[10px] font-medium tracking-[0.1em] text-zinc-500 uppercase"
                         style={{ fontFamily: "'DM Mono', monospace" }}>Mensaje</label>
                  <textarea
                    value={emailPreview.cuerpo}
                    onChange={e => setEmailPreview({ ...emailPreview, cuerpo: e.target.value })}
                    className="flex-1 bg-[#1a1a1d] border border-white/[0.07] rounded-xl p-3.5 text-[13px] text-zinc-300 outline-none focus:border-[#4edea3]/30 transition-colors resize-none w-full leading-relaxed"
                    style={{ minHeight: 160 }}
                  />
                </div>
              </div>

              <div className="flex gap-2 p-3 border-t border-white/[0.07]">
                <button
                  onClick={copyEmail}
                  className={`flex-1 font-semibold text-[12px] py-2.5 rounded-xl transition-all tracking-wide
                    ${copied
                      ? 'bg-[#4edea3] text-[#003824]'
                      : 'bg-[#4edea3]/10 border border-[#4edea3]/25 text-[#4edea3] hover:bg-[#4edea3]/20'
                    }`}>
                  {copied ? '✓ Copiado' : '⎘ Copiar email'}
                </button>
                <button
                  onClick={downloadCV}
                  disabled={isLoading}
                  className="bg-[#1a1a1d] border border-white/[0.07] text-zinc-500 hover:text-zinc-300 font-medium text-[12px] px-4 py-2.5 rounded-xl transition-all disabled:opacity-30 disabled:cursor-not-allowed whitespace-nowrap tracking-wide">
                  ↓ Descargar CV
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}