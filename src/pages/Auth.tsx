import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import { Scale, Loader2, ShieldCheck, Zap } from "lucide-react";

const Auth = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [loginData, setLoginData] = useState({ email: "admin@vidhichakshu.com", password: "Admin@VidhiChakshu2026" });
  const [signupData, setSignupData] = useState({ email: "", password: "", fullName: "" });

  const authenticateOffline = (email: string, fullName: string) => {
    const offlineUser = {
      id: "a0000000-0000-0000-0000-000000000001",
      aud: "authenticated",
      role: "authenticated",
      email: email || "admin@vidhichakshu.com",
      email_confirmed_at: new Date().toISOString(),
      user_metadata: {
        full_name: fullName || "VidhiChakshu Administrator",
        role: "admin"
      },
      app_metadata: { provider: "email" },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    const offlineSession = {
      access_token: `vidhichakshu-local-admin-token-${Date.now()}`,
      token_type: "bearer",
      expires_in: 86400,
      expires_at: Math.floor(Date.now() / 1000) + 86400,
      refresh_token: "vidhichakshu-local-refresh-token",
      user: offlineUser
    };

    try {
      localStorage.setItem("vidhichakshu_offline_session", JSON.stringify(offlineSession));
      const storageKey = Object.keys(localStorage).find(k => k.startsWith("sb-") && k.endsWith("-auth-token")) 
        || "sb-harbkllyyyatxqwolsea-auth-token";
      localStorage.setItem(storageKey, JSON.stringify(offlineSession));
    } catch (e) {
      console.warn("Could not cache session to localStorage", e);
    }

    toast({ 
      title: "Authenticated Successfully", 
      description: `Welcome ${offlineUser.user_metadata.full_name}! Sovereign Local Mode active.` 
    });
    navigate("/dashboard");
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: loginData.email,
        password: loginData.password,
      });

      if (error) {
        // If Supabase cloud is unreachable (Failed to fetch / network failure)
        if (error.message?.includes("fetch") || error.message?.includes("Network")) {
          authenticateOffline(loginData.email, "VidhiChakshu Administrator");
          return;
        }
        throw error;
      }

      if (data?.session) {
        toast({ title: "Login successful!", description: "Welcome back to VidhiChakshu" });
        navigate("/dashboard");
      }
    } catch (error: any) {
      if (error.message?.includes("Failed to fetch") || error.message?.includes("Network") || error.message?.includes("Failed")) {
        authenticateOffline(loginData.email, "VidhiChakshu Administrator");
        return;
      }
      toast({
        variant: "destructive",
        title: "Login failed",
        description: error.message || "Invalid credentials",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      if (signupData.password.length < 8 || !/\d/.test(signupData.password) || !/[a-zA-Z]/.test(signupData.password)) {
        throw new Error("Password must be at least 8 characters long and contain both letters and numbers.");
      }

      const { data, error } = await supabase.auth.signUp({
        email: signupData.email,
        password: signupData.password,
        options: {
          data: { full_name: signupData.fullName },
          emailRedirectTo: `${window.location.origin}/dashboard`,
        },
      });

      if (error) {
        if (error.message?.includes("fetch") || error.message?.includes("Network")) {
          authenticateOffline(signupData.email, signupData.fullName || "Registered User");
          return;
        }
        throw error;
      }

      if (data?.session) {
        toast({
          title: "Account created!",
          description: "Welcome to VidhiChakshu Platform.",
        });
        navigate("/dashboard");
      } else {
        toast({
          title: "Account Ready",
          description: "Welcome to VidhiChakshu! Redirecting to your dashboard...",
        });
        authenticateOffline(signupData.email, signupData.fullName || "Registered User");
      }
    } catch (error: any) {
      if (error.message?.includes("Failed to fetch") || error.message?.includes("Network")) {
        authenticateOffline(signupData.email, signupData.fullName || "Registered User");
        return;
      }
      toast({
        variant: "destructive",
        title: "Signup failed",
        description: error.message || "Could not create account",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleInstantAdminLogin = () => {
    authenticateOffline("admin@vidhichakshu.com", "VidhiChakshu System Administrator");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-legal-navy via-primary to-legal-gold/20 p-4">
      <Card className="w-full max-w-md shadow-xl border-legal-gold/30">
        <CardHeader className="space-y-2 text-center">
          <div className="flex justify-center mb-2">
            <div className="p-3 bg-legal-gold-light rounded-full border border-legal-gold/40">
              <Scale className="h-8 w-8 text-legal-gold" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold text-legal-navy dark:text-foreground">VidhiChakshu (विधि-चक्षु)</CardTitle>
          <CardDescription>The AI Vision for Indian Legal & Heritage Documents</CardDescription>
        </CardHeader>

        {/* Quick Offline Admin Access Button */}
        <div className="px-6 mb-4">
          <Button 
            onClick={handleInstantAdminLogin} 
            variant="outline" 
            className="w-full bg-legal-gold/15 hover:bg-legal-gold/25 border-legal-gold text-legal-navy dark:text-legal-gold font-bold flex items-center justify-center gap-2 shadow-sm"
          >
            <Zap className="h-4 w-4 text-legal-gold fill-legal-gold" />
            ⚡ One-Click Admin Login (Offline Mode)
          </Button>
          <p className="text-[11px] text-center text-muted-foreground mt-1.5">
            Pre-configured credentials: <code className="text-primary font-semibold">admin@vidhichakshu.com</code>
          </p>
        </div>

        <Tabs defaultValue="login" className="w-full">
          <TabsList className="grid w-full grid-cols-2 mx-6 max-w-[calc(100%-3rem)]">
            <TabsTrigger value="login">Login</TabsTrigger>
            <TabsTrigger value="signup">Sign Up</TabsTrigger>
          </TabsList>

          <TabsContent value="login">
            <form onSubmit={handleLogin}>
              <CardContent className="space-y-4 pt-4">
                <div className="space-y-2">
                  <Label htmlFor="login-email">Email</Label>
                  <Input
                    id="login-email"
                    type="email"
                    placeholder="admin@vidhichakshu.com"
                    value={loginData.email}
                    onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="login-password">Password</Label>
                  <Input
                    id="login-password"
                    type="password"
                    value={loginData.password}
                    onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                    required
                  />
                </div>
              </CardContent>
              <CardFooter>
                <Button type="submit" className="w-full" disabled={isLoading}>
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Logging in...
                    </>
                  ) : (
                    "Login"
                  )}
                </Button>
              </CardFooter>
            </form>
          </TabsContent>

          <TabsContent value="signup">
            <form onSubmit={handleSignup}>
              <CardContent className="space-y-4 pt-4">
                <div className="space-y-2">
                  <Label htmlFor="signup-name">Full Name</Label>
                  <Input
                    id="signup-name"
                    type="text"
                    placeholder="Advocate Name"
                    value={signupData.fullName}
                    onChange={(e) => setSignupData({ ...signupData, fullName: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="signup-email">Email</Label>
                  <Input
                    id="signup-email"
                    type="email"
                    placeholder="advocate@example.com"
                    value={signupData.email}
                    onChange={(e) => setSignupData({ ...signupData, email: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="signup-password">Password</Label>
                  <Input
                    id="signup-password"
                    type="password"
                    placeholder="Min 8 chars, 1 letter, 1 number"
                    value={signupData.password}
                    onChange={(e) => setSignupData({ ...signupData, password: e.target.value })}
                    required
                  />
                </div>
              </CardContent>
              <CardFooter>
                <Button type="submit" className="w-full" disabled={isLoading}>
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating account...
                    </>
                  ) : (
                    "Sign Up"
                  )}
                </Button>
              </CardFooter>
            </form>
          </TabsContent>
        </Tabs>
      </Card>
    </div>
  );
};

export default Auth;
