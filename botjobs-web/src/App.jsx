import { Routes, Route, Link } from 'react-router-dom';
import FeedJobs from './pages/FeedJobs';
import ChatBot from './pages/ChatBot';

export default function App() {
  return (
    <div className="min-h-screen bg-[#0e0e10] text-[#e5e1e4] font-sans">
      <header className="fixed top-0 w-full z-50 bg-[#131315]/60 backdrop-blur-xl border-b border-[#3c4a42]/30 h-16 flex items-center px-4">
        <h1 className="text-[#4edea3] font-bold">ELITE CAREER</h1>
      </header>

      <main className="pt-20 pb-24 px-4 max-w-md mx-auto">
        <Routes>
          <Route path="/" element={<FeedJobs />} />
          <Route path="/chat" element={<ChatBot />} />
        </Routes>
      </main>

      <nav className="fixed bottom-0 left-0 right-0 bg-[#201f22]/80 backdrop-blur-xl p-4 flex justify-around">
        <Link to="/" className="text-[#4edea3]">Feed</Link>
        <Link to="/chat" className="text-[#bbcabf]">Chat</Link>
      </nav>
    </div>
  );
}