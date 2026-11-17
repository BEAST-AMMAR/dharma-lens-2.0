import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { Scale, Upload, FileText, Languages, Mic, Brain, LogOut, User, History, Clock, Scroll, BookOpen, Users, Shield } from "lucide-react";
import { Session } from "@supabase/supabase-js";
import DocumentUpload from "@/components/DocumentUpload";
import ProcessingConfig from "@/components/ProcessingConfig";
import ResultsDisplay from "@/components/ResultsDisplay";

const Dashboard = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [currentDocumentPath, setCurrentDocumentPath] = useState<string>("");
  const [processingResult, setProcessingResult] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);

  const fetchHistory = async () => {
    try {
      const { data, error } = await supabase
        .from("processing_results")
        .select("*")
        .order("created_at", { ascending: false });
      if (data && !error) {
        setHistory(data);
      }
    } catch (err) {
      console.error("Failed to load document history", err);
    }
  };

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      let activeSession = session;
      if (!activeSession) {
        try {
          const raw = localStorage.getItem("vidhichakshu_offline_session");
          if (raw) {
            activeSession = JSON.parse(raw);
          }
        } catch (e) {
          // ignore
        }
      }

      setSession(activeSession);
      setIsLoading(false);
      if (!activeSession) {
        navigate("/auth");
      } else {
        fetchHistory();
      }
    }).catch(() => {
      // Offline fallback check on network rejection
      try {
        const raw = localStorage.getItem("vidhichakshu_offline_session");
        if (raw) {
          const activeSession = JSON.parse(raw);
          setSession(activeSession);
          setIsLoading(false);
          return;
        }
      } catch (e) {
        // ignore
      }
      setIsLoading(false);
      navigate("/auth");
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session) {
        setSession(session);
      }
    });

    return () => subscription.unsubscribe();
  }, [navigate]);

  const handleLogout = async () => {
    try {
      await supabase.auth.signOut();
    } catch (e) {
      // ignore
    }
    try {
      localStorage.removeItem("vidhichakshu_offline_session");
      const storageKey = Object.keys(localStorage).find(k => k.startsWith("sb-") && k.endsWith("-auth-token"));
      if (storageKey) localStorage.removeItem(storageKey);
    } catch (e) {
      // ignore
    }
    toast({ title: "Logged out successfully" });
    navigate("/auth");
  };

  const handleSelectHistoryItem = (item: any) => {
    const meta = item.metadata || {};
    const normalized = {
      text: item.extracted_text || item.text,
      extracted_text: item.extracted_text || item.text,
      redacted_text: meta.redacted_text || item.extracted_text || item.text,
      summary: item.summary,
      layman_summary: meta.layman_summary,
      archaic_terms: meta.archaic_terms || [],
      chauhaddi: meta.chauhaddi || {},
      lineage: meta.lineage || {},
      title_chain: meta.title_chain || [],
      title_health_score: meta.title_health_score !== undefined ? meta.title_health_score : 85,
      title_defects: meta.title_defects || [],
      translation: item.translation,
      entities: item.entities,
      legalAnalysis: item.legal_analysis,
      legal_analysis: item.legal_analysis,
      htrMetadata: meta.htrMetadata,
      audio_transcription: item.audio_transcription,
      document_id: item.document_id
    };
    setProcessingResult(normalized);
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  const features = [
    { icon: Scroll, title: "Heritage Scripts (HTR)", desc: "Modi, Halegannada & Nastaliq transliteration" },
    { icon: Users, title: "Citizen Layman Summary", desc: "Everyday explanations for citizens & farmers" },
    { icon: BookOpen, title: "Archaic Revenue Lexicon", desc: "Detects Khasra, Bainama, Watandar & Sanad" },
    { icon: Shield, title: "BNS & Land Law Engine", desc: "Statutory transitions & property checks" },
  ];

  return (
    <div className="min-h-screen bg-muted/30">
      {/* Header */}
      <header className="border-b bg-background">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-legal-gold-light rounded-lg">
              <Scale className="h-6 w-6 text-legal-gold" />
            </div>
            <div>
              <h1 className="text-xl font-bold">VidhiChakshu (विधि-चक्षु)</h1>
              <p className="text-sm text-muted-foreground">The AI Vision for Indian Legal & Heritage Documents</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-muted">
              <User className="h-4 w-4" />
              <span className="text-sm">{session?.user?.email}</span>
            </div>
            <Button variant="outline" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 space-y-8">
        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {features.map((feature, idx) => (
            <Card key={idx} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="p-2 bg-legal-gold-light rounded-lg w-fit mb-2">
                  <feature.icon className="h-5 w-5 text-legal-gold" />
                </div>
                <CardTitle className="text-base">{feature.title}</CardTitle>
                <CardDescription className="text-sm">{feature.desc}</CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>

        {/* History Section */}
        {history.length > 0 && (
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <History className="h-5 w-5 text-legal-gold" />
                My Documents History
              </CardTitle>
              <CardDescription>Previously processed documents and heritage deeds (Saved in your secure account)</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {history.map((item) => {
                  const docTitle = item.document_id ? item.document_id.split('/').pop() : `Document ${item.id.substring(0,6)}`;
                  const scriptType = item.metadata?.htrMetadata?.script_type;
                  return (
                    <Card 
                      key={item.id} 
                      className="p-4 cursor-pointer hover:border-legal-gold transition-colors"
                      onClick={() => handleSelectHistoryItem(item)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-2 mb-2 min-w-0">
                          <FileText className="h-4 w-4 text-legal-gold shrink-0" />
                          <p className="text-sm font-medium truncate" title={docTitle}>
                            {docTitle}
                          </p>
                        </div>
                      </div>
                      {scriptType && (
                        <p className="text-xs text-primary font-semibold mb-2 truncate">
                          📜 {scriptType}
                        </p>
                      )}
                      <div className="flex items-center gap-1 text-xs text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        {new Date(item.created_at).toLocaleDateString()} at {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </Card>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Document Upload Section */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5 text-legal-gold" />
              Upload Documents & Heritage Deeds
            </CardTitle>
            <CardDescription>
              Upload legal documents, century-old property deeds, handwritten manuscripts, or court audio recordings
            </CardDescription>
          </CardHeader>
          <CardContent>
            <DocumentUpload onUploadComplete={setCurrentDocumentPath} />
          </CardContent>
        </Card>

        {/* Processing Configuration */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle>Processing & Paleography Configuration</CardTitle>
            <CardDescription>
              Configure AI vision, script recognition, layman explanation, and statutory analysis options
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ProcessingConfig 
              documentPath={currentDocumentPath}
              onProcessingComplete={(res) => {
                setProcessingResult(res);
                fetchHistory(); // Automatically reload history so the card appears immediately!
              }}
            />
          </CardContent>
        </Card>

        {/* Results Display */}
        {processingResult && (
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle>Processing & Paleographic Analysis Results</CardTitle>
              <CardDescription>
                AI-generated transcription, layman summary, archaic revenue terms, and statutory legal intelligence
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResultsDisplay result={processingResult} />
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
