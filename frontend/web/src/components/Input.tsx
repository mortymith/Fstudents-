
import React, { useState } from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  icon?: string;
  showPasswordToggle?: boolean;
  helpText?: string;
}

const Input: React.FC<InputProps> = ({ label, icon, showPasswordToggle, helpText, ...props }) => {
  const [isVisible, setIsVisible] = useState(false);
  const inputType = showPasswordToggle ? (isVisible ? 'text' : 'password') : props.type;

  return (
    <div className="flex flex-col gap-2 w-full">
      <label className="text-sm font-medium text-text-light ml-1" htmlFor={props.id}>
        {label}
      </label>
      <div className="relative group/input flex items-center">
        {icon && (
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <span className="material-symbols-outlined text-text-dark group-focus-within/input:text-primary transition-colors">
              {icon}
            </span>
          </div>
        )}
        <input
          {...props}
          type={inputType}
          className={`form-input flex w-full min-w-0 flex-1 rounded-full border border-border-dark bg-[#1c2620] h-12 sm:h-14 px-4 text-text-light placeholder:text-text-dark focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary transition-all duration-200 ${icon ? 'pl-11' : ''} ${showPasswordToggle ? 'pr-12' : ''}`}
        />
        {showPasswordToggle && (
          <button
            type="button"
            onClick={() => setIsVisible(!isVisible)}
            className="absolute inset-y-0 right-0 px-4 flex items-center text-text-dark hover:text-text-light transition-colors"
          >
            <span className="material-symbols-outlined">
              {isVisible ? 'visibility_off' : 'visibility'}
            </span>
          </button>
        )}
      </div>
      {helpText && (
        <p className="px-4 text-xs sm:text-sm text-text-dark leading-snug mt-1">
          {helpText}
        </p>
      )}
    </div>
  );
};

export default Input;
