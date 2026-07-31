import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { Scale, Upload, FileText, Languages, Mic, Brain, LogOut, User, History, Clock } from "lucide-react";
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
    const { data, error } = await supabase
      .from("processing_results")
      .select("*")
      .order("created_at", { ascending: false });
    if (data && !error) {
      setHistory(data);
    }
  };

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setIsLoading(false);
      if (!session) {
        navigate("/auth");
      } else {
        fetchHistory();
      }
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      if (!session) {
        navigate("/auth");
      }
    });

    return () => subscription.unsubscribe();
  }, [navigate]);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    toast({ title: "Logged out successfully" });
    navigate("/");
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  const features = [
    { icon: FileText, title: "OCR Processing", desc: "Extract text from legal documents" },
    { icon: Brain, title: "AI Summarization", desc: "Generate concise summaries" },
    { icon: Languages, title: "Translation", desc: "22+ Indian languages supported" },
    { icon: Mic, title: "Audio Transcription", desc: "Court proceedings & hearings" },
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
              <h1 className="text-xl font-bold">Dharma Lens</h1>
              <p className="text-sm text-muted-foreground">Document Processing Dashboard</p>
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
              <CardDescription>Previously processed documents</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {history.map((item) => (
                  <Card 
                    key={item.id} 
                    className="p-4 cursor-pointer hover:border-legal-gold transition-colors"
                    onClick={() => {
                      setProcessingResult(item.result || item);
                      window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
                    }}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2 mb-2">
                        <FileText className="h-4 w-4 text-muted-foreground" />
                        <p className="text-sm font-medium truncate" title={item.document_path || `Document ${item.id.substring(0,6)}`}>
                          {item.document_path ? item.document_path.split('/').pop() : `Document ${item.id.substring(0,6)}`}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-1 text-xs text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      {new Date(item.created_at).toLocaleDateString()}
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Document Upload Section */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5 text-legal-gold" />
              Upload Documents
            </CardTitle>
            <CardDescription>
              Upload legal documents for AI processing (PDF, Images, Audio files)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <DocumentUpload onUploadComplete={setCurrentDocumentPath} />
          </CardContent>
        </Card>

        {/* Processing Configuration */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle>Processing Configuration</CardTitle>
            <CardDescription>
              Configure AI processing options for your documents
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ProcessingConfig 
              documentPath={currentDocumentPath}
              onProcessingComplete={setProcessingResult}
            />
          </CardContent>
        </Card>

        {/* Results Display */}
        {processingResult && (
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle>Processing Results</CardTitle>
              <CardDescription>
                AI-generated analysis and extracted information
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
