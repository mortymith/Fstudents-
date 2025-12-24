
import React from 'react';
import Input from '../components/Input';
import Button from '../components/Button';

interface SetNewPasswordProps {
  onBackToLogin: () => void;
  onResetSuccess: () => void;
}

const SetNewPassword: React.FC<SetNewPasswordProps> = ({ onBackToLogin, onResetSuccess }) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onResetSuccess();
  };

  return (
    <div className="w-full max-w-md flex flex-col items-center gap-8 animate-fade-in">
      {/* Brand Header */}
      <div className="flex flex-col items-center gap-4 text-center">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/20 shadow-[0_0_20px_rgba(56,224,123,0.15)] ring-1 ring-primary/30">
          <span className="material-symbols-outlined text-4xl text-primary">inventory_2</span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-white px-4">Inventory System</h1>
      </div>

      {/* Main Content Card */}
      <div className="flex w-full flex-col gap-8 rounded-[2rem] bg-card-dark/40 backdrop-blur-md p-8 shadow-2xl border border-border-dark/30">
        <div className="text-center">
          <h1 className="text-3xl font-bold tracking-tight text-white">Set a New Password</h1>
          <p className="mt-2 text-[#9eb7a8]">Your new password must be different from previous passwords.</p>
        </div>

        <form className="flex w-full flex-col gap-6" onSubmit={handleSubmit}>
          <Input
            label="New Password"
            id="new-password"
            type="password"
            placeholder="Enter your new password"
            showPasswordToggle
            helpText="Must contain at least 8 characters, one uppercase letter, and one number."
            required
          />

          <Input
            label="Confirm New Password"
            id="confirm-password"
            type="password"
            placeholder="Confirm your new password"
            showPasswordToggle
            required
          />

          <Button type="submit">Reset Password</Button>
        </form>
      </div>

      <button
        type="button"
        onClick={onBackToLogin}
        className="text-base font-medium text-[#9eb7a8] hover:text-primary transition-colors flex items-center gap-2"
      >
        Back to Login
      </button>
    </div>
  );
};

export default SetNewPassword;
