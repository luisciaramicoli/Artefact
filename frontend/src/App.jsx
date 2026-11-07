import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Send,
  PlusCircle,
  MessageSquare,
  Trash2,
  Menu,
  X,
  Music,
  Wrench,
  ChevronDown,
  ChevronUp,
  Sparkles,
  MapPin,
  Clock,
  ShieldCheck,
  Package,
  RotateCcw,
  Guitar
} from 'lucide-react';

const SUGGESTIONS = [
  {
    icon: Guitar,
    title: "Violões até R$ 1.000",
    prompt: "Quais opções de violões disponíveis custando até R$1000?"
  },
  {
    icon: MapPin,
    title: "Endereço e Horários",
    prompt: "Qual o endereço e o horário de funcionamento da loja?"
  },
  {
    icon: Sparkles,
    title: "Preço Takamine GD20",
    prompt: "Quanto custa o Takamine GD20?"
  },
  {
    icon: RotateCcw,
    title: "Política de Devolução",
    prompt: "Me arrependi da minha compra online, posso devolver meu pedido?"
  },
  {
    icon: Package,
    title: "Status do Pedido #1",
    prompt: "Gostaria de saber o status e rastreamento do meu pedido número 1."
  },
  {
    icon: Music,
    title: "Acessórios (Escopo)",
    prompt: "Vocês vendem encordoamento de aço e palhetas avulsas?"
  }
];

