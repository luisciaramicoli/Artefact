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
  MapPin,
  Clock,
  Phone,
  Package,
  RotateCcw,
  Guitar,
  Sparkles,
  Search,
  CheckCheck
} from 'lucide-react';

const SUGGESTIONS = [
  {
    icon: Guitar,
    title: "Violões até R$ 1.000",
    desc: "Modelos para iniciantes e estudantes com bom custo-benefício",
    prompt: "Quais opções de violões vocês têm disponíveis custando até R$ 1.000?"
  },
  {
    icon: Sparkles,
    title: "Ficha do Takamine GD20",
    desc: "Preço, formas de pagamento e especificações",
    prompt: "Quanto custa o Takamine GD20 e quais as opções de parcelamento?"
  },
  {
    icon: Package,
    title: "Acompanhar Meu Pedido",
    desc: "Consulte o status e rastreamento da entrega",
    prompt: "Gostaria de saber o status e rastreamento do meu pedido número 1."
  },
  {
    icon: RotateCcw,
    title: "Regras de Devolução",
    desc: "Direito de arrependimento e trocas pelo WhatsApp",
    prompt: "Comprei um instrumento e me arrependi da compra. Posso devolver? Como funciona o frete e o reembolso?"
  },
  {
    icon: MapPin,
    title: "Onde Fica a Loja?",
    desc: "Endereço em Campo Grande e horários de atendimento",
    prompt: "Qual o endereço da loja física e quais os horários de funcionamento?"
  },
  {
    icon: Search,
    title: "Catálogo Completo",
    desc: "Conheça todas as categorias e instrumentos da loja",
    prompt: "Quais produtos e categorias de instrumentos vocês oferecem?"
  }
];

