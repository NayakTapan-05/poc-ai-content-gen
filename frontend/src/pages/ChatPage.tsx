import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ArrowLeft, Send, Download, Loader2, Sparkles, Plus } from 'lucide-react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Message {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
  media_url?: string;
  media_type?: 'image' | 'video';
  timestamp: string;
}

export function ChatPage() {
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [brands, setBrands] = useState<string[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<string>('none');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchBrands();
    fetchSessions();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchBrands = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/rag/brands`);
      setBrands(response.data.brands || []);
    } catch (error) {
      console.error('Error fetching brands:', error);
    }
  };

  const fetchSessions = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/sessions`);
      
      if (response.data.length === 0) {
        await createNewSession();
      } else {
        const mostRecent = response.data[0];
        setCurrentSessionId(mostRecent.id);
        await loadSessionHistory(mostRecent.id);
      }
    } catch (error) {
      console.error('Error fetching sessions:', error);
    }
  };

  const createNewSession = async () => {
    try {
      const response = await axios.post(`${API_URL}/api/sessions`, {
        name: `Chat ${new Date().toLocaleString()}`
      });
      const newSession = response.data;
      setCurrentSessionId(newSession.id);
      setMessages([]);
    } catch (error) {
      console.error('Error creating session:', error);
    }
  };

  const loadSessionHistory = async (sessionId: string) => {
    try {
      const response = await axios.get(`${API_URL}/api/history/${sessionId}`);
      setMessages(response.data || []);
    } catch (error) {
      console.error('Error loading session history:', error);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || !currentSessionId) return;

    const userPrompt = input;
    setInput('');
    setIsGenerating(true);

    try {
      await axios.post(`${API_URL}/api/agent/chat`, {
        message: userPrompt,
        session_id: currentSessionId,
        brand_id: selectedBrand === 'none' ? null : selectedBrand
      });

      await loadSessionHistory(currentSessionId);
    } catch (error: any) {
      console.error('Error sending message:', error);
      const errorMsg: Message = {
        role: 'assistant',
        content: `Error: ${error.response?.data?.detail || error.message}`,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = async (mediaUrl: string, mediaType: 'image' | 'video') => {
    try {
      const response = await fetch(mediaUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `generated_${mediaType}_${Date.now()}.${mediaType === 'image' ? 'png' : 'mp4'}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading file:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link to="/">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back
                </Button>
              </Link>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white font-bold">
                  AI
                </div>
                <div>
                  <h1 className="text-lg font-bold text-slate-900">
                    AI Content Generator
                  </h1>
                  <p className="text-xs text-slate-600">Multi-Session Chat</p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              {brands.length > 0 && (
                <div className="flex items-center gap-2">
                  <span className="text-sm text-slate-600">Brand:</span>
                  <Select value={selectedBrand} onValueChange={setSelectedBrand}>
                    <SelectTrigger className="w-40">
                      <SelectValue placeholder="None" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">No brand</SelectItem>
                      {brands.map(brand => (
                        <SelectItem key={brand} value={brand}>
                          {brand}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
              <Button onClick={createNewSession} size="sm">
                <Plus className="w-4 h-4 mr-2" />
                New Chat
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6 max-w-7xl flex gap-4">
        <div className="bg-white rounded-2xl shadow-lg border border-slate-200 flex flex-col" style={{ height: 'calc(100vh - 200px)' }}>
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-2xl ${message.role === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-900'} rounded-2xl px-6 py-4`}>
                  <p className="text-sm mb-2">{message.content}</p>
                  
                  {message.media_url && message.media_type === 'image' && (
                    <div className="mt-4 space-y-2">
                      <img
                        src={message.media_url}
                        alt="Generated content"
                        className="rounded-lg max-w-full h-auto"
                      />
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => handleDownload(message.media_url!, 'image')}
                        className="w-full"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Download Image
                      </Button>
                    </div>
                  )}

                  {message.media_url && message.media_type === 'video' && (
                    <div className="mt-4 space-y-2">
                      <video
                        src={message.media_url}
                        controls
                        className="rounded-lg max-w-full h-auto"
                      />
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => handleDownload(message.media_url!, 'video')}
                        className="w-full"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Download Video
                      </Button>
                    </div>
                  )}

                  <p className="text-xs opacity-70 mt-2">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}

            {isGenerating && (
              <div className="flex justify-start">
                <div className="bg-slate-100 text-slate-900 rounded-2xl px-6 py-4 flex items-center gap-3">
                  <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                  <span>Generating content...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div className="border-t border-slate-200 p-4">
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !isGenerating && handleSend()}
                placeholder="Describe what you want to create (image or video)..."
                disabled={isGenerating}
                className="flex-1"
              />
              <Button
                onClick={handleSend}
                disabled={isGenerating || !input.trim()}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {isGenerating ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </Button>
            </div>
            <p className="text-xs text-slate-500 mt-2">
              <Sparkles className="w-3 h-3 inline mr-1" />
              Powered by Stable Diffusion & Stable Video Diffusion
              {selectedBrand !== 'none' && ` • Using ${selectedBrand} brand metadata`}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
