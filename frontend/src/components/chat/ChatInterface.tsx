'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Terminal, Shield, MessageSquare, Trash2, Settings, Download, Copy, Check, AlertCircle, Loader2, Menu, X } from 'lucide-react';

interface Message {
    type: 'system' | 'user' | 'chat' | 'os_command' | 'osquery' | 'error' | 'dashboard';
    content: string;
    timestamp: number;
}

const ChatInterface = () => {
    const [mounted, setMounted] = useState(false);
    const [messages, setMessages] = useState<Message[]>([
        {
            type: 'system',
            content: 'Welcome to LiaAI - Your AI-powered cyber assistant. I can help with chat, OS commands, and security queries.',
            timestamp: Date.now()
        }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('all');
    const [copiedId, setCopiedId] = useState<number | null>(null);
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        setMounted(true);
    }, []);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const detectMessageType = (content: string): Message['type'] => {
        if (content.includes('🛠 Executed:') || content.includes('Command:')) return 'os_command';
        if (content.includes('🔍 Query:') || content.includes('SELECT')) return 'osquery';
        if (content.includes('⚠') || content.includes('Error')) return 'error';
        if (content.includes('🛡️  LIAAI SECURITY DASHBOARD')) return 'dashboard';
        return 'chat';
    };

    const handleSubmit = () => {
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            type: 'user',
            content: input,
            timestamp: Date.now()
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        setTimeout(() => {
            const response = simulateResponse(input);
            const aiMessage: Message = {
                type: detectMessageType(response),
                content: response,
                timestamp: Date.now()
            };
            setMessages(prev => [...prev, aiMessage]);
            setIsLoading(false);
        }, 1500);
    };

    const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    const simulateResponse = (query: string) => {
        const lowerQuery = query.toLowerCase();

        if (lowerQuery.includes('dashboard') || lowerQuery.includes('security status')) {
            return `🛡️  LIAAI SECURITY DASHBOARD
======================================================================
📊 SYSTEM OVERVIEW
----------------------------------------------------------------------
  Hostname: dev-machine
  CPU: Intel Core i7-9750H
  Memory: 16.00 GB

👤 USER ACTIVITY
----------------------------------------------------------------------
  Logged in users: 1
  - admin on console
  Total system users: 12

🌐 NETWORK SECURITY
----------------------------------------------------------------------
  Listening ports: 15
  Active external connections: 8
  Privileged ports in use: 3

⚙️  PROCESS SECURITY
----------------------------------------------------------------------
  Running processes: 247
  Root-owned processes: 45

🚨 SECURITY ALERTS
----------------------------------------------------------------------
  ✅ No immediate security concerns detected

======================================================================`;
        }

        if (lowerQuery.includes('process') || lowerQuery.includes('running')) {
            return `🔍 Query: SELECT pid, name, cmdline FROM processes LIMIT 10;

Results (10 rows):

| pid | name | cmdline |
|---|---|---|
| 1 | systemd | /sbin/init |
| 234 | chrome | /opt/google/chrome/chrome |
| 567 | python3 | python3 app.py |
| 890 | firefox | /usr/lib/firefox/firefox |
| 1234 | code | /usr/share/code/code |`;
        }

        if (lowerQuery.includes('port') || lowerQuery.includes('listening')) {
            return `🔍 Query: SELECT port, protocol, address FROM listening_ports LIMIT 10;

Results (10 rows):

| port | protocol | address |
|---|---|---|
| 22 | TCP | 0.0.0.0 |
| 80 | TCP | 0.0.0.0 |
| 443 | TCP | 0.0.0.0 |
| 3000 | TCP | 127.0.0.1 |`;
        }

        if (lowerQuery.includes('list') || lowerQuery.includes('ls')) {
            return `🛠 Executed: ls -la

Output:
total 48
drwxr-xr-x  8 user  staff   256 Dec  6 10:30 .
drwxr-xr-x  5 user  staff   160 Dec  5 14:20 ..
-rw-r--r--  1 user  staff  1234 Dec  6 09:15 app.py`;
        }

        return "I'm here to help! I can execute OS commands, run security queries with osquery, or just chat. Try asking me to 'show running processes', 'list files', or 'show security dashboard'.";
    };

    const clearChat = () => {
        setMessages([{
            type: 'system',
            content: 'Chat cleared. How can I assist you?',
            timestamp: Date.now()
        }]);
    };

    const copyToClipboard = (content: string, id: number) => {
        navigator.clipboard.writeText(content);
        setCopiedId(id);
        setTimeout(() => setCopiedId(null), 2000);
    };

    const exportChat = () => {
        const chatText = messages.map(m => {
            const date = new Date(m.timestamp);
            return `[${date.toLocaleTimeString()}] ${m.type.toUpperCase()}: ${m.content}`;
        }).join('\n\n');

        const blob = new Blob([chatText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `liaai-chat-${Date.now()}.txt`;
        a.click();
    };

    const filteredMessages = activeTab === 'all'
        ? messages
        : messages.filter(m => m.type === activeTab || m.type === 'user');

    const quickActions = [
        { icon: MessageSquare, label: 'Show processes', query: 'Show me running processes' },
        { icon: Shield, label: 'Security scan', query: 'Show security dashboard' },
        { icon: Terminal, label: 'List files', query: 'List files in current directory' },
    ];

    const MessageBubble = ({ message, index }: { message: Message; index: number }) => {
        const isUser = message.type === 'user';
        const isSystem = message.type === 'system';
        const isError = message.type === 'error';
        const isDashboard = message.type === 'dashboard';

        const formatTime = (timestamp: number) => {
            if (!mounted) return '';
            const date = new Date(timestamp);
            return date.toLocaleTimeString();
        };

        return (
            <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 message-enter`}>
                <div className={`max-w-[80%] rounded-2xl px-5 py-4 shadow-lg transition-all duration-300 hover:shadow-xl ${isUser
                    ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white'
                    : isSystem
                        ? 'bg-gradient-to-br from-purple-500 to-purple-600 text-white'
                        : isError
                            ? 'bg-gradient-to-br from-red-500 to-red-600 text-white'
                            : 'glass text-white'
                    }`}>
                    <div className="flex items-start justify-between gap-3">
                        <div className="flex-1 min-w-0">
                            {message.type === 'os_command' && (
                                <div className="flex items-center gap-2 mb-2 pb-2 border-b border-white/20">
                                    <Terminal className="w-4 h-4 text-cyan-300 flex-shrink-0" />
                                    <span className="text-xs font-semibold text-cyan-300 uppercase tracking-wide">OS Command</span>
                                </div>
                            )}
                            {message.type === 'osquery' && (
                                <div className="flex items-center gap-2 mb-2 pb-2 border-b border-white/20">
                                    <Shield className="w-4 h-4 text-green-300 flex-shrink-0" />
                                    <span className="text-xs font-semibold text-green-300 uppercase tracking-wide">Security Query</span>
                                </div>
                            )}
                            {isDashboard && (
                                <div className="flex items-center gap-2 mb-2 pb-2 border-b border-white/20">
                                    <Shield className="w-4 h-4 text-purple-300 flex-shrink-0" />
                                    <span className="text-xs font-semibold text-purple-300 uppercase tracking-wide">Security Dashboard</span>
                                </div>
                            )}
                            <pre className={`whitespace-pre-wrap font-sans break-words ${isDashboard ? 'text-xs' : 'text-sm'
                                } leading-relaxed text-white`}>
                                {message.content}
                            </pre>
                        </div>
                        {!isUser && (
                            <button
                                onClick={() => copyToClipboard(message.content, index)}
                                className="flex-shrink-0 p-2 rounded-lg transition-all duration-200 hover:bg-white/20 hover:scale-110"
                            >
                                {copiedId === index ? (
                                    <Check className="w-4 h-4 text-green-300" />
                                ) : (
                                    <Copy className="w-4 h-4 text-white/70" />
                                )}
                            </button>
                        )}
                    </div>
                    {mounted && (
                        <div className="text-xs mt-2 text-white/60">
                            {formatTime(message.timestamp)}
                        </div>
                    )}
                </div>
            </div>
        );
    };

    if (!mounted) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-center">
                    <Loader2 className="w-8 h-8 animate-spin mx-auto text-purple-500 mb-4" />
                    <p className="text-white/70">Loading LiaAI...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="flex h-screen overflow-hidden relative">
            {/* Sidebar */}
            <div className={`${sidebarOpen ? 'w-72' : 'w-0'
                } glass-strong border-r border-white/10 transition-all duration-300 flex-shrink-0 flex flex-col overflow-hidden relative z-10`}
            >
                <div className="p-6 border-b border-white/10 flex-shrink-0">
                    <div className="flex items-center gap-3">
                        <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg">
                            <Shield className="w-6 h-6 text-white" />
                        </div>
                        <div className="min-w-0">
                            <h1 className="font-bold text-xl text-gradient-purple truncate">LiaAI</h1>
                            <p className="text-xs text-white/60 truncate">Cyber Assistant v0.3.0</p>
                        </div>
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto p-4">
                    <div className="mb-6">
                        <h3 className="text-xs font-semibold text-white/50 uppercase mb-3 tracking-wider">Quick Actions</h3>
                        <div className="space-y-2">
                            {quickActions.map((action, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => setInput(action.query)}
                                    className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-white/5 hover:bg-white/10 transition-all duration-200 hover:scale-105"
                                >
                                    <action.icon className="w-4 h-4 text-white/70 flex-shrink-0" />
                                    <span className="text-sm text-white/80 font-medium">{action.label}</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="mb-6">
                        <h3 className="text-xs font-semibold text-white/50 uppercase mb-3 tracking-wider">Filter Messages</h3>
                        <div className="space-y-2">
                            {[
                                { id: 'all', label: 'All Messages', icon: MessageSquare },
                                { id: 'chat', label: 'Chat', icon: MessageSquare },
                                { id: 'os_command', label: 'OS Commands', icon: Terminal },
                                { id: 'osquery', label: 'Security Queries', icon: Shield },
                            ].map(tab => (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 hover:scale-105 ${activeTab === tab.id
                                        ? 'bg-purple-500/20 text-white border border-purple-500/30'
                                        : 'hover:bg-white/5 text-white/60'
                                        }`}
                                >
                                    <tab.icon className="w-4 h-4 flex-shrink-0" />
                                    <span className="text-sm font-medium">{tab.label}</span>
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="p-4 border-t border-white/10 space-y-2 flex-shrink-0">
                    <button
                        onClick={exportChat}
                        className="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/10 transition-all duration-200 hover:scale-105"
                    >
                        <Download className="w-4 h-4 text-blue-400 flex-shrink-0" />
                        <span className="text-sm text-white/70 font-medium">Export Chat</span>
                    </button>
                    <button
                        onClick={clearChat}
                        className="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-red-500/20 transition-all duration-200 hover:scale-105"
                    >
                        <Trash2 className="w-4 h-4 text-red-400 flex-shrink-0" />
                        <span className="text-sm text-red-400 font-medium">Clear Chat</span>
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 flex flex-col min-w-0 relative z-0">
                {/* Header */}
                <div className="glass-strong border-b border-white/10 px-6 py-4 flex items-center justify-between flex-shrink-0 backdrop-blur-xl">
                    <div className="flex items-center gap-4 min-w-0">
                        <button
                            onClick={() => setSidebarOpen(!sidebarOpen)}
                            className="p-3 hover:bg-white/10 rounded-xl transition-all duration-200 hover:scale-110 flex-shrink-0"
                        >
                            {sidebarOpen ? <X className="w-5 h-5 text-white/70" /> : <Menu className="w-5 h-5 text-white/70" />}
                        </button>
                        <div className="min-w-0">
                            <h2 className="font-semibold text-white truncate">Chat Interface</h2>
                            <p className="text-sm text-white/60 truncate">
                                {filteredMessages.length} messages
                            </p>
                        </div>
                    </div>
                    <button className="p-3 hover:bg-white/10 rounded-xl transition-all duration-200 hover:scale-110 flex-shrink-0">
                        <Settings className="w-5 h-5 text-white/70" />
                    </button>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto px-6 py-6">
                    <div className="max-w-4xl mx-auto">
                        {filteredMessages.map((message, index) => (
                            <MessageBubble key={index} message={message} index={index} />
                        ))}
                        {isLoading && (
                            <div className="flex items-center gap-3 glass px-5 py-4 rounded-2xl mb-4 w-fit">
                                <div className="typing-indicator">
                                    <span className="bg-purple-400"></span>
                                    <span className="bg-blue-400"></span>
                                    <span className="bg-cyan-400"></span>
                                </div>
                                <span className="text-sm text-white/80 ml-2">Lia is thinking...</span>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>
                </div>

                {/* Input Area */}
                <div className="glass-strong border-t border-white/10 px-6 py-5 flex-shrink-0 backdrop-blur-xl">
                    <div className="max-w-4xl mx-auto">
                        <div className="bg-blue-500/10 border border-blue-500/20 px-4 py-3 rounded-xl mb-4 flex items-start gap-2">
                            <AlertCircle className="h-4 w-4 text-blue-400 flex-shrink-0 mt-0.5" />
                            <p className="text-sm text-white/70">
                                <strong className="text-blue-300">Examples:</strong> "show running processes", "list files", "security dashboard"
                            </p>
                        </div>

                        <div className="flex gap-3">
                            <input
                                ref={inputRef}
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={handleKeyPress}
                                placeholder="Ask LiaAI anything..."
                                className="flex-1 px-5 py-4 glass border border-white/20 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-white placeholder-white/50 text-sm"
                                disabled={isLoading}
                            />
                            <button
                                onClick={handleSubmit}
                                disabled={!input.trim() || isLoading}
                                className="px-8 py-4 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-xl hover:from-purple-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-2 font-medium shadow-lg hover:shadow-xl hover:scale-105 active:scale-100 flex-shrink-0"
                            >
                                {isLoading ? (
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                ) : (
                                    <Send className="w-5 h-5" />
                                )}
                                <span className="hidden sm:inline">Send</span>
                            </button>
                        </div>

                        <div className="flex items-center gap-4 mt-4 text-xs text-white/50">
                            <div className="flex items-center gap-2">
                                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                                <span>System Ready</span>
                            </div>
                            <span>•</span>
                            <span>Press Enter to send</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ChatInterface;