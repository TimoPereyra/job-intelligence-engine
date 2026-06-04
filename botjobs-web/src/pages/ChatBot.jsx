import React, { useState } from 'react';

export default function ChatBot() {
  const [messages, setMessages] = useState([{ role: 'bot', text: '¡Hola! ¿En qué puedo ayudarte con tu búsqueda laboral?' }]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Lógica para el TOKEN:
    // 1. Intenta tomarlo de Vercel (import.meta.env.VITE_INTERNAL_API_KEY)
    // 2. Si no existe, usa tu string hardcodeado como respaldo
    const API_KEY = import.meta.env.VITE_INTERNAL_API_KEY || "";
    
    // Lo mismo para la URL de la API:
    // En Vercel usarás la URL de tu API desplegada, en local usas localhost
    const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

    const userMessage = { role: 'user', text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${API_KEY}` 
        },
        body: JSON.stringify({ url: input }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Error al conectar');
      }

      setMessages((prev) => [...prev, { role: 'bot', text: data.message || "Análisis recibido correctamente." }]);
      
    } catch (error) {
      setMessages((prev) => [...prev, { role: 'bot', text: `Error: ${error.message}` }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-[70vh] flex flex-col justify-between">
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.map((m, i) => (
          <div key={i} className={`p-3 rounded-lg ${m.role === 'user' ? 'bg-[#4edea3]/20 ml-auto w-fit' : 'bg-[#18181a] w-fit'}`}>
            {m.text}
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <input 
          value={input} 
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 bg-[#18181a] border border-[#3c4a42] rounded-lg p-2 text-white"
          placeholder="Escribe algo..."
        />
        <button onClick={sendMessage} className="bg-[#4edea3] text-[#003824] px-4 py-2 rounded-lg">Enviar</button>
      </div>
    </div>
  );
}