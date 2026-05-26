import React, { useState, useEffect } from 'react';
import { supabase } from './lib/supabase';

export default function App() {
  // Estados para la base de datos y UI
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isSheetOpen, setIsSheetOpen] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);

  // Métricas dinámicas
  const [stats, setStats] = useState({ scraped: 0, qualified: 0, recommended: 0 });

  // Función para traer las ofertas desde Supabase ordenadas por Score descendente
  const fetchJobs = async () => {
    try {
      setLoading(true);
      
      const { data, error } = await supabase
        .from('jobs') // Nombre exacto de tu tabla
        .select('*')
        .order('score', { ascending: false });

      console.log("Error de Supabase:", error);
      console.log("Datos que llegaron:", data);

      if (error) throw error;

      if (data) {
        setJobs(data);
        const totalScraped = data.length;
        const totalQualified = data.filter(j => parseInt(j.score || 0, 10) > 0).length;
        const totalRecommended = data.filter(j => j.recommended === true || j.recommended === 'true').length;

        setStats({
          scraped: totalScraped,
          qualified: totalQualified,
          recommended: totalRecommended
        });
      }
    } catch (error) {
      console.error('Error cargando ofertas de Supabase:', error.message);
    } finally {
      setLoading(false);
    }
  };

  // Traer datos al montar la app por primera vez
  useEffect(() => {
    fetchJobs();
  }, []);

  const handleSync = async () => {
    if (isSyncing) return;
    setIsSyncing(true);
    await fetchJobs();
    setIsSyncing(false);
  };

  return (
    <div className="min-h-screen bg-[#0e0e10] text-[#e5e1e4] font-sans antialiased selection:bg-emerald-500/30">
      
      {/* Inyección de fuentes e iconos */}
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"/>
      <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>

      {/* Top App Bar */}
      <header className="fixed top-0 w-full z-50 bg-[#131315]/60 backdrop-blur-xl border-b border-[#3c4a42]/30 flex justify-between items-center px-4 h-16">
        <div className="flex items-center gap-2 cursor-pointer active:scale-95 transition-transform duration-200">
          <span className="material-symbols-outlined text-[#4edea3]">terminal</span>
          <h1 className="font-semibold tracking-tighter text-xl text-[#4edea3]">ELITE CAREER</h1>
        </div>
        <div 
          onClick={handleSync}
          className="flex items-center justify-center p-2 text-[#4edea3] cursor-pointer active:scale-95 transition-transform duration-200"
        >
          <span className={`material-symbols-outlined ${isSyncing ? 'animate-spin' : ''}`}>sync</span>
        </div>
      </header>

      <main className="pt-20 pb-24 px-4 max-w-md mx-auto">
        {/* Dashboard Header Stats Dinámicos */}
        <section className="grid grid-cols-3 gap-3 mb-6">
          <div className="bg-[#18181a]/60 backdrop-blur-md border border-[#3c4a42]/30 p-3 rounded-xl flex flex-col items-center justify-center text-center">
            <span className="text-[#bbcabf] text-xs font-medium">Scraped</span>
            <span className="text-[#4edea3] text-lg font-semibold">{stats.scraped}</span>
          </div>
          <div className="bg-[#18181a]/60 backdrop-blur-md border border-[#3c4a42]/30 p-3 rounded-xl flex flex-col items-center justify-center text-center">
            <span className="text-[#bbcabf] text-xs font-medium">Qualified</span>
            <span className="text-[#4edea3] text-lg font-semibold">{stats.qualified}</span>
          </div>
          <div className="bg-[#18181a]/60 backdrop-blur-md border border-[#3c4a42]/30 p-3 rounded-xl flex flex-col items-center justify-center text-center">
            <span className="text-[#bbcabf] text-xs font-medium">Best Fit</span>
            <span className="text-[#4edea3] text-lg font-semibold">{stats.recommended}</span>
          </div>
        </section>

        {/* Sync Action Button */}
        <button 
          onClick={handleSync}
          disabled={isSyncing}
          className="w-full h-12 bg-[#4edea3] text-[#003824] font-semibold rounded-xl mb-6 flex items-center justify-center gap-2 active:scale-[0.98] transition-all disabled:opacity-80"
        >
          <span className={`material-symbols-outlined ${isSyncing ? 'animate-spin' : ''}`}>refresh</span>
          <span>{isSyncing ? 'Syncing Feed...' : 'Sync Job Feed'}</span>
        </button>

        {/* Feed de ofertas */}
        <div className="flex flex-col gap-3">
          {loading ? (
            <div className="text-center py-12 text-[#bbcabf] text-sm animate-pulse">
              Cargando ofertas reales...
            </div>
          ) : jobs.length === 0 ? (
            <div className="text-center py-12 text-[#bbcabf] text-sm">
              No hay ofertas procesadas en la base de datos.
            </div>
          ) : (
            jobs.map((job, index) => {
              const numericScore = parseInt(job.score || 0, 10);
              const isPositive = numericScore > 0;
              const isNegative = numericScore < 0;

              return (
                <div 
                  key={job.id || index} 
                  className={`bg-[#18181a]/60 backdrop-blur-md p-5 rounded-xl border border-[#3c4a42]/30 transition-all ${
                    isPositive ? 'hover:border-[#4edea3]/50' : isNegative ? 'opacity-60' : ''
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="max-w-[70%]">
                      <h3 className="text-base font-semibold text-[#e5e1e4] truncate">{job.title || "Sin título"}</h3>
                      <p className="text-xs text-[#bbcabf] truncate">{job.company || "Compañía Oculta"}</p>
                    </div>
                    
                    <div className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${
                      isPositive ? 'bg-emerald-500/10 text-[#4edea3] border-emerald-500/20' :
                      isNegative ? 'bg-rose-500/10 text-rose-400 border-rose-500/30' :
                      'bg-[#353437] text-[#bbcabf] border-[#3c4a42]'
                    }`}>
                      {numericScore > 0 ? `+${numericScore}` : numericScore}
                    </div>
                  </div>

                  {/* Keywords Positivas */}
                  {job.matched_positive && job.matched_positive.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mb-2">
                      {job.matched_positive.map((tag, i) => (
                        <span key={i} className="bg-emerald-500/5 text-[#4edea3] text-[10px] px-2 py-0.5 rounded border border-emerald-500/10">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Keywords Negativas */}
                  {job.matched_negative && job.matched_negative.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mb-3">
                      {job.matched_negative.map((tag, i) => (
                        <span key={i} className="bg-rose-500/5 text-rose-400 text-[10px] px-2 py-0.5 rounded border border-rose-500/10">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* AI Summary real */}
                  {job.ai_summary && (
                    <p className="italic text-[#bbcabf]/80 text-xs border-l-2 border-[#4edea3]/30 pl-3 py-1 mb-3">
                      {job.ai_summary}
                    </p>
                  )}

                  {/* Botón enlace real */}
                  <a 
                    href={job.url || "#"} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className={`w-full block text-center font-semibold py-2.5 rounded-lg active:scale-95 transition-all text-sm ${
                      isPositive ? 'bg-[#4edea3] text-[#003824]' : 'bg-[#353437] text-[#e5e1e4]'
                    }`}
                  >
                    Aplicar 🔗
                  </a>
                </div>
              );
            })
          )}
        </div>
      </main>

      {/* Bottom Navigation Bar */}
      <nav className="fixed bottom-0 left-0 right-0 z-50 rounded-t-xl bg-[#201f22]/80 backdrop-blur-xl border-t border-[#3c4a42]/20 shadow-lg flex justify-around items-center px-4 py-3">
        <div className="flex flex-col items-center justify-center text-[#4edea3] bg-[#10b981]/20 rounded-xl px-4 py-1 cursor-pointer">
          <span className="material-symbols-outlined">explore</span>
          <span className="text-[11px] font-semibold">Feed</span>
        </div>
        <div className="flex flex-col items-center justify-center text-[#bbcabf] cursor-pointer">
          <span className="material-symbols-outlined">analytics</span>
          <span className="text-[11px] font-semibold">Metrics</span>
        </div>
        <div 
          onClick={() => setIsSheetOpen(true)}
          className="flex flex-col items-center justify-center text-[#bbcabf] cursor-pointer"
        >
          <span className="material-symbols-outlined">tune</span>
          <span className="text-[11px] font-semibold">Filters</span>
        </div>
      </nav>

      {/* Drawer inferior para los Filtros */}
      {isSheetOpen && (
        <div 
          onClick={() => setIsSheetOpen(false)}
          className="fixed inset-0 bg-black/60 z-[60]"
        />
      )}

      <div className={`fixed bottom-0 left-0 right-0 z-[70] bg-[#18181a] border-t border-[#3c4a42]/40 rounded-t-3xl px-4 pt-3 pb-12 transition-transform duration-300 transform max-w-md mx-auto ${
        isSheetOpen ? 'translate-y-0' : 'translate-y-full'
      }`}>
        <div className="w-12 h-1.5 bg-[#3c4a42]/50 rounded-full mx-auto mb-6"></div>
        <h2 className="text-xl font-semibold text-[#e5e1e4] mb-6">Keywords &amp; Filters</h2>
        
        <div className="mb-8">
          <h3 className="text-base font-semibold text-[#4edea3] mb-4">Active Skills</h3>
          <div className="flex flex-wrap gap-2">
            {["React", "Tailwind CSS", "Python"].map((skill, index) => (
              <div key={index} className="flex items-center gap-1 bg-[#2a2a2c] border border-[#3c4a42] text-[#e5e1e4] px-4 py-2 rounded-full text-xs font-medium">
                {skill}
                <span className="material-symbols-outlined text-[16px] text-[#bbcabf] cursor-pointer hover:text-rose-400">close</span>
              </div>
            ))}
          </div>
        </div>

        <button 
          onClick={() => setIsSheetOpen(false)}
          className="w-full bg-[#4edea3] text-[#003824] font-semibold py-4 rounded-xl shadow-lg active:scale-[0.98] transition-transform"
        >
          Apply Selection
        </button>
      </div>

    </div>
  );
}