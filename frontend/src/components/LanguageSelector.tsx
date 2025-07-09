import { useState, useRef, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Globe, Volume2, X } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface Language {
  code: string;
  name: string;
  nativeName: string;
  flag: string;
  audio?: string;
}

const languages: Language[] = [
  { code: 'en', name: 'English', nativeName: 'English', flag: 'A' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिंदी', flag: 'हि' },
  { code: 'pa', name: 'Punjabi', nativeName: 'ਪੰਜਾਬੀ', flag: 'ਪੰ' },
  { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી', flag: 'ગુ' },
  { code: 'bn', name: 'Bengali', nativeName: 'বাংলা', flag: 'বা' },
  { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்', flag: 'த' },
  { code: 'te', name: 'Telugu', nativeName: 'తెలుగు', flag: 'తె' },
  { code: 'mr', name: 'Marathi', nativeName: 'मराठी', flag: 'म' },
  { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ', flag: 'ಕ' },
  { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം', flag: 'മ' },
  { code: 'or', name: 'Odia', nativeName: 'ଓଡ଼ିଆ', flag: 'ଓ' },
  { code: 'as', name: 'Assamese', nativeName: 'অসমীয়া', flag: 'অ' },
  { code: 'ur', name: 'Urdu', nativeName: 'اردو', flag: 'ا' },
  { code: 'sd', name: 'Sindhi', nativeName: 'سنڌي', flag: 'س' },
  { code: 'ne', name: 'Nepali', nativeName: 'नेपाली', flag: 'ने' },
  { code: 'sa', name: 'Sanskrit', nativeName: 'संस्कृतम्', flag: 'सं' },
  { code: 'ks', name: 'Kashmiri', nativeName: 'कॉशुर', flag: 'कॉ' },
  { code: 'mni', name: 'Manipuri', nativeName: 'মৈতৈলোন্', flag: 'ম' }
];

interface LanguageSelectorProps {
  userRole?: 'ministry' | 'farmer';
}

export default function LanguageSelector({ userRole = 'farmer' }: LanguageSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState(languages[0]);
  const [isAnimating, setIsAnimating] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);
  const { toast } = useToast();

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest('[data-language-selector]')) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  const handleToggle = () => {
    setIsAnimating(true);
    setIsOpen(!isOpen);
    setTimeout(() => setIsAnimating(false), 300);
  };

  const handleLanguageSelect = (language: Language) => {
    setSelectedLanguage(language);
    setIsOpen(false);
    
    // Announce language selection
    const announcement = `${language.nativeName} selected`;
    toast({
      title: "भाषा बदली गई / Language Changed",
      description: `${language.nativeName} ${language.name} selected`,
    });

    // Simulate text-to-speech announcement
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(announcement);
      utterance.lang = language.code;
      speechSynthesis.speak(utterance);
    }
  };

  const playLanguageAudio = (language: Language, event: React.MouseEvent) => {
    event.stopPropagation();
    
    // Simulate pronunciation using speech synthesis
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(language.nativeName);
      utterance.lang = language.code;
      utterance.rate = 0.8; // Slower for better comprehension
      speechSynthesis.speak(utterance);
    }
    
    toast({
      title: "🔊 भाषा सुनें / Listen to Language",
      description: `Playing ${language.nativeName}`,
    });
  };

  // Only show for farmers by default, or if explicitly enabled
  if (userRole === 'ministry') {
    return null;
  }

  return (
    <div 
      className="fixed bottom-6 right-6 z-50"
      data-language-selector
      role="region"
      aria-label="Language Selector"
    >
      {/* Language Selection Menu */}
      {isOpen && (
        <Card className={`
          absolute bottom-16 right-0 w-80 max-h-96 overflow-y-auto
          bg-card/95 backdrop-blur-sm border border-primary/20 shadow-strong
          transform transition-all duration-300 ease-out origin-bottom-right
          ${isAnimating ? 'animate-scale-in' : ''}
        `}>
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
                <Globe className="h-5 w-5 text-primary" />
                भाषा चुनें / Choose Language
              </h3>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsOpen(false)}
                aria-label="Close language menu"
                className="h-8 w-8"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            
            <div className="space-y-2">
              {languages.map((language) => (
                <div
                  key={language.code}
                  className={`
                    flex items-center p-3 rounded-lg cursor-pointer transition-all duration-200
                    hover:bg-primary/10 hover:scale-[1.02] group
                    ${selectedLanguage.code === language.code 
                      ? 'bg-primary/20 border border-primary/30' 
                      : 'bg-muted/50 border border-transparent'
                    }
                  `}
                  onClick={() => handleLanguageSelect(language)}
                  role="button"
                  tabIndex={0}
                  aria-label={`Select ${language.name} language`}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      handleLanguageSelect(language);
                    }
                  }}
                >
                  {/* Flag/Icon */}
                  <div className="text-2xl mr-3 flex-shrink-0">
                    {language.flag}
                  </div>
                  
                  {/* Language Names */}
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-foreground text-base">
                      {language.nativeName}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {language.name}
                    </div>
                  </div>
                  
                  {/* Audio Button */}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-10 w-10 flex-shrink-0 opacity-70 group-hover:opacity-100"
                    onClick={(e) => playLanguageAudio(language, e)}
                    aria-label={`Listen to ${language.name} pronunciation`}
                  >
                    <Volume2 className="h-4 w-4" />
                  </Button>
                  
                  {/* Active Indicator */}
                  {selectedLanguage.code === language.code && (
                    <div className="w-2 h-2 bg-primary rounded-full ml-2 animate-pulse" />
                  )}
                </div>
              ))}
            </div>
            
            {/* Help Text */}
            <div className="mt-4 p-3 bg-success/10 rounded-lg border border-success/20">
              <p className="text-xs text-success-foreground text-center">
                🎤 Voice support • 🔊 Audio guidance • 👆 Large buttons
              </p>
              <p className="text-xs text-muted-foreground text-center mt-1">
                Tap speaker icons to hear language names
              </p>
            </div>
          </div>
        </Card>
      )}
      
      {/* Main Floating Button */}
      <Button
        className={`
          h-14 w-14 rounded-full shadow-strong hover:shadow-medium
          bg-primary hover:bg-primary/90 text-primary-foreground
          transition-all duration-300 ease-out
          ${isOpen ? 'scale-110 bg-primary/90' : 'hover:scale-105'}
        `}
        onClick={handleToggle}
        aria-label="Open language selector menu"
        aria-expanded={isOpen}
        aria-haspopup="menu"
      >
        <div className="relative">
          <Globe className={`h-6 w-6 transition-transform duration-300 ${
            isOpen ? 'rotate-180' : ''
          }`} />
          
          {/* Active Language Indicator */}
          <Badge 
            className="absolute -top-2 -right-2 h-6 w-6 p-0 text-xs bg-accent hover:bg-accent"
            aria-label={`Current language: ${selectedLanguage.name}`}
          >
            {selectedLanguage.flag}
          </Badge>
        </div>
      </Button>
      
      {/* Accessibility Announcement */}
      <div 
        className="sr-only" 
        aria-live="polite" 
        aria-atomic="true"
      >
        {isOpen ? 'Language menu opened' : 'Language menu closed'}
      </div>
    </div>
  );
}