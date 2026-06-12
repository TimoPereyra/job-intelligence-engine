import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';

// ── helpers ──────────────────────────────────────────────────────────────────

function detectMarket(source = '', location = '') {
  const s = (source + ' ' + location).toLowerCase();

  // Brasil
  if (/brazil|brasil|são paulo|rio de janeiro|belo horizonte/.test(s))
    return { label: '🇧🇷 Brasil', cls: 'badge-br' };

  // Global en inglés
  if (/united states|europe|european|global-en|uk|united kingdom|canada|australia/.test(s))
    return { label: '🌎 Remote', cls: 'badge-en' };

  // LATAM hispanohablante — solo si matchea explícitamente
  if (/argentina|buenos aires|uruguay|chile|colombia|mexico|méxico|perú|peru|latam|latinoamerica/.test(s))
    return { label: '🇦🇷 LATAM', cls: 'badge-ar' };

  // No matchea nada conocido → badge neutro, no asumas región
  return { label: '🌐 Otro', cls: 'badge-other' };
}
function detectTags(title = '', description = '') {
  const text = `${title} ${description}`.toLowerCase();
  const TECH = [
    'python','django','fastapi','flask',
    'react','next.js','nextjs','vue','angular',
    'typescript','javascript','node','node.js',
    'postgresql','sql','mongodb','redis',
    'docker','aws','gcp','azure',
    'graphql','rest','api',
  ];
  return TECH.filter(t => text.includes(t)).slice(0, 5);
}

function isRemote(location = '', description = '') {
  const text = `${location} ${description}`.toLowerCase();
  return text.includes('remote') || text.includes('remoto') || text.includes('home office');
}

function timeAgo(dateStr) {
  if (!dateStr) return '';
  const diff = (Date.now() - new Date(dateStr)) / 1000;
  if (diff < 3600)  return `hace ${Math.floor(diff / 60)}m`;
  if (diff < 86400) return `hace ${Math.floor(diff / 3600)}h`;
  return `hace ${Math.floor(diff / 86400)}d`;
}

// score 0-100 → color + dashoffset del arco SVG (circunferencia = 125.6)
function scoreStyle(score) {
  const s = Math.max(0, Math.min(100, score ?? 0));
  const offset = 125.6 - (125.6 * s) / 100;
  const color  = s >= 70 ? '#4edea3' : s >= 40 ? '#f0c060' : '#e06060';
  const track  = s >= 70 ? '#1a3326' : s >= 40 ? '#2a2a1a' : '#2a1a1a';
  return { offset, color, track };
}

// ── componente ───────────────────────────────────────────────────────────────