export default function App() {
  const [conversations, setConversations] = useState([]);
  const [currentConvId, setCurrentConvId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [health, setHealth] = useState(null);
  const [expandedTools, setExpandedTools] = useState({});

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Load initial health & conversations
  useEffect(() => {
    fetchHealth();
    loadConversations();
  }, []);

  const fetchHealth = async () => {
    try {
      const res = await fetch('/api/health');
      if (res.ok) {
        const data = await res.json();
        setHealth(data);
      }
    } catch (e) {
      console.warn("Backend not yet connected:", e);
    }
  };

  const loadConversations = async () => {
    try {
      const res = await fetch('/api/conversations');
      if (res.ok) {
        const data = await res.json();
        setConversations(data);
      }
    } catch (e) {
      console.error("Error loading conversations:", e);
    }
  };

  const selectConversation = async (convId) => {
    try {
      setLoading(true);
      setCurrentConvId(convId);
      const res = await fetch(`/api/conversations/${convId}`);
      if (res.ok) {
        const data = await res.json();
        setMessages(data.messages || []);
      }
      setSidebarOpen(false);
    } catch (e) {
      console.error("Error loading conversation history:", e);
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = () => {
    setCurrentConvId(null);
    setMessages([]);
    setInputMessage('');
    setSidebarOpen(false);
    if (inputRef.current) inputRef.current.focus();
  };

  const handleDeleteConversation = async (e, convId) => {
    e.stopPropagation();
    if (!window.confirm("Deseja apagar esta conversa?")) return;

    try {
      const res = await fetch(`/api/conversations/${convId}`, { method: 'DELETE' });
      if (res.ok) {
        setConversations(prev => prev.filter(c => c.id !== convId));
        if (currentConvId === convId) {
          handleNewChat();
        }
      }
    } catch (e) {
      console.error("Error deleting conversation:", e);
    }
  };

  const handleSendMessage = async (textToSend) => {
    const text = (textToSend || inputMessage).trim();
    if (!text || loading) return;

    const tempUserMsg = {
      id: Date.now(),
      role: 'user',
      content: text,
      created_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, tempUserMsg]);
    setInputMessage('');
    setLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          conversation_id: currentConvId
        })
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP Error ${res.status}`);
      }

      const data = await res.json();

      const assistantMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: data.message,
        tool_calls: data.tool_calls || [],
        created_at: data.created_at
      };

      setMessages(prev => [...prev, assistantMsg]);
      setCurrentConvId(data.conversation_id);
      loadConversations();
    } catch (err) {
      console.error("Chat error:", err);
      const errorMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: `⚠️ Desculpe, tive uma oscilação na conexão: ${err.message}. Poderia tentar novamente em alguns segundos?`,
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const toggleToolExpand = (msgId) => {
    setExpandedTools(prev => ({
      ...prev,
      [msgId]: !prev[msgId]
    }));
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-stone-950 text-stone-100">
      {/* Mobile Sidebar Backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-72 flex-col bg-stone-900 border-r border-stone-800 transition-transform duration-300 ease-in-out lg:static lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="p-4 border-b border-stone-800 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emporio-600 to-amber-500 flex items-center justify-center text-white shadow-lg shadow-emporio-900/40">
              <Guitar className="w-6 h-6" />
            </div>
            <div>
              <h1 className="font-bold text-base tracking-tight text-white leading-tight">Empório da Música</h1>
              <p className="text-xs text-stone-400">Campo Grande • MS</p>
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-1.5 rounded-lg text-stone-400 hover:text-white hover:bg-stone-800 lg:hidden"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* New Chat Button */}
        <div className="p-3">
          <button
            onClick={handleNewChat}
            className="w-full flex items-center justify-center space-x-2 py-2.5 px-4 rounded-xl bg-emporio-600 hover:bg-emporio-500 text-white font-medium text-sm transition-all shadow-md shadow-emporio-700/20 active:scale-[0.98]"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Nova Conversa</span>
          </button>
        </div>

        {/* Conversations History List */}
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
          <p className="px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-stone-500">
            Histórico Recente
          </p>
          {conversations.length === 0 ? (
            <p className="px-3 py-4 text-xs text-stone-500 italic text-center">
              Nenhuma conversa salva ainda.
            </p>
          ) : (
            conversations.map((c) => {
              const active = c.id === currentConvId;
              return (
                <div
                  key={c.id}
                  onClick={() => selectConversation(c.id)}
                  className={`group flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium cursor-pointer transition-colors ${
                    active
                      ? 'bg-stone-800 text-white border border-stone-700'
                      : 'text-stone-300 hover:bg-stone-800/60 hover:text-white'
                  }`}
                >
                  <div className="flex items-center space-x-2.5 truncate pr-2">
                    <MessageSquare className={`w-3.5 h-3.5 shrink-0 ${active ? 'text-emporio-400' : 'text-stone-500'}`} />
                    <span className="truncate">{c.title || "Conversa"}</span>
                  </div>
                  <button
                    onClick={(e) => handleDeleteConversation(e, c.id)}
                    className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-stone-700 text-stone-400 hover:text-red-400 transition-opacity"
                    title="Excluir"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })
          )}
        </div>

        {/* Tech Stack Footer */}
        <div className="p-3 border-t border-stone-800 bg-stone-900/50 text-[11px] text-stone-400 space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-stone-500">Modelo:</span>
            <span className="font-mono text-emerald-400">{health?.model || 'gemini-3.1-flash-lite'}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-stone-500">Vector Store:</span>
            <span className="font-mono text-amber-400">Qdrant ({health?.total_indexed_policies || 10} chunks)</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-stone-500">Produtos DB:</span>
            <span className="font-mono text-cyan-400">{health?.total_products || 65} itens</span>
          </div>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col h-full bg-stone-950 relative overflow-hidden">
        {/* Header Bar */}
        <header className="h-16 px-4 lg:px-6 border-b border-stone-800 flex items-center justify-between bg-stone-900/60 backdrop-blur-md shrink-0">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 rounded-lg text-stone-400 hover:text-white hover:bg-stone-800 lg:hidden"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="flex items-center space-x-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-sm font-semibold text-white">Atendimento Empório da Música</span>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className="hidden sm:inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-stone-800 text-stone-300 border border-stone-700">
              Rua 14 de Maio, 3200 • (67) 3341-4444
            </span>
          </div>
        </header>

        {/* Message Feed */}
        <div className="flex-1 overflow-y-auto p-4 lg:p-6 space-y-6">
          {messages.length === 0 ? (
            /* Welcome Empty State with Actionable Prompts */
            <div className="max-w-2xl mx-auto py-8 text-center space-y-6">
              <div className="inline-flex p-4 rounded-2xl bg-stone-900 border border-stone-800 text-emporio-400 shadow-xl">
                <Guitar className="w-12 h-12" />
              </div>
              <div className="space-y-2">
                <h2 className="text-2xl font-bold text-white tracking-tight">
                  Bem-vindo à Empório da Música! 🎸
                </h2>
                <p className="text-sm text-stone-400 max-w-lg mx-auto">
                  Olá! Sou o assistente virtual inteligente da loja. Posso consultar nosso estoque em tempo real, checar status de pedidos, explicar regras de devolução e te ajudar a escolher o instrumento perfeito.
                </p>
              </div>

              {/* Suggestions Grid */}
              <div className="pt-4 grid grid-cols-1 sm:grid-cols-2 gap-3 text-left">
                {SUGGESTIONS.map((item, idx) => {
                  const Icon = item.icon;
                  return (
                    <button
                      key={idx}
                      onClick={() => handleSendMessage(item.prompt)}
                      className="p-3.5 rounded-xl bg-stone-900 hover:bg-stone-800/80 border border-stone-800 hover:border-emporio-600/50 transition-all text-left group active:scale-[0.99]"
                    >
                      <div className="flex items-center space-x-2 text-emporio-400 group-hover:text-emporio-300 mb-1">
                        <Icon className="w-4 h-4" />
                        <span className="text-xs font-semibold">{item.title}</span>
                      </div>
                      <p className="text-xs text-stone-400 group-hover:text-stone-300 leading-snug">
                        "{item.prompt}"
                      </p>
                    </button>
                  );
                })}
              </div>
            </div>
          ) : (
            /* Conversation Messages */
            <div className="max-w-3xl mx-auto space-y-6">
              {messages.map((m) => {
                const isUser = m.role === 'user';
                const hasTools = m.tool_calls && m.tool_calls.length > 0;
                const isToolsOpen = expandedTools[m.id];

                return (
                  <div
                    key={m.id}
                    className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
                  >
                    {/* Avatar */}
                    <div
                      className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 text-xs font-bold ${
                        isUser
                          ? 'bg-emporio-600 text-white shadow-md'
                          : 'bg-stone-800 border border-stone-700 text-emporio-400'
                      }`}
                    >
                      {isUser ? 'VC' : <Guitar className="w-4 h-4" />}
                    </div>

                    {/* Bubble Content */}
                    <div className={`space-y-1.5 max-w-[85%] sm:max-w-[78%]`}>
                      {/* Optional Tool Calls Disclosure for Assistant */}
                      {!isUser && hasTools && (
                        <div className="mb-2">
                          <button
                            onClick={() => toggleToolExpand(m.id)}
                            className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-stone-900/90 border border-amber-500/30 text-[11px] text-amber-300 hover:bg-stone-800 transition-colors"
                          >
                            <Wrench className="w-3 h-3 text-amber-400" />
                            <span>
                              {m.tool_calls.length} consulta{m.tool_calls.length > 1 ? 's' : ''} realizada{m.tool_calls.length > 1 ? 's' : ''} nos sistemas da loja
                            </span>
                            {isToolsOpen ? (
                              <ChevronUp className="w-3 h-3" />
                            ) : (
                              <ChevronDown className="w-3 h-3" />
                            )}
                          </button>

                          {isToolsOpen && (
                            <div className="mt-1.5 p-3 rounded-xl bg-stone-900 border border-stone-800 text-[11px] font-mono space-y-2">
                              {m.tool_calls.map((tc, idx) => (
                                <div key={idx} className="border-b border-stone-800 last:border-0 pb-1.5 last:pb-0">
                                  <div className="text-amber-400 font-semibold flex items-center space-x-1">
                                    <span>⚙️</span>
                                    <span>{tc.tool}</span>
                                  </div>
                                  <div className="text-stone-400 overflow-x-auto mt-0.5">
                                    <pre>{JSON.stringify(tc.arguments, null, 2)}</pre>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}

                      {/* Message Text Bubble */}
                      <div
                        className={`rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm ${
                          isUser
                            ? 'bg-emporio-600 text-white rounded-tr-sm'
                            : 'bg-stone-900 border border-stone-800 text-stone-200 rounded-tl-sm'
                        }`}
                      >
                        <div className="prose prose-invert prose-stone max-w-none text-sm break-words">
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {m.content}
                          </ReactMarkdown>
                        </div>
                      </div>

                      {/* Timestamp */}
                      <div className={`text-[10px] text-stone-500 px-1 ${isUser ? 'text-right' : 'text-left'}`}>
                        {m.created_at ? new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                      </div>
                    </div>
                  </div>
                );
              })}

              {/* Loading Thinking State */}
              {loading && (
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-xl bg-stone-800 border border-stone-700 flex items-center justify-center shrink-0 text-emporio-400">
                    <Guitar className="w-4 h-4 animate-spin" />
                  </div>
                  <div className="rounded-2xl rounded-tl-sm px-4 py-3 bg-stone-900 border border-stone-800 text-xs text-stone-400 flex items-center space-x-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-emporio-400 animate-ping" />
                    <span>Consultando catálogo, políticas e preparando resposta...</span>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Bottom Input Area */}
        <div className="p-4 border-t border-stone-800 bg-stone-900/60 backdrop-blur-md shrink-0">
          <div className="max-w-3xl mx-auto">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="relative flex items-center bg-stone-900 rounded-2xl border border-stone-800 focus-within:border-emporio-600 transition-colors shadow-lg"
            >
              <textarea
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                rows={1}
                placeholder="Pergunte sobre instrumentos, preços, status de pedidos ou políticas da loja..."
                className="w-full py-3.5 pl-4 pr-12 bg-transparent text-sm text-stone-100 placeholder-stone-500 focus:outline-none resize-none max-h-32 min-h-[48px]"
              />
              <button
                type="submit"
                disabled={!inputMessage.trim() || loading}
                className="absolute right-2 p-2 rounded-xl bg-emporio-600 hover:bg-emporio-500 text-white disabled:opacity-40 disabled:cursor-not-allowed transition-all active:scale-95"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
            <p className="mt-2 text-[11px] text-stone-500 text-center">
              Empório da Música • Atendimento com IA Generativa (Gemini + Qdrant RAG + SQLite)
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