export default function App() {
  const [conversations, setConversations] = useState([]);
  const [currentConvId, setCurrentConvId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const res = await fetch('/api/conversations');
      if (res.ok) {
        const data = await res.json();
        setConversations(data);
      }
    } catch (e) {
      console.error("Erro ao carregar conversas:", e);
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
      console.error("Erro ao carregar histórico:", e);
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
    if (!window.confirm("Deseja apagar esta conversa do seu histórico?")) return;

    try {
      const res = await fetch(`/api/conversations/${convId}`, { method: 'DELETE' });
      if (res.ok) {
        setConversations(prev => prev.filter(c => c.id !== convId));
        if (currentConvId === convId) {
          handleNewChat();
        }
      }
    } catch (e) {
      console.error("Erro ao excluir conversa:", e);
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
        throw new Error(errorData.detail || `Erro de conexão`);
      }

      const data = await res.json();

      const assistantMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: data.message,
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
        content: `Desculpe, tive uma instabilidade passageira na conexão. Poderia enviar sua pergunta novamente? Estou à disposição!`,
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-stone-950 text-stone-100 font-sans">
      {/* Mobile Backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-72 sm:w-80 flex-col bg-stone-900 border-r border-stone-800 transition-transform duration-300 ease-in-out lg:static lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="p-4 border-b border-stone-800 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-600 to-amber-400 flex items-center justify-center text-stone-950 shadow-md">
              <Guitar className="w-6 h-6 stroke-[2.2]" />
            </div>
            <div>
              <h1 className="font-bold text-base text-white tracking-tight leading-snug">Empório da Música</h1>
              <p className="text-xs text-amber-400/90 font-medium">Sua música começa aqui</p>
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
            className="w-full flex items-center justify-center space-x-2 py-2.5 px-4 rounded-xl bg-amber-600 hover:bg-amber-500 text-stone-950 font-semibold text-sm transition-all shadow-md shadow-amber-950/20 active:scale-[0.98]"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Nova Conversa</span>
          </button>
        </div>

        {/* Saved Conversations List */}
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
          <p className="px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-stone-400">
            Conversas Anteriores
          </p>
          {conversations.length === 0 ? (
            <div className="px-3 py-8 text-center text-xs text-stone-400 space-y-1">
              <MessageSquare className="w-6 h-6 mx-auto opacity-40 mb-2" />
              <p>Nenhuma conversa salva ainda.</p>
              <p className="text-[11px] text-stone-400">Inicie uma conversa ao lado!</p>
            </div>
          ) : (
            conversations.map((c) => {
              const active = c.id === currentConvId;
              return (
                <div
                  key={c.id}
                  onClick={() => selectConversation(c.id)}
                  className={`group flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium cursor-pointer transition-colors ${
                    active
                      ? 'bg-stone-800 text-white border border-stone-700 shadow-sm'
                      : 'text-stone-300 hover:bg-stone-800/60 hover:text-white'
                  }`}
                >
                  <div className="flex items-center space-x-2.5 truncate pr-2">
                    <MessageSquare className={`w-3.5 h-3.5 shrink-0 ${active ? 'text-amber-400' : 'text-stone-400'}`} />
                    <span className="truncate">{c.title || "Atendimento"}</span>
                  </div>
                  <button
                    onClick={(e) => handleDeleteConversation(e, c.id)}
                    className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-stone-700 text-stone-400 hover:text-red-400 transition-opacity"
                    title="Excluir conversa"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })
          )}
        </div>

        {/* Customer Information Footer */}
        <div className="p-4 border-t border-stone-800 bg-stone-900/60 text-xs text-stone-300 space-y-2.5">
          <div className="flex items-start space-x-2">
            <MapPin className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
            <span className="text-[11px] leading-tight">Rua 14 de Maio, 3200 — Centro, Campo Grande - MS</span>
          </div>
          <div className="flex items-center space-x-2">
            <Clock className="w-3.5 h-3.5 text-amber-400 shrink-0" />
            <span className="text-[11px]">Seg a Sex 09h–18h | Sáb 09h–13h</span>
          </div>
          <div className="flex items-center space-x-2">
            <Phone className="w-3.5 h-3.5 text-amber-400 shrink-0" />
            <span className="text-[11px] font-medium text-stone-200">(67) 3341-4444</span>
          </div>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col h-full bg-stone-950 relative overflow-hidden">
        {/* Header Bar */}
        <header className="h-16 px-4 lg:px-6 border-b border-stone-800 flex items-center justify-between bg-stone-900/70 backdrop-blur-md shrink-0">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 rounded-lg text-stone-400 hover:text-white hover:bg-stone-800 lg:hidden"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="relative">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-amber-600 to-amber-400 flex items-center justify-center text-stone-950 shadow">
                <Guitar className="w-5 h-5 stroke-[2.2]" />
              </div>
              <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-emerald-500 ring-2 ring-stone-900" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white leading-tight">Empório da Música</h2>
              <div className="flex items-center space-x-1.5 text-[11px] text-emerald-400">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                <span>Atendente Virtual • Online</span>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleNewChat}
              className="hidden sm:inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-stone-800 hover:bg-stone-700/80 text-stone-200 text-xs font-medium border border-stone-700 transition-colors"
            >
              <PlusCircle className="w-3.5 h-3.5 text-amber-400" />
              <span>Nova Conversa</span>
            </button>
          </div>
        </header>

        {/* Message Feed */}
        <div className="flex-1 overflow-y-auto p-4 lg:p-6 space-y-6">
          {messages.length === 0 ? (
            /* Welcome State with Customer-Focused Prompts */
            <div className="max-w-2xl mx-auto py-8 text-center space-y-6">
              <div className="inline-flex p-4 rounded-2xl bg-gradient-to-b from-stone-800 to-stone-900 border border-stone-800 text-amber-400 shadow-xl">
                <Guitar className="w-10 h-10 stroke-[1.8]" />
              </div>
              <div className="space-y-2">
                <h2 className="text-2xl font-bold text-white tracking-tight">
                  Olá! Como posso ajudar você hoje? 🎸
                </h2>
                <p className="text-sm text-stone-300 max-w-lg mx-auto leading-relaxed">
                  Bem-vindo à <strong>Empório da Música</strong>! Estou aqui para te ajudar a escolher o instrumento perfeito, consultar preços, tirar dúvidas sobre entregas ou acompanhar seus pedidos.
                </p>
              </div>

              {/* Suggestions Grid */}
              <div className="pt-2 grid grid-cols-1 sm:grid-cols-2 gap-3 text-left">
                {SUGGESTIONS.map((item, idx) => {
                  const Icon = item.icon;
                  return (
                    <button
                      key={idx}
                      onClick={() => handleSendMessage(item.prompt)}
                      className="p-3.5 rounded-2xl bg-stone-900/90 hover:bg-stone-800/90 border border-stone-800 hover:border-amber-500/40 transition-all text-left group active:scale-[0.99] shadow-sm"
                    >
                      <div className="flex items-center space-x-2 text-amber-400 group-hover:text-amber-300 mb-1">
                        <Icon className="w-4 h-4" />
                        <span className="text-xs font-semibold">{item.title}</span>
                      </div>
                      <p className="text-xs text-stone-300 group-hover:text-stone-200 leading-snug">
                        {item.desc}
                      </p>
                    </button>
                  );
                })}
              </div>
            </div>
          ) : (
            /* Conversation Messages */
            <div className="max-w-3xl mx-auto space-y-5">
              {messages.map((m) => {
                const isUser = m.role === 'user';

                return (
                  <div
                    key={m.id}
                    className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
                  >
                    {/* Avatar */}
                    <div
                      className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 text-xs font-bold ${
                        isUser
                          ? 'bg-amber-600 text-stone-950 shadow-md font-semibold'
                          : 'bg-stone-800 border border-stone-700 text-amber-400'
                      }`}
                    >
                      {isUser ? 'Você' : <Guitar className="w-4 h-4" />}
                    </div>

                    {/* Bubble Content */}
                    <div className="space-y-1 max-w-[85%] sm:max-w-[78%]">
                      <div
                        className={`rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm ${
                          isUser
                            ? 'bg-amber-600 text-stone-950 rounded-tr-sm font-medium'
                            : 'bg-stone-900 border border-stone-800 text-stone-200 rounded-tl-sm'
                        }`}
                      >
                        <div className={`prose ${isUser ? 'text-stone-950 prose-invert-0' : 'prose-invert prose-stone'} max-w-none text-sm break-words`}>
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {m.content}
                          </ReactMarkdown>
                        </div>
                      </div>

                      {/* Timestamp & Status */}
                      <div className={`flex items-center space-x-1 text-[10px] text-stone-400 px-1 ${isUser ? 'justify-end' : 'justify-start'}`}>
                        <span>
                          {m.created_at ? new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                        </span>
                        {isUser && <CheckCheck className="w-3 h-3 text-amber-400/80 inline" />}
                      </div>
                    </div>
                  </div>
                );
              })}

              {/* Typing Indicator */}
              {loading && (
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-xl bg-stone-800 border border-stone-700 flex items-center justify-center shrink-0 text-amber-400">
                    <Guitar className="w-4 h-4 animate-pulse" />
                  </div>
                  <div className="rounded-2xl rounded-tl-sm px-4 py-3 bg-stone-900 border border-stone-800 text-stone-300 flex items-center space-x-2 text-xs">
                    <div className="flex space-x-1 items-center py-0.5">
                      <span className="w-2 h-2 rounded-full bg-amber-400 animate-bounce [animation-delay:-0.3s]" />
                      <span className="w-2 h-2 rounded-full bg-amber-400 animate-bounce [animation-delay:-0.15s]" />
                      <span className="w-2 h-2 rounded-full bg-amber-400 animate-bounce" />
                    </div>
                    <span className="text-stone-400 text-xs pl-1">Consultando informações...</span>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Bottom Input Area */}
        <div className="p-4 border-t border-stone-800 bg-stone-900/70 backdrop-blur-md shrink-0">
          <div className="max-w-3xl mx-auto">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="relative flex items-center bg-stone-900 rounded-2xl border border-stone-800 focus-within:border-amber-500/80 transition-colors shadow-lg"
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
                placeholder="Digite sua dúvida sobre instrumentos, pedidos ou políticas..."
                className="w-full py-3.5 pl-4 pr-12 bg-transparent text-sm text-stone-100 placeholder-stone-400 focus:outline-none resize-none max-h-32 min-h-[48px]"
              />
              <button
                type="submit"
                disabled={!inputMessage.trim() || loading}
                className="absolute right-2 p-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-stone-950 disabled:opacity-30 disabled:cursor-not-allowed transition-all active:scale-95 shadow-sm"
                title="Enviar mensagem"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
            <p className="mt-2 text-[11px] text-stone-400 text-center">
              Empório da Música • Atendimento Oficial • Campo Grande / MS
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