export default function FeedJobs() {
  const [jobs, setJobs]         = useState([]);
  const [loading, setLoading]   = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);

  const fetchJobs = async () => {
    const { data, error } = await supabase
      .from('jobs')
      .select('*')
      .order('score', { ascending: false });
    if (!error) setJobs(data ?? []);
  };

  const handleSync = async () => {
    setIsSyncing(true);
    await fetchJobs();
    setIsSyncing(false);
    setLoading(false);
  };

  useEffect(() => { handleSync(); }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10, padding: 16 }}>

      {/* ── Sync button ── */}
      <button onClick={handleSync} disabled={isSyncing} style={{
        width: '100%', height: 48,
        background: '#4edea3', color: '#003824',
        border: 'none', borderRadius: 14,
        fontWeight: 700, fontSize: 14,
        display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
        cursor: 'pointer', opacity: isSyncing ? 0.8 : 1,
        transition: 'opacity .15s',
      }}>
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"
          style={{ animation: isSyncing ? 'spin 1s linear infinite' : 'none' }}>
          <path d="M3 12a9 9 0 0 1 15-6.7L21 8M21 3v5h-5M21 12a9 9 0 0 1-15 6.7L3 16M3 21v-5h5"/>
        </svg>
        {isSyncing ? 'Sincronizando...' : 'Sync Job Feed'}
      </button>

      {/* ── Estado de carga ── */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '48px 0', color: '#4a6654', fontSize: 13 }}>
          Cargando ofertas...
        </div>

      ) : jobs.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '64px 16px' }}>
          <div style={{ fontSize: 32, marginBottom: 12, opacity: .3 }}>📭</div>
          <p style={{ color: '#e5e1e4', fontWeight: 600, marginBottom: 4 }}>Sin ofertas por ahora</p>
          <p style={{ color: '#4a6654', fontSize: 12 }}>Sincronizá para traer nuevas oportunidades.</p>
        </div>

      ) : (
        /* ── Job cards ── */
        jobs.map((job) => {
          const market  = detectMarket(job.source, job.location);
          const tags    = detectTags(job.title, job.description);
          const remote  = isRemote(job.location, job.description);
          const ago     = timeAgo(job.posted_at);
          const { offset, color, track } = scoreStyle(job.score);

          return (
            <div key={job.id} style={{
              background: '#18211c',
              border: '1px solid #2a3d32',
              borderRadius: 16,
              padding: 16,
              display: 'flex',
              gap: 14,
              alignItems: 'flex-start',
            }}>

              {/* ── Info ── */}
              <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: 7 }}>

                {/* Badges */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
                  <MarketBadge label={market.label} cls={market.cls} />
                  {remote && <MarketBadge label="remoto" cls="badge-remote" />}
                </div>

                {/* Título */}
                <div style={{ fontSize: 15, fontWeight: 600, color: '#e5e1e4', lineHeight: 1.3 }}>
                  {job.title}
                </div>

                {/* Empresa + ubicación */}
                <div style={{ fontSize: 12, color: '#6a8a72' }}>
                  {job.company}
                  {job.location ? <span style={{ color: '#3d5a47' }}> · {job.location}</span> : null}
                </div>

                {/* Descripción (primeras 120 chars) */}
                {job.description && (
                  <div style={{ fontSize: 11, color: '#4a6654', lineHeight: 1.5,
                    overflow: 'hidden', display: '-webkit-box',
                    WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                    {job.description}
                  </div>
                )}

                {/* Tech tags */}
                {tags.length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                    {tags.map(t => (
                      <span key={t} style={{
                        fontSize: 10, fontWeight: 500,
                        background: '#0d1c14', color: '#4edea3',
                        border: '1px solid #1e3828',
                        borderRadius: 5, padding: '2px 6px',
                      }}>{t}</span>
                    ))}
                  </div>
                )}

                {/* Footer: tiempo + botón */}
                <div style={{ display: 'flex', alignItems: 'center', marginTop: 2 }}>
                  {ago && <span style={{ fontSize: 10, color: '#3d5a47' }}>{ago}</span>}
                  <a href={job.url} target="_blank" rel="noopener noreferrer"
                    style={{
                      marginLeft: 'auto',
                      background: 'transparent', color: '#4edea3',
                      border: '1px solid #2a4a38', borderRadius: 8,
                      fontSize: 11, fontWeight: 600,
                      padding: '4px 10px', textDecoration: 'none',
                    }}>
                    Ver oferta ↗
                  </a>
                </div>
              </div>

              {/* ── Score ring ── */}
              <div style={{ flexShrink: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
                <svg width="52" height="52" viewBox="0 0 52 52" style={{ overflow: 'visible' }}>
                  <circle cx="26" cy="26" r="20" fill="none" stroke={track} strokeWidth="4"/>
                  <circle cx="26" cy="26" r="20" fill="none" stroke={color} strokeWidth="4"
                    strokeDasharray="125.6" strokeDashoffset={offset}
                    strokeLinecap="round" transform="rotate(-90 26 26)"
                    style={{ transition: 'stroke-dashoffset .6s ease' }}
                  />
                  <text x="26" y="31" textAnchor="middle"
                    fontSize="13" fontWeight="700" fill={color}
                    fontFamily="system-ui, sans-serif">
                    {job.score ?? '—'}
                  </text>
                </svg>
                <span style={{ fontSize: 9, fontWeight: 600, color: '#4a6654',
                  textTransform: 'uppercase', letterSpacing: '.06em' }}>
                  score
                </span>
              </div>

            </div>
          );
        })
      )}

      {/* ── keyframes para el spinner ── */}
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

const BADGE_STYLES = {
  'badge-ar':     { background: '#1a3326', color: '#4edea3' },
  'badge-br':     { background: '#1e2a1a', color: '#7dd87a' },
  'badge-en':     { background: '#1a2236', color: '#6db8f5' },
  'badge-remote': { background: '#221a36', color: '#b49bf5' },
  'badge-other':  { background: '#1e1e1e', color: '#888880' }, // gris neutro
};
function MarketBadge({ label, cls }) {
  return (
    <span style={{
      fontSize: 11, fontWeight: 600, padding: '2px 7px',
      borderRadius: 6, whiteSpace: 'nowrap',
      ...BADGE_STYLES[cls],
    }}>
      {label}
    </span>
  );
}