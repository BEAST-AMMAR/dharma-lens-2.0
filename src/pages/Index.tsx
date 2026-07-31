import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Scale, Brain, Languages, FileText, Mic, Shield, ArrowRight, CheckCircle2 } from "lucide-react";

const Index = () => {
  const features = [
    {
      icon: FileText,
      title: "Advanced OCR",
      description: "Extract text from legal documents with 99%+ accuracy using multiple OCR engines",
    },
    {
      icon: Brain,
      title: "AI Summarization",
      description: "Generate concise summaries using state-of-the-art large language models",
    },
    {
      icon: Languages,
      title: "Multi-Language Translation",
      description: "Translate to 22+ Indian languages with context-aware accuracy",
    },
    {
      icon: Mic,
      title: "Audio Transcription",
      description: "Convert court hearings and legal recordings to text with speaker diarization",
    },
    {
      icon: Shield,
      title: "Constitutional Analysis",
      description: "AI-powered analysis of Indian Constitution articles and legal precedents",
    },
    {
      icon: CheckCircle2,
      title: "Entity Extraction",
      description: "Automatically identify parties, dates, citations, and 10+ entity types",
    },
  ];

  const stats = [
    { value: "High", label: "OCR Accuracy" },
    { value: "22+", label: "Languages" },
    { value: "10+", label: "Entity Types" },
    { value: "Fast", label: "Processing Time" },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-legal-navy via-primary to-legal-gold/20">
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-10"></div>
        <div className="container relative mx-auto px-4 py-24 md:py-32">
          <div className="max-w-4xl mx-auto text-center space-y-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-legal-gold-light border border-legal-gold/30">
              <Scale className="h-4 w-4 text-legal-gold" />
              <span className="text-sm font-medium text-foreground">Indian Legal Document AI Processing</span>
            </div>

            <h1 className="text-4xl md:text-6xl font-bold text-white leading-tight">
              Transform Legal Documents with{" "}
              <span className="text-legal-gold">AI-Powered Intelligence</span>
            </h1>

            <p className="text-lg md:text-xl text-white/90 max-w-2xl mx-auto">
              Professional AI platform for OCR, summarization, translation, and constitutional analysis 
              of Indian legal documents. Built for legal professionals, by legal tech experts.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/auth">
                <Button size="lg" className="bg-legal-gold hover:bg-legal-gold/90 text-legal-navy font-semibold">
                  Get Started Free
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Link to="/auth">
                <Button size="lg" variant="outline" className="bg-white/10 hover:bg-white/20 text-white border-white/30">
                  View Demo
                </Button>
              </Link>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 pt-12">
              {stats.map((stat, idx) => (
                <div key={idx} className="text-center">
                  <div className="text-3xl md:text-4xl font-bold text-legal-gold mb-2">
                    {stat.value}
                  </div>
                  <div className="text-sm text-white/80">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-background">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Comprehensive Legal AI Suite
            </h2>
            <p className="text-lg text-muted-foreground">
              Everything you need to process, analyze, and understand Indian legal documents
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, idx) => (
              <Card key={idx} className="group hover:shadow-xl transition-all duration-300 hover:border-legal-gold/50">
                <CardHeader>
                  <div className="mb-4 p-3 bg-legal-gold-light rounded-lg w-fit group-hover:bg-legal-gold/20 transition-colors">
                    <feature.icon className="h-6 w-6 text-legal-gold" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                  <CardDescription className="text-base">
                    {feature.description}
                  </CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-br from-legal-navy to-primary">
        <div className="container mx-auto px-4 text-center">
          <div className="max-w-3xl mx-auto space-y-8">
            <h2 className="text-3xl md:text-4xl font-bold text-white">
              Ready to Transform Your Legal Workflow?
            </h2>
            <p className="text-lg text-white/90">
              Join legal professionals across India using AI to process documents faster and smarter
            </p>
            <Link to="/auth">
              <Button size="lg" className="bg-legal-gold hover:bg-legal-gold/90 text-legal-navy font-semibold">
                Start Processing Documents
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-12 bg-muted/30">
        <div className="container mx-auto px-4 text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Scale className="h-6 w-6 text-legal-gold" />
            <span className="text-lg font-bold">Dharma Lens</span>
          </div>
          <p className="text-sm text-muted-foreground">
            © 2026 Dharma Lens Platform. All rights reserved. | Built for Indian Legal Professionals
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
