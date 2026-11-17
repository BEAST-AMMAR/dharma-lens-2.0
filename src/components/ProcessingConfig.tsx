import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Card } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Settings, Play } from "lucide-react";
import { ACCEPTED_EXTENSIONS } from "@/lib/fileTypes";

interface ProcessingConfigProps {
  documentPath?: string;
  onProcessingComplete?: (result: any) => void;
}

const ProcessingConfig = ({ documentPath, onProcessingComplete }: ProcessingConfigProps) => {
  const { toast } = useToast();
  const [isProcessing, setIsProcessing] = useState(false);
  const [config, setConfig] = useState({
    processingMode: "hybrid", // "hybrid" | "local" | "cloud"
    historicalScriptType: "auto", // "auto" | "modi" | "halegannada" | "perso-arabic"
    targetLanguage: "auto",
    summaryLength: 200,
    enableOCR: true,
    enableSummarization: true,
    enableTranslation: false,
    enableAudioTranscription: false,
    enableLegalAnalysis: true,
    enableEntityExtraction: true,
    enableHistoricalHTR: false,
  });

  const languages = [
    { value: "auto", label: "Auto Detect" },
    { value: "hi", label: "Hindi" },
    { value: "en", label: "English" },
    { value: "bn", label: "Bengali" },
    { value: "te", label: "Telugu" },
    { value: "mr", label: "Marathi" },
    { value: "ta", label: "Tamil" },
    { value: "gu", label: "Gujarati" },
    { value: "kn", label: "Kannada" },
    { value: "ml", label: "Malayalam" },
    { value: "pa", label: "Punjabi" },
  ];

  const handleProcess = async () => {
    if (!documentPath) {
      toast({
        title: "No document selected",
        description: "Please upload a document first",
        variant: "destructive",
      });
      return;
    }

    // Validate file type
    const extension = documentPath.split('.').pop()?.toLowerCase();
    if (extension && !ACCEPTED_EXTENSIONS.includes(extension)) {
      toast({
        title: "Unsupported file type",
        description: `Please upload supported file types: ${ACCEPTED_EXTENSIONS.join(', ')}`,
        variant: "destructive",
      });
      return;
    }

    setIsProcessing(true);

    try {
      // Get current session for JWT with sovereign offline fallback
      let token = "vidhichakshu-local-admin-token";
      try {
        const { data: { session } } = await supabase.auth.getSession();
        if (session?.access_token) {
          token = session.access_token;
        } else {
          const stored = localStorage.getItem("vidhichakshu-offline-session");
          if (stored) {
            token = JSON.parse(stored).access_token || token;
          }
        }
      } catch {
        // use fallback token
      }

      const apiUrl = import.meta.env.VITE_API_GATEWAY_URL || 'http://localhost:3000';
      let response: Response | null = null;
      let effectiveBaseUrl = apiUrl;

      // Primary: Node.js API Gateway
      try {
        response = await fetch(`${apiUrl}/api/process-document`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ documentPath, config })
        });
      } catch (gateErr) {
        console.warn('[Process] Gateway unreachable, attempting direct Python engine:', gateErr);
      }

      // Secondary: Direct Python AI Engine (Port 8000)
      if (!response || !response.ok) {
        try {
          const directPyRes = await fetch(`http://localhost:8000/process`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ documentPath, config })
          });
          if (directPyRes.ok) {
            response = directPyRes;
            effectiveBaseUrl = 'http://localhost:8000';
          }
        } catch (directErr) {
          console.warn('[Process] Direct Python engine unreachable:', directErr);
        }
      }

      if (!response) {
        throw new Error('Both API Gateway (port 3000) and AI Engine (port 8000) are currently unreachable.');
      }

      const data = await response.json().catch(() => null);

      if (response.status === 429) {
        toast({
          title: "Rate limit exceeded",
          description: "Too many requests. Please wait a moment and try again.",
          variant: "destructive",
        });
        return;
      }

      if (!response.ok || data?.success === false) {
        toast({
          title: "Processing failed",
          description: data?.error || data?.detail || "Failed to process document",
          variant: "destructive",
        });
        return;
      }

      if (data?.success && data?.job_id) {
        toast({
          title: "Processing started",
          description: `Document queued using ${config.processingMode.toUpperCase()} mode...`,
        });

        // Polling loop with max attempts safety cap
        const jobId = data.job_id;
        let jobFinished = false;
        let attempts = 0;
        const maxAttempts = 100; // Cap at 5 minutes
        
        while (!jobFinished && attempts < maxAttempts) {
          attempts++;
          await new Promise(resolve => setTimeout(resolve, 3000));
          
          const statusUrl = effectiveBaseUrl.includes(':8000')
            ? `http://localhost:8000/job/${jobId}`
            : `${apiUrl}/api/job/${jobId}`;

          const statusRes = await fetch(statusUrl, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          const statusData = await statusRes.json().catch(() => null);
          if (!statusData) continue;
          
          if (statusData.status === 'completed') {
            jobFinished = true;
            toast({
              title: "Processing complete",
              description: "Your document has been processed successfully",
            });
            onProcessingComplete?.(statusData.result);
          } else if (statusData.status === 'failed') {
            jobFinished = true;
            toast({
              title: "Processing failed",
              description: statusData.error || "Job failed on backend",
              variant: "destructive",
            });
          }
        }

        if (!jobFinished && attempts >= maxAttempts) {
          toast({
            title: "Processing timeout",
            description: "Job exceeded maximum allowed waiting time.",
            variant: "destructive",
          });
        }
      } else {
        toast({
          title: "Unexpected response",
          description: "Failed to queue job",
          variant: "destructive",
        });
      }
    } catch (error: any) {
      toast({
        title: "Processing failed",
        description: error.message || "An unexpected error occurred",
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Model Mode Selection (Hybrid / Local / Cloud) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="processingMode" className="font-semibold text-legal-gold">VidhiChakshu AI Execution Engine</Label>
          <Select
            value={config.processingMode}
            onValueChange={(value) => setConfig({ ...config, processingMode: value })}
          >
            <SelectTrigger id="processingMode">
              <SelectValue placeholder="Select processing mode" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="hybrid">⚡ Hybrid Mode (Local Ollama + Auto Cloud Failover)</SelectItem>
              <SelectItem value="local">🔒 Local Offline Mode (Ollama Qwen2.5-7B / Air-Gapped)</SelectItem>
              <SelectItem value="cloud">☁️ Cloud Mode (Multi-Modal Vision & OpenRouter)</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Translation Language */}
        <div className="space-y-2">
          <Label htmlFor="language">Target Translation Language</Label>
          <Select
            value={config.targetLanguage}
            onValueChange={(value) => setConfig({ ...config, targetLanguage: value })}
          >
            <SelectTrigger id="language">
              <SelectValue placeholder="Select language" />
            </SelectTrigger>
            <SelectContent>
              {languages.map(lang => (
                <SelectItem key={lang.value} value={lang.value}>
                  {lang.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Historical Script Recognition Options */}
      <div className="p-4 border rounded-lg bg-muted/30 space-y-3">
        <div className="flex items-center space-x-2">
          <Checkbox
            id="historical"
            checked={config.enableHistoricalHTR}
            onCheckedChange={(checked) =>
              setConfig({ ...config, enableHistoricalHTR: checked as boolean })
            }
          />
          <Label htmlFor="historical" className="font-medium cursor-pointer text-primary">
            📜 Enable Historical / Ancient Script Recognition (HTR Track)
          </Label>
        </div>
        
        {config.enableHistoricalHTR && (
          <div className="pl-6 space-y-2">
            <Label htmlFor="scriptType" className="text-sm text-muted-foreground">Historical Script Specialist Model</Label>
            <Select
              value={config.historicalScriptType}
              onValueChange={(val) => setConfig({ ...config, historicalScriptType: val })}
            >
              <SelectTrigger id="scriptType" className="w-full">
                <SelectValue placeholder="Select script" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="auto">Auto Detect Historical Script</SelectItem>
                <SelectItem value="modi">Modi Script (Maharashtra 17th–20th c. Land Deeds - Paleography VLM)</SelectItem>
                <SelectItem value="halegannada">Halegannada (Old Kannada Historical Grants - Epigraphy VLM)</SelectItem>
                <SelectItem value="perso-arabic">Perso-Arabic (Urdu/Persian Nastaliq Revenue Records - Paleography VLM)</SelectItem>
              </SelectContent>
            </Select>
          </div>
        )}
      </div>

      {/* Summary Length */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label>Summary Length</Label>
          <span className="text-sm text-muted-foreground">{config.summaryLength} words</span>
        </div>
        <Slider
          value={[config.summaryLength]}
          onValueChange={([value]) => setConfig({ ...config, summaryLength: value })}
          min={50}
          max={500}
          step={50}
          className="py-4"
        />
      </div>

      <Separator />

      {/* Processing Options */}
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Settings className="h-4 w-4 text-legal-gold" />
          <Label className="text-base font-medium">Processing Options</Label>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card className="p-4 space-y-3">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="ocr"
                checked={config.enableOCR}
                onCheckedChange={(checked) =>
                  setConfig({ ...config, enableOCR: checked as boolean })
                }
              />
              <Label htmlFor="ocr" className="font-normal cursor-pointer">
                Enable OCR (Text Extraction)
              </Label>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="summarization"
                checked={config.enableSummarization}
                onCheckedChange={(checked) =>
                  setConfig({ ...config, enableSummarization: checked as boolean })
                }
              />
              <Label htmlFor="summarization" className="font-normal cursor-pointer">
                Enable AI Summarization
              </Label>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="translation"
                checked={config.enableTranslation}
                onCheckedChange={(checked) =>
                  setConfig({ ...config, enableTranslation: checked as boolean })
                }
              />
              <Label htmlFor="translation" className="font-normal cursor-pointer">
                Enable Translation
              </Label>
            </div>
          </Card>

          <Card className="p-4 space-y-3">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="audio"
                checked={config.enableAudioTranscription}
                onCheckedChange={(checked) =>
                  setConfig({ ...config, enableAudioTranscription: checked as boolean })
                }
              />
              <Label htmlFor="audio" className="font-normal cursor-pointer">
                Enable Audio Transcription (faster-whisper)
              </Label>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="legal"
                checked={config.enableLegalAnalysis}
                onCheckedChange={(checked) =>
                  setConfig({ ...config, enableLegalAnalysis: checked as boolean })
                }
              />
              <Label htmlFor="legal" className="font-normal cursor-pointer">
                Enable Agentic Legal RAG Analysis
              </Label>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="entity"
                checked={config.enableEntityExtraction}
                onCheckedChange={(checked) =>
                  setConfig({ ...config, enableEntityExtraction: checked as boolean })
                }
              />
              <Label htmlFor="entity" className="font-normal cursor-pointer">
                Enable Entity Extraction
              </Label>
            </div>
          </Card>
        </div>
      </div>

      {/* Action Button */}
      <Button 
        onClick={handleProcess} 
        className="w-full" 
        size="lg"
        disabled={isProcessing || !documentPath}
      >
        <Play className="mr-2 h-5 w-5" />
        {isProcessing ? "Processing Document..." : `Start Processing (${config.processingMode.toUpperCase()})`}
      </Button>
    </div>
  );
};

export default ProcessingConfig;

