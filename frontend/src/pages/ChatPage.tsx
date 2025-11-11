import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ArrowLeft, Send, Download, Loader2, Image as ImageIcon, Video as VideoIcon } from 'lucide-react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  mediaUrl?: string;
  mediaType?: 'image' | 'video';
  timestamp: Date;
}

interface Brand {
  name: string;
}

export function ChatPage() {
  const { type } = useParams<{ type: 'image' | 'video' }>();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [brands, setBrands] = useState<string[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchBrands();
    setMessages([
      {
        role: 'assistant',
        content: `Welcome to ${type === 'image' ? 'Image' : 'Video'} Generation! I can help you create brand-compliant ${type}s using AI. ${brands.length > 0 ? 'Select a brand and describe what you want to create.' : 'Upload brand metadata first or describe what you want to create without brand context.'}`,
        timestamp: new Date()
      }
    ]);
  }, [type]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchBrands = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/brands`);
      setBrands(response.data.brands || []);
    } catch (error) {
      console.error('Error fetching brands:', error);
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsGenerating(true);

    try {
      const endpoint = type === 'image' ? '/api/generate/image' : '/api/generate/video';
      
      const response = await axios.post(`${API_URL}${endpoint}`, {
        prompt: input,
        brand_name: selectedBrand || null
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: `Generated ${type} successfully! ${selectedBrand ? `Using brand: ${selectedBrand}` : ''}`,
        mediaUrl: `${API_URL}${response.data.media_url}`,
        mediaType: type,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        role: 'assistant',
        content: `Error generating ${type}: ${error.response?.data?.detail || error.message}. ${error.response?.status === 404 ? 'Please upload brand metadata first.' : ''}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
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
                  U
                </div>
                <div>
                  <h1 className="text-lg font-bold text-slate-900">
                    {type === 'image' ? 'Image' : 'Video'} Generation
                  </h1>
                  <p className="text-xs text-slate-600">AI-Powered Creative Studio</p>
                </div>
              </div>
            </div>

            {brands.length > 0 && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-slate-600">Brand:</span>
                <Select value={selectedBrand} onValueChange={setSelectedBrand}>
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Select brand (optional)" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">No brand</SelectItem>
                    {brands.map(brand => (
                      <SelectItem key={brand} value={brand}>
                        {brand}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6 max-w-5xl">
        <div className="bg-white rounded-2xl shadow-lg border border-slate-200 flex flex-col" style={{ height: 'calc(100vh - 200px)' }}>
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-2xl ${message.role === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-900'} rounded-2xl px-6 py-4`}>
                  <p className="text-sm mb-2">{message.content}</p>
                  
                  {message.mediaUrl && message.mediaType === 'image' && (
                    <div className="mt-4 space-y-2">
                      <img
                        src={message.mediaUrl}
                        alt="Generated content"
                        className="rounded-lg max-w-full h-auto"
                      />
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => handleDownload(message.mediaUrl!, 'image')}
                        className="w-full"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Download Image
                      </Button>
                    </div>
                  )}

                  {message.mediaUrl && message.mediaType === 'video' && (
                    <div className="mt-4 space-y-2">
                      <video
                        src={message.mediaUrl}
                        controls
                        className="rounded-lg max-w-full h-auto"
                      />
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => handleDownload(message.mediaUrl!, 'video')}
                        className="w-full"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Download Video
                      </Button>
                    </div>
                  )}

                  <p className="text-xs opacity-70 mt-2">
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}

            {isGenerating && (
              <div className="flex justify-start">
                <div className="bg-slate-100 text-slate-900 rounded-2xl px-6 py-4 flex items-center gap-3">
                  <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                  <span>Generating {type}...</span>
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
                placeholder={`Describe the ${type} you want to create...`}
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
              {type === 'image' ? (
                <>
                  <ImageIcon className="w-3 h-3 inline mr-1" />
                  Powered by Stable Diffusion XL
                </>
              ) : (
                <>
                  <VideoIcon className="w-3 h-3 inline mr-1" />
                  Powered by ModelScope Text-to-Video
                </>
              )}
              {selectedBrand && ` • Using ${selectedBrand} brand metadata`}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
