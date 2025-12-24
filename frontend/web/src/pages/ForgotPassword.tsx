
import React from 'react';
import Input from '../components/Input';
import Button from '../components/Button';

interface ForgotPasswordProps {
  onBackToLogin: () => void;
  onSendLink: () => void;
}

const ForgotPassword: React.FC<ForgotPasswordProps> = ({ onBackToLogin, onSendLink }) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSendLink();
  };

  return (
    <div className="w-full max-w-[440px] flex flex-col gap-8 animate-fade-in">
      {/* Brand Logo */}
      <div className="flex justify-center">
        <div className="flex flex-col items-center gap-3 group">
          <div className="size-14 rounded-2xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center border border-primary/10 shadow-[0_0_15px_rgba(56,224,123,0.1)] transition-transform group-hover:scale-105">
            <span className="material-symbols-outlined text-4xl text-primary">inventory_2</span>
          </div>
          <span className="text-xl font-bold tracking-tight text-white/90">Inventory System</span>
        </div>
      </div>

      {/* Card */}
      <div className="bg-card-dark rounded-[2rem] p-6 sm:p-10 shadow-xl border border-[#264532]">
        <div className="flex flex-col gap-3 mb-8 text-center">
          <h1 className="text-3xl font-black leading-tight tracking-[-0.02em] text-white">Forgot Password</h1>
          <p className="text-[#96c5a9] text-base font-normal leading-relaxed">
            Enter your email address to receive a password reset link.
          </p>
        </div>

        <form className="flex flex-col gap-6" onSubmit={handleSubmit}>
          <Input 
            label="Email Address" 
            id="email" 
            type="email" 
            placeholder="name@company.com" 
            icon="mail" 
            required 
          />
          
          <Button type="submit">Send Reset Link</Button>

          <div className="flex justify-center pt-2">
            <button 
              type="button"
              onClick={onBackToLogin}
              className="group flex items-center gap-2 text-sm font-bold text-[#96c5a9] hover:text-primary transition-colors"
            >
              <span className="material-symbols-outlined text-lg group-hover:-translate-x-1 transition-transform">arrow_back</span>
              Back to Login
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ForgotPassword;
