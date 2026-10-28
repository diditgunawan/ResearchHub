import React, { useState, useEffect } from 'react';
import { api, User } from '../api/client';
import { Mail, ArrowRight, ShieldCheck, KeyRound, UserCheck } from 'lucide-react';

interface LoginPageProps {
  onLoginSuccess: (user: User) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('didit.gunawan@uajy.ac.id');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [manualToken, setManualToken] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleVerifyToken = async (tokenToVerify: string) => {
    if (!tokenToVerify.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const res = await api.verifySession(tokenToVerify.trim());
      onLoginSuccess(res.user);
    } catch (err: any) {
      setError(err.detail || 'Invalid, expired, or already-used token. Please request a fresh link.');
    } finally {
      setLoading(false);
    }
  };

  // Auto-verify if ?token= query parameter is present in URL
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const urlToken = params.get('token');
    if (urlToken) {
      handleVerifyToken(urlToken);
    }
  }, []);

  const handleRequestMagicLink = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      const res = await api.requestMagicLink(email);
      setMessage(res.message);
      if (res.token) {
        setManualToken(res.token);
      }
    } catch (err: any) {
      setError(err.detail || 'Failed to request magic link');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-sm border border-[#D7DEE3] p-8">
        <div className="text-center mb-6">
          <div className="inline-flex w-12 h-12 rounded-xl bg-[#0B5C7A] items-center justify-center text-white font-bold text-xl mb-3">
            RF
          </div>
          <h1 className="font-serif text-2xl font-bold text-[#12202B]">ResearchHub</h1>
          <p className="text-sm text-[#4A5B68] mt-1">
            Grounded, Zero-Hallucination Academic Research Workspace
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-[#FBE4E4] text-[#8A1C1C] border border-[#EBB5B5] text-sm">
            {error}
          </div>
        )}

        {message && (
          <div className="mb-4 p-3 rounded-lg bg-[#E4F3EA] text-[#14532D] border border-[#B7DEC5] text-sm">
            {message}
          </div>
        )}

        {/* Quick Administrator Account Selection */}
        <div className="mb-5 bg-[#F6F8FA] p-3 rounded-lg border border-[#E1E4E8]">
          <div className="flex items-center space-x-1.5 text-xs font-semibold text-[#0B4A63] mb-2">
            <UserCheck className="w-3.5 h-3.5 text-[#0B5C7A]" />
            <span>Select System Administrator Account</span>
          </div>
          <div className="flex flex-col gap-1.5">
            <button
              type="button"
              onClick={() => setEmail('didit.gunawan@uajy.ac.id')}
              className={`text-left text-xs px-2.5 py-1.5 rounded border transition-colors ${
                email === 'didit.gunawan@uajy.ac.id'
                  ? 'bg-white border-[#0B5C7A] text-[#0B5C7A] font-semibold shadow-xs'
                  : 'bg-transparent border-transparent hover:bg-white text-[#4A5B68]'
              }`}
            >
              didit.gunawan@uajy.ac.id (System Administrator)
            </button>
            <button
              type="button"
              onClick={() => setEmail('lead.researcher@medical.ox.ac.uk')}
              className={`text-left text-xs px-2.5 py-1.5 rounded border transition-colors ${
                email === 'lead.researcher@medical.ox.ac.uk'
                  ? 'bg-white border-[#0B5C7A] text-[#0B5C7A] font-semibold shadow-xs'
                  : 'bg-transparent border-transparent hover:bg-white text-[#4A5B68]'
              }`}
            >
              lead.researcher@medical.ox.ac.uk (System Administrator)
            </button>
          </div>
        </div>

        <form onSubmit={handleRequestMagicLink} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-[#34495A] uppercase tracking-wider mb-1">
              Administrator Email
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 absolute left-3 top-3 text-[#4A5B68]" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@university.edu"
                className="w-full pl-9 pr-3 py-2 bg-white border border-[#D7DEE3] rounded-lg text-sm text-[#12202B] focus:outline-none focus:ring-2 focus:ring-[#0B5C7A]"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center space-x-2 py-2.5 px-4 bg-[#0B5C7A] hover:bg-[#0B4A63] text-white rounded-lg text-sm font-semibold transition-colors disabled:opacity-50"
          >
            <span>{loading ? 'Generating link...' : 'Generate Magic Sign-In Link'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Manual Token Redemption Box (P1/P9 compliant) */}
        <div className="mt-6 pt-5 border-t border-[#D7DEE3]">
          <div className="flex items-center space-x-1.5 text-xs font-semibold text-[#12202B] mb-2">
            <KeyRound className="w-3.5 h-3.5 text-[#0B5C7A]" />
            <span>Enter Single-Use Token</span>
          </div>
          <p className="text-xs text-[#4A5B68] mb-2.5">
            In local development, your login token is logged to your terminal console:
          </p>
          <div className="flex gap-2">
            <input
              type="text"
              value={manualToken}
              onChange={(e) => setManualToken(e.target.value)}
              placeholder="Paste token from server log..."
              className="flex-1 px-3 py-1.5 bg-white border border-[#D7DEE3] rounded-lg text-xs font-mono text-[#12202B] focus:outline-none focus:ring-2 focus:ring-[#0B5C7A]"
            />
            <button
              type="button"
              onClick={() => handleVerifyToken(manualToken)}
              disabled={loading || !manualToken.trim()}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-[#0B5C7A] hover:bg-[#0B4A63] text-white rounded-lg text-xs font-semibold disabled:opacity-50 transition-colors"
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Sign In</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
