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
  Sliders,
  Compass,
  CheckCheck,
  User,
  Store,
  AlertTriangle
} from 'lucide-react';

const SUGGESTIONS = [
  {
    icon: Guitar,
    title: "Violões até R$ 1.000",
    desc: "Modelos para iniciantes e estudantes com bom custo-benefício",
    prompt: "Quais opções de violões vocês têm disponíveis custando até R$ 1.000?"
  },
  {
    icon: Sliders,
    title: "Ficha do Takamine GD20",
    desc: "Preço, formas de pagamento e especificações",
    prompt: "Quanto custa o Takamine GD20 e quais as opções de parcelamento?"
  },
  {
    icon: Package,
    title: "Acompanhar Pedido",
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
    title: "Localização da Loja",
    desc: "Endereço em Campo Grande e horários de atendimento",
    prompt: "Qual o endereço da loja física e quais os horários de funcionamento?"
  },
  {
    icon: Compass,
    title: "Catálogo Completo",
    desc: "Conheça todas as categorias e instrumentos da loja",
    prompt: "Quais produtos e categorias de instrumentos vocês oferecem?"
  }
];

export default function App() {
  const [conversations, setConversations] = useState([]);
  const [currentConvId, setCurrentConvId] = useState(() => {
    return localStorage.getItem('emporio_conv_id') || null;
  });
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Modal confirmation state for deletion
  const [deleteModal, setDeleteModal] = useState({
    isOpen: false,
    type: null, // 'single' | 'all'
    convId: null,
    title: ''
  });

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Load conversations on mount and auto-resume last session
  useEffect(() => {
    const initSessions = async () => {
      try {
        const res = await fetch('/api/conversations');
        if (res.ok) {
          const data = await res.json();
          setConversations(data);

          const savedId = localStorage.getItem('emporio_conv_id');
          if (savedId) {
            const exists = data.some(c => c.id === savedId);
            if (exists) {
              await selectConversation(savedId);
              return;
            }
          }
          if (data.length > 0) {
            await selectConversation(data[0].id);
          }
        }
      } catch (e) {
        console.error("Erro ao carregar conversas:", e);
      }
    };
    initSessions();
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
    if (!convId) return;
    try {
      setLoading(true);
      setCurrentConvId(convId);
      localStorage.setItem('emporio_conv_id', convId);
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
    localStorage.removeItem('emporio_conv_id');
    setCurrentConvId(null);
    setMessages([]);
    setInputMessage('');
    setSidebarOpen(false);
    if (inputRef.current) inputRef.current.focus();
  };

  // Open delete single dialog
  const openDeleteSingle = (convId, title, e) => {
    if (e) e.stopPropagation();
    setDeleteModal({
      isOpen: true,
      type: 'single',
      convId,
      title: title || 'este atendimento'
    });
  };

  // Open delete all dialog
  const openDeleteAll = (e) => {
    if (e) e.stopPropagation();
    setDeleteModal({
      isOpen: true,
      type: 'all',
      convId: null,
      title: 'todo o histórico de atendimentos'
    });
  };

  // Confirm and execute deletion
  const handleConfirmDelete = async () => {
    try {
      if (deleteModal.type === 'single' && deleteModal.convId) {
        const res = await fetch(`/api/conversations/${deleteModal.convId}`, { method: 'DELETE' });
        if (res.ok) {
          setConversations(prev => prev.filter(c => c.id !== deleteModal.convId));
          if (currentConvId === deleteModal.convId) {
            handleNewChat();
          }
        }
      } else if (deleteModal.type === 'all') {
        const res = await fetch('/api/conversations', { method: 'DELETE' });
        if (res.ok) {
          setConversations([]);
          handleNewChat();
        }
      }
    } catch (e) {
      console.error("Erro ao excluir:", e);
    } finally {
      setDeleteModal({ isOpen: false, type: null, convId: null, title: '' });
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
      localStorage.setItem('emporio_conv_id', data.conversation_id);
      loadConversations();
    } catch (err) {
      console.error("Chat error:", err);
      const errorMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: `Desculpe, tive uma instabilidade passageira na conexão. Poderia enviar sua pergunta novamente? Estou à disposição.`,
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  // Helper to remove any residual emojis from text if present
  const sanitizeText = (text) => {
    if (!text) return "";
    return text.replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1F900}-\u{1F9FF}\u{1F018}-\u{1F270}]/gu, '');
  };

  // Get active conversation title
  const activeConversation = conversations.find(c => c.id === currentConvId);

  return (
    <div className="flex h-[100dvh] w-full min-h-[100dvh] max-h-[100dvh] overflow-hidden bg-stone-950 text-stone-100 font-sans antialiased selection:bg-amber-500/30">
      
      {/* Mobile Backdrop Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm transition-opacity lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Delete Confirmation Modal */}
      {deleteModal.isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="w-full max-w-sm rounded-2xl bg-stone-900 border border-stone-800 p-5 shadow-2xl space-y-4">
            <div className="flex items-center space-x-3 text-red-400">
              <div className="p-2.5 rounded-xl bg-red-950/60 border border-red-800/50">
                <Trash2 className="w-5 h-5 text-red-400" />
              </div>
              <div>
                <h3 className="font-semibold text-white text-sm">
                  {deleteModal.type === 'all' ? "Limpar todo o histórico?" : "Excluir atendimento?"}
                </h3>
                <p className="text-xs text-stone-400">Esta ação é irreversível</p>
              </div>
            </div>

            <p className="text-xs text-stone-300 leading-relaxed">
              {deleteModal.type === 'all'
                ? "Deseja excluir permanentemente todas as conversas salvas no seu histórico de atendimento?"
                : `Deseja remover permanentemente o atendimento "${sanitizeText(deleteModal.title)}"?`}
            </p>

            <div className="flex items-center justify-end space-x-2.5 pt-2">
              <button
                type="button"
                onClick={() => setDeleteModal({ isOpen: false, type: null, convId: null, title: '' })}
                className="px-4 py-2 rounded-xl text-xs font-medium text-stone-300 hover:text-white bg-stone-800 hover:bg-stone-700 transition-colors"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={handleConfirmDelete}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-white bg-red-600 hover:bg-red-500 active:scale-95 transition-all shadow-md shadow-red-950/40 flex items-center space-x-1.5"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Excluir</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Sidebar Drawer */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-[84vw] max-w-[320px] flex-col bg-stone-900 border-r border-stone-800 transition-transform duration-300 ease-in-out lg:static lg:w-72 xl:w-80 lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="p-4 border-b border-stone-800 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-600 to-amber-500 flex items-center justify-center text-stone-950 shadow-md shrink-0">
              <Guitar className="w-5 h-5 stroke-[2.2]" />
            </div>
            <div className="min-w-0">
              <h1 className="font-bold text-sm sm:text-base text-white tracking-tight leading-snug truncate">
                Empório da Música
              </h1>
              <p className="text-[11px] sm:text-xs text-amber-400 font-medium truncate">Atendimento Especializado</p>
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-2 rounded-xl text-stone-400 hover:text-white hover:bg-stone-800 lg:hidden min-w-[36px] min-h-[36px] flex items-center justify-center"
            title="Fechar menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* New Chat Button */}
        <div className="p-3 shrink-0">
          <button
            onClick={handleNewChat}
            className="w-full flex items-center justify-center space-x-2 py-2.5 px-4 rounded-xl bg-amber-600 hover:bg-amber-500 text-stone-950 font-semibold text-xs sm:text-sm transition-all shadow-md shadow-amber-950/20 active:scale-[0.98]"
          >
            <PlusCircle className="w-4 h-4 shrink-0" />
            <span>Novo Atendimento</span>
          </button>
        </div>

        {/* Conversations History Section */}
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1 overscroll-contain">
          <div className="flex items-center justify-between px-2 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-stone-400">
            <span>Histórico de Atendimento</span>
            {conversations.length > 0 && (
              <button
                onClick={openDeleteAll}
                className="text-[10px] lowercase text-stone-400 hover:text-red-400 active:text-red-300 flex items-center space-x-1 p-1 rounded transition-colors"
                title="Limpar todo o histórico"
              >
                <Trash2 className="w-3 h-3" />
                <span>limpar tudo</span>
              </button>
            )}
          </div>

          {conversations.length === 0 ? (
            <div className="px-3 py-10 text-center text-xs text-stone-400 space-y-1">
              <MessageSquare className="w-6 h-6 mx-auto opacity-40 mb-2" />
              <p>Nenhuma conversa gravada.</p>
              <p className="text-[11px] text-stone-500">Inicie uma nova mensagem ao lado.</p>
            </div>
          ) : (
            conversations.map((c) => {
              const active = c.id === currentConvId;
              const titleText = sanitizeText(c.title) || "Atendimento";

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
                  <div className="flex items-center space-x-2.5 truncate pr-1 min-w-0 flex-1">
                    <MessageSquare className={`w-3.5 h-3.5 shrink-0 ${active ? 'text-amber-400' : 'text-stone-400'}`} />
                    <span className="truncate">{titleText}</span>
                  </div>

                  {/* Delete Conversation Button: Always visible on touch/mobile, hover on desktop */}
                  <button
                    type="button"
                    onClick={(e) => openDeleteSingle(c.id, titleText, e)}
                    className="p-1.5 rounded-lg text-stone-400 hover:text-red-400 hover:bg-stone-700/80 active:bg-red-950/40 opacity-75 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity shrink-0 ml-1"
                    title="Excluir este atendimento"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })
          )}
        </div>

        {/* Store Info Footer */}
        <div className="p-3.5 border-t border-stone-800 bg-stone-900/60 text-xs text-stone-300 space-y-2 shrink-0">
          <div className="flex items-start space-x-2">
            <MapPin className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
            <span className="text-[11px] leading-tight">Rua 14 de Maio, 3200 — Centro, Campo Grande - MS</span>
          </div>
          <div className="flex items-center space-x-2">
            <Clock className="w-3.5 h-3.5 text-amber-400 shrink-0" />
            <span className="text-[11px]">Seg a Sex: 09h às 18h | Sáb: 09h às 13h</span>
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
        <header className="h-14 sm:h-16 px-3 sm:px-6 border-b border-stone-800 flex items-center justify-between bg-stone-900/70 backdrop-blur-md shrink-0 z-10">
          <div className="flex items-center space-x-2.5 sm:space-x-3 min-w-0">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 rounded-xl text-stone-300 hover:text-white hover:bg-stone-800 lg:hidden min-w-[40px] min-h-[40px] flex items-center justify-center shrink-0 active:scale-95"
              title="Abrir histórico e menu"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="relative shrink-0">
              <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-xl bg-gradient-to-tr from-amber-600 to-amber-500 flex items-center justify-center text-stone-950 shadow">
                <Store className="w-4 h-4 sm:w-5 sm:h-5 stroke-[2.2]" />
              </div>
              <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-emerald-500 ring-2 ring-stone-900" />
            </div>
            <div className="min-w-0">
              <h2 className="text-xs sm:text-sm font-semibold text-white leading-tight truncate">
                Empório da Música
              </h2>
              <div className="flex items-center space-x-1.5 text-[10px] sm:text-[11px] text-emerald-400 font-medium">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse shrink-0" />
                <span className="truncate">Atendimento Online</span>
              </div>
            </div>
          </div>

          {/* Header Action Buttons */}
          <div className="flex items-center space-x-1.5 sm:space-x-2 shrink-0">
            {/* Delete Active Session Button */}
            {currentConvId && (
              <button
                type="button"
                onClick={() => openDeleteSingle(currentConvId, activeConversation?.title)}
                className="inline-flex items-center justify-center space-x-1.5 p-2 sm:px-2.5 sm:py-1.5 rounded-lg text-stone-400 hover:text-red-400 hover:bg-red-950/30 border border-stone-800 hover:border-red-900/40 text-xs font-medium transition-all active:scale-95 whitespace-nowrap"
                title="Excluir este atendimento"
              >
                <Trash2 className="w-3.5 h-3.5 shrink-0" />
                <span className="hidden sm:inline">Excluir</span>
              </button>
            )}

            {/* New Chat Button */}
            <button
              onClick={handleNewChat}
              className="inline-flex items-center justify-center space-x-1.5 p-2 sm:px-3 sm:py-1.5 rounded-lg bg-stone-800 hover:bg-stone-700/80 text-stone-200 text-xs font-medium border border-stone-700 transition-colors active:scale-95 whitespace-nowrap"
              title="Iniciar novo atendimento"
            >
              <PlusCircle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
              <span className="hidden sm:inline">Nova Conversa</span>
            </button>
          </div>
        </header>

        {/* Message Feed */}
        <div className="flex-1 overflow-y-auto p-3 sm:p-5 lg:p-6 space-y-4 sm:space-y-6 overscroll-contain">
          {messages.length === 0 ? (
            /* Welcome State */
            <div className="max-w-2xl mx-auto py-4 sm:py-8 text-center space-y-4 sm:space-y-6">
              <div className="inline-flex p-3 sm:p-4 rounded-2xl bg-gradient-to-b from-stone-800 to-stone-900 border border-stone-800 text-amber-400 shadow-xl">
                <Guitar className="w-8 h-8 sm:w-10 sm:h-10 stroke-[1.8]" />
              </div>
              <div className="space-y-1.5 sm:space-y-2 px-2">
                <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
                  Como podemos ajudar você hoje?
                </h2>
                <p className="text-xs sm:text-sm text-stone-300 max-w-lg mx-auto leading-relaxed">
                  Bem-vindo à <strong>Empório da Música</strong>. Consulte modelos, preços com desconto no PIX, rastreio de pedidos e prazos de garantia.
                </p>
              </div>

              {/* Suggestions Grid */}
              <div className="pt-2 grid grid-cols-1 sm:grid-cols-2 gap-2.5 sm:gap-3 text-left">
                {SUGGESTIONS.map((item, idx) => {
                  const Icon = item.icon;
                  return (
                    <button
                      key={idx}
                      onClick={() => handleSendMessage(item.prompt)}
                      className="p-3 sm:p-3.5 rounded-2xl bg-stone-900/90 hover:bg-stone-800/90 border border-stone-800 hover:border-amber-500/40 transition-all text-left group active:scale-[0.98] shadow-sm flex items-start space-x-3"
                    >
                      <div className="p-2 rounded-xl bg-stone-800 text-amber-400 group-hover:bg-amber-600 group-hover:text-stone-950 transition-colors shrink-0">
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <span className="text-xs font-semibold text-white group-hover:text-amber-300 block mb-0.5 truncate">
                          {item.title}
                        </span>
                        <p className="text-[11px] sm:text-xs text-stone-400 group-hover:text-stone-300 leading-snug line-clamp-2">
                          {item.desc}
                        </p>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          ) : (
            /* Conversation Messages */
            <div className="max-w-3xl mx-auto space-y-4 sm:space-y-5">
              {messages.map((m) => {
                const isUser = m.role === 'user';
                const cleanContent = sanitizeText(m.content);

                return (
                  <div
                    key={m.id}
                    className={`flex items-start gap-2.5 sm:gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
                  >
                    {/* Avatar */}
                    <div
                      className={`w-7 h-7 sm:w-8 sm:h-8 rounded-xl flex items-center justify-center shrink-0 text-xs shadow-sm ${
                        isUser
                          ? 'bg-amber-600 text-stone-950'
                          : 'bg-stone-800 border border-stone-700 text-amber-400'
                      }`}
                    >
                      {isUser ? <User className="w-3.5 h-3.5 sm:w-4 sm:h-4 stroke-[2.2]" /> : <Store className="w-3.5 h-3.5 sm:w-4 sm:h-4 stroke-[2]" />}
                    </div>

                    {/* Bubble Content */}
                    <div className="space-y-1 max-w-[88%] sm:max-w-[78%]">
                      <div
                        className={`rounded-2xl px-3.5 py-2.5 sm:px-4 sm:py-3 text-[13px] sm:text-sm leading-relaxed shadow-sm ${
                          isUser
                            ? 'bg-amber-600 text-stone-950 rounded-tr-sm font-medium'
                            : 'bg-stone-900 border border-stone-800 text-stone-200 rounded-tl-sm'
                        }`}
                      >
                        <div className={`prose ${isUser ? 'text-stone-950 prose-invert-0' : 'prose-invert prose-stone'} max-w-none text-[13px] sm:text-sm break-words overflow-x-auto`}>
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              li: ({ node, children, ...props }) => (
                                <li className="my-1.5 list-disc ml-4 leading-relaxed" {...props}>
                                  {children}
                                </li>
                              )
                            }}
                          >
                            {cleanContent}
                          </ReactMarkdown>
                        </div>
                      </div>

                      {/* Timestamp & Status */}
                      <div className={`flex items-center space-x-1 text-[10px] text-stone-400 px-1 ${isUser ? 'justify-end' : 'justify-start'}`}>
                        <span>
                          {m.created_at ? new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                        </span>
                        {isUser && <CheckCheck className="w-3.5 h-3.5 text-amber-400 inline" />}
                      </div>
                    </div>
                  </div>
                );
              })}

              {/* Typing Indicator */}
              {loading && (
                <div className="flex items-start gap-2.5 sm:gap-3">
                  <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-stone-800 border border-stone-700 flex items-center justify-center shrink-0 text-amber-400">
                    <Store className="w-3.5 h-3.5 sm:w-4 sm:h-4 animate-pulse" />
                  </div>
                  <div className="rounded-2xl rounded-tl-sm px-3.5 py-2.5 bg-stone-900 border border-stone-800 text-stone-300 flex items-center space-x-2 text-xs">
                    <div className="flex space-x-1 items-center py-0.5">
                      <span className="w-2 h-2 rounded-full bg-amber-400 animate-bounce [animation-delay:-0.3s]" />
                      <span className="w-2 h-2 rounded-full bg-amber-400 animate-bounce [animation-delay:-0.15s]" />
                      <span className="w-2 h-2 rounded-full bg-amber-400 animate-bounce" />
                    </div>
                    <span className="text-stone-400 text-[11px] sm:text-xs pl-1">Consultando informações...</span>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Bottom Input Area */}
        <div className="p-2.5 sm:p-4 border-t border-stone-800 bg-stone-900/80 backdrop-blur-md shrink-0 pb-[max(0.75rem,env(safe-area-inset-bottom))]">
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
                placeholder="Pergunte sobre produtos, pedidos, trocas..."
                className="w-full py-3 sm:py-3.5 pl-3.5 sm:pl-4 pr-12 bg-transparent text-base sm:text-sm text-stone-100 placeholder-stone-400 focus:outline-none resize-none max-h-32 min-h-[44px]"
              />
              <button
                type="submit"
                disabled={!inputMessage.trim() || loading}
                className="absolute right-1.5 sm:right-2 p-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-stone-950 disabled:opacity-30 disabled:cursor-not-allowed transition-all active:scale-95 shadow-sm min-w-[36px] min-h-[36px] flex items-center justify-center"
                title="Enviar mensagem"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
            <p className="mt-1.5 text-[10px] sm:text-[11px] text-stone-400 text-center truncate">
              Empório da Música • Atendimento Oficial • Campo Grande / MS
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
