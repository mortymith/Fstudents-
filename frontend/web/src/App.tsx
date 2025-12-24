
import React, { useState } from 'react';
import Login from './pages/Login';
import ForgotPassword from './pages/ForgotPassword';
import SetNewPassword from './pages/SetNewPassword';

enum Screen {
  LOGIN = 'LOGIN',
  FORGOT_PASSWORD = 'FORGOT_PASSWORD',
  SET_PASSWORD = 'SET_PASSWORD'
}

const App: React.FC = () => {
  const [currentScreen, setCurrentScreen] = useState<Screen>(Screen.LOGIN);

  const navigateTo = (screen: Screen) => {
    setCurrentScreen(screen);
  };

  const renderScreen = () => {
    switch (currentScreen) {
      case Screen.LOGIN:
        return (
          <Login 
            onForgotPassword={() => navigateTo(Screen.FORGOT_PASSWORD)} 
            onLogin={() => alert('Logged in (mock)')} 
          />
        );
      case Screen.FORGOT_PASSWORD:
        return (
          <ForgotPassword 
            onBackToLogin={() => navigateTo(Screen.LOGIN)} 
            onSendLink={() => navigateTo(Screen.SET_PASSWORD)} 
          />
        );
      case Screen.SET_PASSWORD:
        return (
          <SetNewPassword 
            onBackToLogin={() => navigateTo(Screen.LOGIN)} 
            onResetSuccess={() => {
              alert('Password reset successful!');
              navigateTo(Screen.LOGIN);
            }} 
          />
        );
      default:
        return <Login onForgotPassword={() => navigateTo(Screen.FORGOT_PASSWORD)} onLogin={() => {}} />;
    }
  };

  return (
    <div className="relative min-h-screen w-full flex flex-col items-center justify-center p-4 selection:bg-primary selection:text-button-text-dark">
      {renderScreen()}
      
      {/* Subtle Background Decorations */}
      <div className="fixed inset-0 pointer-events-none -z-10 overflow-hidden">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-primary/5 rounded-full blur-[120px] opacity-20 transform -translate-y-1/2"></div>
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-primary/5 rounded-full blur-[120px] opacity-20 transform translate-y-1/2"></div>
      </div>
    </div>
  );
};

export default App;
