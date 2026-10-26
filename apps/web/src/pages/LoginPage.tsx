import React, { useState } from 'react';
import { api, User } from '../api/client';
import { Mail, ArrowRight, ShieldCheck, Sparkles } from 'lucide-react';

interface LoginPageProps {
  onLoginSuccess: (user: User) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('lead.researcher@medical.ox.ac.uk');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [devToken, setDevToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRequestMagicLink = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      const res = await api.requestMagicLink(email);
      setMessage(res.message);
      if (res.token) {
        setDevToken(res.token);
      }
    } catch (err: any) {
      setError(err.detail || 'Failed to request magic link');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyDevToken = async () => {
    if (!devToken) return;
    setLoading(true);
    setError(null);

    try {
      const res = await api.verifySession(devToken);
      onLoginSuccess(res.user);
    } catch (err: any) {
      setError(err.detail || 'Failed to verify session token');
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
          <h1 className="font-serif text-2xl font-bold text-[#12202B]">ResearchForge</h1>
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

        <form onSubmit={handleRequestMagicLink} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-[#34495A] uppercase tracking-wider mb-1">
              Academic Email
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
            <span>{loading ? 'Sending link...' : 'Send Magic Sign-In Link'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {devToken && (
          <div className="mt-6 pt-6 border-t border-[#D7DEE3]">
            <div className="flex items-center space-x-1.5 text-xs font-semibold text-[#0B4A63] mb-2">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Local Dev Sandbox Bypass Detected</span>
            </div>
            <p className="text-xs text-[#4A5B68] mb-3">
              Magic link token issued automatically for local testing. Click below to sign in immediately:
            </p>
            <button
              onClick={handleVerifyDevToken}
              disabled={loading}
              className="w-full flex items-center justify-center space-x-1.5 py-2 px-3 bg-[#E3F0F5] hover:bg-[#d0e5ed] text-[#0B4A63] rounded-lg text-xs font-bold border border-[#B5D5E2] transition-colors"
            >
              <ShieldCheck className="w-4 h-4 text-[#0B5C7A]" />
              <span>Instant Local Sign-In as {email}</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
