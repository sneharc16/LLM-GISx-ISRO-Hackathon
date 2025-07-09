import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import AuthTabs from "@/components/AuthTabs";
import LanguageSelector from "@/components/LanguageSelector";
import { useAuth } from "@/context/AuthContext"
import heroImage from "@/assets/hero-bg.jpg";

const Index = () => {
  const { user, login } = useAuth();
  const navigate = useNavigate();

  const handleAuthSuccess = (userType: 'ministry' | 'farmer', userData: any) => {
    login(userType, userData);
  };

  useEffect(() => {
    if (user) {
      navigate("/dashboard");
    }
  }, [user, navigate]);

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <div className="relative min-h-screen flex flex-col">
        {/* Background Image */}
        <div 
          className="absolute inset-0 z-0"
          style={{
            backgroundImage: `url(${heroImage})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            backgroundRepeat: 'no-repeat'
          }}
        >
          <div className="absolute inset-0 bg-gradient-to-r from-primary/90 to-primary/70"></div>
        </div>

        {/* Content */}
        <div className="relative z-10 flex-1 flex flex-col">
          {/* Header */}
          <header className="p-6">
            <div className="container mx-auto">
              <h1 className="text-2xl font-bold text-primary-foreground">
                LLM-GISX Ministry Portal
              </h1>
              <p className="text-primary-foreground/80 mt-1">
                Digital Agriculture • Data Insights • Smart Farming
              </p>
            </div>
          </header>

          {/* Main Content */}
          <div className="flex-1 flex items-center justify-center p-6">
            <div className="container mx-auto">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                {/* Left Column - Welcome Text */}
                <div className="text-center lg:text-left">
                  <h2 className="text-4xl lg:text-6xl font-bold text-primary-foreground mb-6">
                    Empowering Agriculture Through Technology
                  </h2>
                  <p className="text-xl text-primary-foreground/90 mb-8 leading-relaxed">
                    Connect with our intelligent agricultural assistant to get 
                    real-time insights, crop recommendations, and data-driven 
                    solutions for sustainable farming.
                  </p>
                  
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
                    <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                      <h3 className="font-semibold text-primary-foreground mb-2">
                        For Ministries
                      </h3>
                      <p className="text-sm text-primary-foreground/80">
                        Comprehensive reports, cost analysis, and administrative tools
                      </p>
                    </div>
                    <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                      <h3 className="font-semibold text-primary-foreground mb-2">
                        For Farmers
                      </h3>
                      <p className="text-sm text-primary-foreground/80">
                        Voice support, crop guidance, and multilingual assistance
                      </p>
                    </div>
                  </div>
                </div>

                {/* Right Column - Auth Form */}
                <div className="flex justify-center lg:justify-end">
                  <div className="w-full max-w-md bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl p-8">
                    <div className="text-center mb-8">
                      <h3 className="text-2xl font-bold text-foreground mb-2">
                        Access Portal
                      </h3>
                      <p className="text-muted-foreground">
                        Choose your user type to continue
                      </p>
                    </div>
                    
                    <AuthTabs onAuthSuccess={handleAuthSuccess} />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <footer className="p-6 border-t border-white/20">
            <div className="container mx-auto text-center">
              <p className="text-primary-foreground/70 text-sm">
                © 2025 Agricultural Ministry Portal. Powered by Digital India Initiative.
              </p>
            </div>
          </footer>
        </div>
      </div>
      
      {/* Language Selector - Available on login page for accessibility */}
      <LanguageSelector />
    </div>
  );
};

export default Index;