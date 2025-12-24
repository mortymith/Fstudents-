
import React from 'react';
import Input from '../components/Input';
import Button from '../components/Button';

interface LoginProps {
  onForgotPassword: () => void;
  onLogin: () => void;
}

const Login: React.FC<LoginProps> = ({ onForgotPassword, onLogin }) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onLogin();
  };

  return (
    <div className="w-full max-w-sm flex flex-col gap-8 animate-fade-in">
      {/* Brand Header */}
      <div className="flex flex-col items-center gap-4 text-center">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/20 shadow-[0_0_20px_rgba(56,224,123,0.15)] ring-1 ring-primary/30">
          <span className="material-symbols-outlined text-4xl text-primary">inventory_2</span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-white px-4">Inventory System</h1>
      </div>

      {/* Login Card */}
      <div className="w-full rounded-[1.5rem] sm:rounded-[2rem] bg-card-dark p-8 shadow-2xl ring-1 ring-border-dark/50">
        <form className="flex flex-col gap-6" onSubmit={handleSubmit}>
          <Input 
            label="Email" 
            id="email" 
            type="email" 
            placeholder="user@acme.corp" 
            icon="mail" 
            required 
          />
          <Input 
            label="Password" 
            id="password" 
            type="password" 
            placeholder="Password" 
            icon="lock" 
            showPasswordToggle
            required 
          />
          
          <div className="flex flex-col gap-4 pt-2">
            <Button type="submit">Log In</Button>
            <button 
              type="button"
              onClick={onForgotPassword}
              className="text-center text-sm text-text-dark underline-offset-4 hover:text-primary hover:underline transition-all"
            >
              Forgot Password?
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;
