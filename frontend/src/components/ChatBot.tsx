// frontend/src/components/ChatBot.tsx

import { useState, useRef, useEffect } from "react";
import MapView from "./MapView";
import { submitQuery, getSummary } from "../api";
import {
  Card, CardContent, CardDescription, CardHeader, CardTitle
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { MessageSquare, Send, Bot, User, Map, Download, Mic, MicOff } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  hasMapOption?: boolean;
}

interface ChatBotProps {
  userRole: 'ministry' | 'farmer';
}

type Stage = 'idle' | 'awaitingBox' | 'processing';

export default function ChatBot({ userRole }: ChatBotProps) {
  const [messages, setMessages] = useState<Message[]>([{
    id: '1',
    type: 'bot',
    content: `Welcome to the Agricultural Assistant! I'm here to help you with crop analysis, weather information, and agricultural insights. ${userRole === 'ministry' ? 'As a ministry user, you can generate detailed reports and access comprehensive data.' : 'As a farmer, you have access to voice support in multiple languages.'}`,
    timestamp: new Date(),
  }]);

  const [inputValue, setInputValue] = useState("");
  const [stage, setStage] = useState<Stage>('idle');
  const [pendingQuery, setPendingQuery] = useState<string>("");
  const [taskId, setTaskId] = useState<string | null>(null);

  const [isListening, setIsListening] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  // Auto-scroll
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  // 1) User presses “Send”
  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    // Append the user message
    const userMsg: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    };
    setMessages(ms => [...ms, userMsg]);

    // Save query, clear input, switch to map mode
    setPendingQuery(inputValue);
    setInputValue("");
    setStage('awaitingBox');
  };

  // 2) MapView calls this when bounding box is done
  const onBoxComplete = async (coords: { lat: number; lng: number }[]) => {
    // Compute [minx, miny, maxx, maxy]
    const lats = coords.map(c => c.lat);
    const lngs = coords.map(c => c.lng);
    const bbox = [
      Math.min(...lngs),
      Math.min(...lats),
      Math.max(...lngs),
      Math.max(...lats),
    ];

    setStage('processing');
    try {
      const id = await submitQuery(pendingQuery, bbox);
      setTaskId(id);

      // Poll for summary
      let summaryData: { summary?: string } = {};
      do {
        await new Promise(r => setTimeout(r, 2000));
        summaryData = await getSummary(id);
      } while (!summaryData.summary);

      // Append bot’s summary
      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: summaryData.summary!,
        timestamp: new Date(),
      };
      setMessages(ms => [...ms, botMsg]);
    } catch (err: any) {
      toast({
        title: "Error",
        description: err.message || "Something went wrong",
        variant: "destructive"
      });
    } finally {
      setStage('idle');
    }
  };

  // Voice support (farmers only)
  const handleVoiceToggle = () => {
    if (userRole !== 'farmer') {
      toast({
        title: "Voice Support",
        description: "Voice support is available for farmer accounts only",
        variant: "destructive",
      });
      return;
    }

    setIsListening(l => !l);
    toast({
      title: isListening ? "Voice Recording Stopped" : "Voice Recording Started",
      description: isListening ? "Processing your voice input..." : "Speak your query in any language",
    });

    if (!isListening) {
      // Simulate recognition
      setTimeout(() => {
        setInputValue("What are the best crops for monsoon season?");
        setIsListening(false);
      }, 3000);
    }
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageSquare className="h-5 w-5" />
          Agricultural Assistant
          {userRole === 'farmer' && (
            <Badge variant="secondary" className="ml-2">
              Voice Enabled
            </Badge>
          )}
        </CardTitle>
        <CardDescription>
          Ask questions about crops, weather, soil analysis, and agricultural recommendations
        </CardDescription>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-0">
        <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
          <div className="space-y-4">
            {messages.map(message => (
              <div key={message.id} className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`flex gap-3 max-w-[80%] ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                    message.type === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'
                  }`}>
                    {message.type === 'user' ? <User className="h-4 w-4"/> : <Bot className="h-4 w-4"/>}
                  </div>
                  <div className={`rounded-lg p-3 ${
                    message.type === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'
                  }`}>
                    <p className="text-sm">{message.content}</p>
                    <p className={`text-xs mt-1 ${
                      message.type === 'user' ? 'text-primary-foreground/70' : 'text-muted-foreground'
                    }`}>
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {stage === 'processing' && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                <Bot className="h-4 w-4 animate-pulse" />
              </div>
              <div className="bg-muted rounded-lg p-3">
                <p className="text-sm text-muted-foreground">Processing your request...</p>
              </div>
            </div>
          )}
        </ScrollArea>

        {/* When awaiting box, render MapView in place of input */}
        {stage === 'awaitingBox'
          ? (
            <MapView userRole={userRole} onCoordinatesSelect={onBoxComplete} />
          )
          : (
            <div className="border-t p-4">
              <div className="flex gap-2">
                <Input
                  value={inputValue}
                  onChange={e => setInputValue(e.target.value)}
                  placeholder="Ask about crops, weather, soil analysis..."
                  onKeyPress={e => e.key === 'Enter' && handleSendMessage()}
                  className="flex-1"
                  disabled={stage !== 'idle'}
                />
                {userRole === 'farmer' && (
                  <Button
                    variant={isListening ? "destructive" : "outline"}
                    size="icon"
                    onClick={handleVoiceToggle}
                    disabled={stage !== 'idle'}
                  >
                    {isListening ? <MicOff className="h-4 w-4"/> : <Mic className="h-4 w-4"/>}
                  </Button>
                )}
                <Button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || stage !== 'idle'}
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
              {isListening && (
                <div className="mt-2 text-center">
                  <Badge variant="destructive" className="animate-pulse">
                    <Mic className="h-3 w-3 mr-1" />
                    Listening...
                  </Badge>
                </div>
              )}
            </div>
          )
        }
      </CardContent>
    </Card>
  );
}