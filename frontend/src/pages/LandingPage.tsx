import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Image, Video, Sparkles, ArrowRight } from 'lucide-react';

export function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      <header className="container mx-auto px-4 py-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-blue-600 flex items-center justify-center text-white font-bold text-2xl">
            U
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">AI Content Generator</h1>
            <p className="text-xs text-slate-600">by Unilever</p>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 pt-20 pb-16">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <div className="inline-flex items-center gap-2 px-5 py-2 rounded-full bg-white border border-blue-200 shadow-sm">
            <Sparkles className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-medium text-slate-700">AI-Powered Creative Studio</span>
          </div>

          <h1 className="text-6xl md:text-7xl font-bold tracking-tight leading-tight text-slate-900">
            Create with
            <br />
            <span className="bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
              AI Confidence
            </span>
          </h1>

          <p className="text-xl md:text-2xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
            Generate brand-compliant images and videos using AI with RAG-enhanced prompts.
          </p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-12">
        <div className="max-w-5xl mx-auto">
          <div className="text-center space-y-4 mb-12">
            <h2 className="text-3xl font-bold text-slate-900">Choose Your Creation Type</h2>
            <p className="text-lg text-slate-600">Select image or video generation to get started</p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <Link to="/chat">
              <Card className="group hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 cursor-pointer border-2 border-transparent hover:border-blue-500 bg-white">
                <CardContent className="pt-12 pb-12 text-center space-y-6">
                  <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 mx-auto flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Image className="w-10 h-10 text-white" />
                  </div>
                  <div>
                    <h3 className="font-bold text-2xl mb-2 text-slate-900">Image Generation</h3>
                    <p className="text-slate-600 leading-relaxed">
                      Create stunning brand-compliant images using Stable Diffusion XL with RAG-enhanced prompts
                    </p>
                  </div>
                  <div className="flex items-center justify-center gap-2 text-blue-600 font-semibold group-hover:gap-4 transition-all">
                    <span>Start Creating</span>
                    <ArrowRight className="w-5 h-5" />
                  </div>
                </CardContent>
              </Card>
            </Link>

            <Link to="/chat">
              <Card className="group hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 cursor-pointer border-2 border-transparent hover:border-cyan-500 bg-white">
                <CardContent className="pt-12 pb-12 text-center space-y-6">
                  <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-cyan-500 to-cyan-600 mx-auto flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Video className="w-10 h-10 text-white" />
                  </div>
                  <div>
                    <h3 className="font-bold text-2xl mb-2 text-slate-900">Video Generation</h3>
                    <p className="text-slate-600 leading-relaxed">
                      Generate engaging brand videos using ModelScope text-to-video with brand metadata integration
                    </p>
                  </div>
                  <div className="flex items-center justify-center gap-2 text-cyan-600 font-semibold group-hover:gap-4 transition-all">
                    <span>Start Creating</span>
                    <ArrowRight className="w-5 h-5" />
                  </div>
                </CardContent>
              </Card>
            </Link>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-20">
        <div className="max-w-6xl mx-auto">
          <div className="text-center space-y-4 mb-12">
            <h2 className="text-3xl font-bold text-slate-900">Powered by RAG Pipeline</h2>
            <p className="text-slate-600">Brand metadata retrieval for enhanced AI generation</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Card className="bg-white border-slate-200">
              <CardContent className="pt-8 pb-8 space-y-4">
                <div className="w-14 h-14 rounded-2xl bg-blue-100 flex items-center justify-center">
                  <Sparkles className="w-7 h-7 text-blue-600" />
                </div>
                <h3 className="font-bold text-xl text-slate-900">Vector Database</h3>
                <p className="text-slate-600 leading-relaxed">
                  ChromaDB stores brand metadata including tone of voice, visual style, and brand communications
                </p>
              </CardContent>
            </Card>

            <Card className="bg-white border-slate-200">
              <CardContent className="pt-8 pb-8 space-y-4">
                <div className="w-14 h-14 rounded-2xl bg-cyan-100 flex items-center justify-center">
                  <Sparkles className="w-7 h-7 text-cyan-600" />
                </div>
                <h3 className="font-bold text-xl text-slate-900">Smart Retrieval</h3>
                <p className="text-slate-600 leading-relaxed">
                  Automatically retrieves relevant brand information based on your selected brand
                </p>
              </CardContent>
            </Card>

            <Card className="bg-white border-slate-200">
              <CardContent className="pt-8 pb-8 space-y-4">
                <div className="w-14 h-14 rounded-2xl bg-purple-100 flex items-center justify-center">
                  <Sparkles className="w-7 h-7 text-purple-600" />
                </div>
                <h3 className="font-bold text-xl text-slate-900">Enhanced Prompts</h3>
                <p className="text-slate-600 leading-relaxed">
                  Your prompts are enriched with brand metadata for consistent, on-brand content
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      <footer className="container mx-auto px-4 py-12 text-center text-sm text-slate-600 border-t border-slate-200">
        <div className="flex items-center justify-center gap-2 mb-2">
          <div className="w-6 h-6 rounded bg-blue-600 flex items-center justify-center text-white text-xs font-bold">
            U
          </div>
          <span className="font-semibold text-slate-900">AI Content Generator POC</span>
        </div>
        <p>Powered by Unilever - RAG Pipeline with Stable Diffusion XL & ModelScope</p>
      </footer>
    </div>
  );
}
