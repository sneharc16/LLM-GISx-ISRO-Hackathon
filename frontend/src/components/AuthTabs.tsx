import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Building2, Users } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface AuthTabsProps {
  onAuthSuccess: (userType: 'ministry' | 'farmer', userData: any) => void;
}

export default function AuthTabs({ onAuthSuccess }: AuthTabsProps) {
  const [ministryForm, setMinistryForm] = useState({ email: "", password: "" });
  const [farmerSignIn, setFarmerSignIn] = useState({ mobile: "", password: "" });
  const [farmerSignUp, setFarmerSignUp] = useState({ name: "", mobile: "", password: "" });
  const [activeTab, setActiveTab] = useState("ministry");
  const [farmerMode, setFarmerMode] = useState<"signin" | "signup">("signin");
  const { toast } = useToast();

  const handleMinistryLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (!ministryForm.email || !ministryForm.password) {
      toast({
        title: "Missing Information",
        description: "Please fill in all fields",
        variant: "destructive"
      });
      return;
    }
    
    // Simulate authentication
    toast({
      title: "Welcome Back!",
      description: "Ministry login successful",
    });
    
    onAuthSuccess('ministry', {
      email: ministryForm.email,
      role: 'ministry'
    });
  };

  const handleFarmerAuth = (e: React.FormEvent) => {
    e.preventDefault();
    const data = farmerMode === "signin" ? farmerSignIn : farmerSignUp;
    
    if (!data.mobile || !data.password || (farmerMode === "signup" && !farmerSignUp.name)) {
      toast({
        title: "Missing Information",
        description: "Please fill in all fields",
        variant: "destructive"
      });
      return;
    }

    toast({
      title: farmerMode === "signin" ? "Welcome Back!" : "Account Created!",
      description: `Farmer ${farmerMode === "signin" ? "login" : "registration"} successful`,
    });

    onAuthSuccess('farmer', {
      mobile: data.mobile,
      name: farmerMode === "signup" ? farmerSignUp.name : "Farmer",
      role: 'farmer'
    });
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2 mb-6">
          <TabsTrigger value="ministry" className="flex items-center gap-2">
            <Building2 className="h-4 w-4" />
            Ministry
          </TabsTrigger>
          <TabsTrigger value="farmer" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            Farmer
          </TabsTrigger>
        </TabsList>

        <TabsContent value="ministry">
          <Card>
            <CardHeader className="text-center">
              <CardTitle className="text-xl font-semibold">Ministry Portal</CardTitle>
              <CardDescription>
                Access the administrative dashboard with email and password
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleMinistryLogin} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="ministry-email">Email Address</Label>
                  <Input
                    id="ministry-email"
                    type="email"
                    value={ministryForm.email}
                    onChange={(e) => setMinistryForm(prev => ({ ...prev, email: e.target.value }))}
                    placeholder="ministry@gov.in"
                    className="w-full"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="ministry-password">Password</Label>
                  <Input
                    id="ministry-password"
                    type="password"
                    value={ministryForm.password}
                    onChange={(e) => setMinistryForm(prev => ({ ...prev, password: e.target.value }))}
                    placeholder="Enter your password"
                    className="w-full"
                  />
                </div>
                <Button type="submit" className="w-full">
                  Sign In to Ministry Portal
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="farmer">
          <Card>
            <CardHeader className="text-center">
              <CardTitle className="text-xl font-semibold">Farmer Portal</CardTitle>
              <CardDescription>
                Join the community with your mobile number
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2 mb-4">
                <Button
                  variant={farmerMode === "signin" ? "default" : "outline"}
                  onClick={() => setFarmerMode("signin")}
                  className="flex-1"
                >
                  Sign In
                </Button>
                <Button
                  variant={farmerMode === "signup" ? "default" : "outline"}
                  onClick={() => setFarmerMode("signup")}
                  className="flex-1"
                >
                  Sign Up
                </Button>
              </div>

              <Separator className="my-4" />

              <form onSubmit={handleFarmerAuth} className="space-y-4">
                {farmerMode === "signup" && (
                  <div className="space-y-2">
                    <Label htmlFor="farmer-name">Full Name</Label>
                    <Input
                      id="farmer-name"
                      type="text"
                      value={farmerSignUp.name}
                      onChange={(e) => setFarmerSignUp(prev => ({ ...prev, name: e.target.value }))}
                      placeholder="Enter your full name"
                      className="w-full"
                    />
                  </div>
                )}
                
                <div className="space-y-2">
                  <Label htmlFor="farmer-mobile">Mobile Number</Label>
                  <Input
                    id="farmer-mobile"
                    type="tel"
                    value={farmerMode === "signin" ? farmerSignIn.mobile : farmerSignUp.mobile}
                    onChange={(e) => {
                      const value = e.target.value;
                      if (farmerMode === "signin") {
                        setFarmerSignIn(prev => ({ ...prev, mobile: value }));
                      } else {
                        setFarmerSignUp(prev => ({ ...prev, mobile: value }));
                      }
                    }}
                    placeholder="+91 98765 43210"
                    className="w-full"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="farmer-password">Password</Label>
                  <Input
                    id="farmer-password"
                    type="password"
                    value={farmerMode === "signin" ? farmerSignIn.password : farmerSignUp.password}
                    onChange={(e) => {
                      const value = e.target.value;
                      if (farmerMode === "signin") {
                        setFarmerSignIn(prev => ({ ...prev, password: value }));
                      } else {
                        setFarmerSignUp(prev => ({ ...prev, password: value }));
                      }
                    }}
                    placeholder="Enter your password"
                    className="w-full"
                  />
                </div>
                
                <Button type="submit" className="w-full">
                  {farmerMode === "signin" ? "Sign In" : "Create Account"}
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}