
import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
}

const Button: React.FC<ButtonProps> = ({ children, ...props }) => {
  return (
    <button
      {...props}
      className="group flex w-full cursor-pointer items-center justify-center overflow-hidden rounded-full h-12 px-5 bg-primary hover:bg-[#2fd16f] active:scale-[0.98] transition-all duration-200 text-button-text-dark text-base font-bold leading-normal tracking-wide shadow-[0_4px_14px_0_rgba(56,224,123,0.39)] hover:shadow-[0_6px_20px_rgba(56,224,123,0.23)] disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <span className="truncate">{children}</span>
    </button>
  );
};

export default Button;
