import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { FileText, Brain, Languages, Scale, Users, AlertTriangle, Mic, ThumbsUp, ThumbsDown, MessageSquare, Send } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { supabase } from "@/integrations/supabase/client";

interface ResultsDisplayProps {
  result: {
    extracted_text?: string;
    redacted_text?: string;
    summary?: string;
    translation?: string;
    entities?: any;
    legal_analysis?: any;
    metadata?: any;
    htrMetadata?: {
      script_type?: string;
      confidence_score?: number;
      needs_human_verification?: boolean;
    };
    audio_transcription?: string;
  };
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

const ResultsDisplay = ({ result }: ResultsDisplayProps) => {
  const [feedbackGiven, setFeedbackGiven] = useState<'up' | 'down' | null>(null);
  
  // Chat state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([{role: 'assistant', content: 'Hello! I have analyzed this document. What would you like to know?'}]);
  const [chatInput, setChatInput] = useState("");
  const [isChatting, setIsChatting] = useState(false);

  const handleFeedback = async (type: 'up' | 'down') => {
    if (feedbackGiven) return;
    setFeedbackGiven(type);
    
    // Extract chunk IDs from retrieved legal analysis citations
    const citations = result.legal_analysis?.citations || result.legal_analysis?.relevant_articles || [];
    const chunkIds = Array.isArray(citations) 
      ? citations.map((c: any) => c.id || c.section || c.title || "chunk_ref").filter(Boolean)
      : [];

    try {
      await supabase.from('rlhf_feedback').insert({
        query_text: result.summary?.substring(0, 100) || "Summary Evaluation",
        retrieved_chunk_ids: chunkIds,
        response_text: result.summary || "",
        retrieval_strategy: "agentic_graph_hybrid",
        reward_score: type === 'up' ? 1.0 : -1.0
      });
    } catch (e) {
      console.error("Failed to submit RLHF feedback", e);
    }
  };

  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;
    
    const newMessage: ChatMessage = { role: 'user', content: chatInput };
    setChatMessages(prev => [...prev, newMessage]);
    setChatInput("");
    setIsChatting(true);
    
    try {
      const { data: { session } } = await supabase.auth.getSession();
      const apiUrl = import.meta.env.VITE_API_GATEWAY_URL || 'http://localhost:3000';
      
      const res = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`
        },
        body: JSON.stringify({
          document_text: result.redacted_text || result.extracted_text || "",
          query: newMessage.content,
          chat_history: chatMessages.slice(1)
        })
      });
      
      const data = await res.json();
      if (data.success) {
        setChatMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);
      } else {
        setChatMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I encountered an error answering that." }]);
      }
    } catch (e) {
      setChatMessages(prev => [...prev, { role: 'assistant', content: "Connection error." }]);
    } finally {
      setIsChatting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Historical Script Recognition Banner */}
      {result.htrMetadata && (
        <Alert variant={result.htrMetadata.needs_human_verification ? "destructive" : "default"} className="border-legal-gold bg-legal-gold-light/10">
          <AlertTriangle className="h-4 w-4 text-legal-gold" />
          <AlertTitle className="font-bold">Historical Script Recognition: {result.htrMetadata.script_type}</AlertTitle>
          <AlertDescription>
            Extraction Confidence: <strong>{((result.htrMetadata.confidence_score || 0.8) * 100).toFixed(1)}%</strong>. 
            {result.htrMetadata.needs_human_verification 
              ? " ⚠️ Low confidence transcription — manual verification recommended before relying on legal claims."
              : " Transliterated to modern Devanagari/English cleanly."}
          </AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="summary" className="w-full">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="summary">Summary</TabsTrigger>
          <TabsTrigger value="chat" className="font-bold text-legal-gold">Chat</TabsTrigger>
          <TabsTrigger value="text">Extracted Text</TabsTrigger>
          <TabsTrigger value="translation">Translation</TabsTrigger>
          <TabsTrigger value="entities">Entities</TabsTrigger>
          <TabsTrigger value="legal">Legal Analysis</TabsTrigger>
          {result.audio_transcription && (
            <TabsTrigger value="audio">Audio</TabsTrigger>
          )}
        </TabsList>

        {result.metadata?.truncated && (
          <Alert variant="destructive" className="bg-destructive/10 text-destructive border-destructive/20 mt-4">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>Warning: Document Truncated</AlertTitle>
            <AlertDescription>
              This document was too long for full processing. Analysis covers only the first part of the document.
            </AlertDescription>
          </Alert>
        )}

        <TabsContent value="chat" className="space-y-4">
          <Card className="flex flex-col h-[600px]">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-legal-gold" />
                Chat with Document
              </CardTitle>
              <CardDescription>
                Ask specific legal questions about this document's contents.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-1 overflow-y-auto space-y-4">
              {chatMessages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] rounded-lg p-3 ${msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  </div>
                </div>
              ))}
              {isChatting && (
                <div className="flex justify-start">
                  <div className="bg-muted max-w-[80%] rounded-lg p-3">
                    <p className="text-sm text-muted-foreground animate-pulse">Thinking...</p>
                  </div>
                </div>
              )}
            </CardContent>
            <CardFooter className="pt-4 border-t">
              <div className="flex w-full items-center space-x-2">
                <Input 
                  placeholder="e.g. Does this document mention penal codes or land rights?" 
                  value={chatInput} 
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                  disabled={isChatting}
                />
                <Button size="icon" onClick={handleSendMessage} disabled={isChatting || !chatInput.trim()}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </CardFooter>
          </Card>
        </TabsContent>

        <TabsContent value="summary" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5 text-legal-gold" />
                  AI-Generated Legal Summary
                </CardTitle>
                <CardDescription>
                  Synthesized overview of the legal document
                </CardDescription>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-xs text-muted-foreground mr-2">Rate this analysis (RLHF)</span>
                <Button 
                  variant={feedbackGiven === 'up' ? "default" : "outline"} 
                  size="sm" 
                  onClick={() => handleFeedback('up')}
                  disabled={feedbackGiven !== null}
                >
                  <ThumbsUp className="h-4 w-4" />
                </Button>
                <Button 
                  variant={feedbackGiven === 'down' ? "destructive" : "outline"} 
                  size="sm" 
                  onClick={() => handleFeedback('down')}
                  disabled={feedbackGiven !== null}
                >
                  <ThumbsDown className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed whitespace-pre-wrap">
                {result.summary || "No summary available"}
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="text" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-legal-gold" />
                Extracted & Redacted Text
              </CardTitle>
              <CardDescription>
                Complete text extracted from the document (PII Redacted for Security)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="max-h-[500px] overflow-y-auto">
                <p className="text-sm leading-relaxed whitespace-pre-wrap font-mono">
                  {result.redacted_text || result.extracted_text || "No text extracted"}
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="translation" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Languages className="h-5 w-5 text-legal-gold" />
                Translation
              </CardTitle>
              <CardDescription>
                Translated version of the legal document
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="max-h-[500px] overflow-y-auto">
                <p className="text-sm leading-relaxed whitespace-pre-wrap">
                  {result.translation || "No translation available"}
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="entities" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5 text-legal-gold" />
                Extracted Entities
              </CardTitle>
              <CardDescription>
                Legal entities identified in the document
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {result.entities && typeof result.entities === 'object' ? (
                  Object.entries(result.entities).map(([category, items]) => (
                    <div key={category}>
                      <h4 className="font-medium text-sm capitalize mb-2">{category.replace(/_/g, ' ')}</h4>
                      <div className="flex flex-wrap gap-2">
                        {Array.isArray(items) && items.length > 0 ? (
                          items.map((item: string, idx: number) => (
                            <Badge key={idx} variant="secondary">
                              {item}
                            </Badge>
                          ))
                        ) : (
                          <span className="text-sm text-muted-foreground">None found</span>
                        )}
                      </div>
                      {Object.keys(result.entities).indexOf(category) < Object.keys(result.entities).length - 1 && (
                        <Separator className="mt-4" />
                      )}
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground">No entities extracted</p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="legal" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Scale className="h-5 w-5 text-legal-gold" />
                Agentic Constitutional & Statutory Analysis
              </CardTitle>
              <CardDescription>
                Multi-Agent RAG Findings with IPC &lt;-&gt; BNS Transitions &amp; Verified Citations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {result.legal_analysis && typeof result.legal_analysis === 'object' ? (
                  Object.entries(result.legal_analysis).map(([key, value]) => (
                    <div key={key}>
                      <h4 className="font-semibold text-sm capitalize mb-2 text-primary">
                        {key.replace(/_/g, ' ')}
                      </h4>
                      {Array.isArray(value) ? (
                        <div className="space-y-2">
                          {value.map((item: any, idx: number) => (
                            <div key={idx} className="text-sm border-l-2 border-legal-gold pl-3 py-1 bg-muted/20 rounded-r">
                              {typeof item === 'object' ? (
                                <div>
                                  <div className="font-bold">{item.section || item.title} {item.similarity ? `(Relevance: ${(item.similarity * 100).toFixed(0)}%)` : ''}</div>
                                  <div className="text-muted-foreground text-xs">{item.content}</div>
                                  {item.replaces && <Badge variant="outline" className="mt-1 text-[10px]">Replaces: {item.replaces}</Badge>}
                                </div>
                              ) : (
                                <span>{String(item)}</span>
                              )}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-muted-foreground">{String(value)}</p>
                      )}
                      {Object.keys(result.legal_analysis).indexOf(key) < Object.keys(result.legal_analysis).length - 1 && (
                        <Separator className="mt-4" />
                      )}
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground">No legal analysis available</p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {result.audio_transcription && (
          <TabsContent value="audio" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Mic className="h-5 w-5 text-legal-gold" />
                  Audio Transcription (faster-whisper)
                </CardTitle>
                <CardDescription>
                  Text transcribed from the audio recording
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="max-h-[500px] overflow-y-auto">
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">
                    {result.audio_transcription}
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        )}
      </Tabs>
    </div>
  );
};

export default ResultsDisplay;