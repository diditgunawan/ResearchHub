import React from 'react';
import { ShieldCheck, AlertTriangle, XCircle, Clock } from 'lucide-react';

export type VerificationState = 'verified' | 'needs_review' | 'refused' | 'pending';

interface StatusBadgeProps {
  state: VerificationState;
  label?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ state, label }) => {
  switch (state) {
    case 'verified':
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#E4F3EA] text-[#14532D] border border-[#B7DEC5]">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>{label || 'Grounded (Verified 100%)'}</span>
        </span>
      );
    case 'needs_review':
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#FDF0DC] text-[#7A3E00] border border-[#EBCB98]">
          <AlertTriangle className="w-3.5 h-3.5" />
          <span>{label || 'Needs Review'}</span>
        </span>
      );
    case 'refused':
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#FBE4E4] text-[#8A1C1C] border border-[#EBB5B5]">
          <XCircle className="w-3.5 h-3.5" />
          <span>{label || 'Refused (Insufficient Evidence)'}</span>
        </span>
      );
    case 'pending':
    default:
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#F6F8F9] text-[#4A5B68] border border-[#D7DEE3]">
          <Clock className="w-3.5 h-3.5" />
          <span>{label || 'Verifying...'}</span>
        </span>
      );
  }
};
