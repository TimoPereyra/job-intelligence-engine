import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';

export default function FeedJobs() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);

  const fetchJobs = async () => {
    try {
      const { data, error } = await supabase
        .from('jobs')
        .select('*')
        .order('score', { ascending: false });
      
      if (error) throw error;
      setJobs(data || []);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  // Función para inicializar carga y sincronización
  const handleSync = async () => {
    setIsSyncing(true);
    await fetchJobs();
    setIsSyncing(false);
    setLoading(false); // Aseguramos que el estado de carga inicial termine
  };

  useEffect(() => {
    handleSync();
  }, []);

  return (
    <div className="flex flex-col gap-3">
      {/* Botón de Sincronización */}
      <button 
        onClick={handleSync}
        disabled={isSyncing}
        className="w-full h-12 bg-[#4edea3] text-[#003824] font-semibold rounded-xl flex items-center justify-center gap-2 active:scale-[0.98] transition-all disabled:opacity-80"
      >
        <span className={`material-symbols-outlined ${isSyncing ? 'animate-spin' : ''}`}>Load</span>
        <span>{isSyncing ? 'Syncing Feed...' : 'Sync Job Feed'}</span>
      </button>

      {/* Listado de trabajos */}
      {loading ? (
        <div className="text-center py-12 text-[#bbcabf] animate-pulse">Cargando ofertas...</div>
      ) : jobs.length > 0 ? (
        jobs.map((job) => (
          <div key={job.id} className="bg-[#18181a]/60 p-5 rounded-xl border border-[#3c4a42]/30">
            <h3 className="text-base font-semibold text-[#e5e1e4]">{job.title}</h3>
            <p className="text-xs text-[#bbcabf] mb-3">{job.company}</p>
            <a href={job.url} target="_blank" rel="noopener noreferrer" className="block text-center bg-[#4edea3] text-[#003824] py-2 rounded-lg font-semibold text-sm">
              Aplicar 🔗
            </a>
          </div>
        ))
      ) : (
        <div className="text-center py-20 px-4">
          <h3 className="text-[#e5e1e4] font-semibold mb-2">No hay empleos</h3>
          <p className="text-[#bbcabf] text-sm">Sincroniza para traer nuevas ofertas.</p>
        </div>
      )}
    </div>
  );
}