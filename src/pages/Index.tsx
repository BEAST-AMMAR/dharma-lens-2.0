import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Scale, Brain, Languages, FileText, Mic, Shield, ArrowRight, CheckCircle2, Scroll, BookOpen, Users } from "lucide-react";

const Index = () => {
  const features = [
    {
      icon: Scroll,
      title: "Historical & Ancient Scripts (HTR)",
      description: "Transcribe and transliterate century-old Modi script land records, Halegannada (Old Kannada), and Perso-Arabic Nastaliq revenue deeds into modern standard text.",
    },
    {
      icon: Users,
      title: "Citizen-Friendly Layman Explanation",
      description: "Explains complex property deeds, wills, and court filings in simple plain words for everyday citizens, farmers, and property buyers.",
    },
    {
      icon: BookOpen,
      title: "Archaic Revenue Lexicon",
      description: "Automatically detects and clarifies 250+ historical revenue terms like Khasra, Jamabandi, Bainama, Watandar, Sanad, Inam, and Chauhaddi.",
    },
    {
      icon: Shield,
      title: "BNS & Property Law Intelligence",
      description: "Direct statutory mapping from legacy colonial codes (IPC, CrPC, Evidence Act) to modern laws (BNS, BNSS, BSA) and Transfer of Property Act provisions.",
    },
    {
      icon: Languages,
      title: "22+ Indian Languages Translation",
      description: "Context-aware legal translation into Hindi, Marathi, Kannada, Bengali, Tamil, Telugu, Gujarati, and other official languages.",
    },
    {
      icon: Mic,
      title: "Court Audio Transcription",
      description: "Convert recorded court proceedings, witness statements, and legal conferences to verbatim text using offline speech AI.",
    },
  ];

  const stats = [
    { value: "300+ Yrs", label: "Heritage Deeds Deciphered" },
    { value: "250+", label: "Archaic Terms Cataloged" },
    { value: "22+", label: "Indian Languages" },
    { value: "100%", label: "Privacy & Air-Gap Ready" },
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
              <span className="text-sm font-medium text-foreground">VidhiChakshu (विधि-चक्षु) — The AI Vision for Indian Legal & Heritage Documents</span>
            </div>

            <h1 className="text-4xl md:text-6xl font-bold text-white leading-tight">
              Decipher Centuries of Law with{" "}
              <span className="text-legal-gold">VidhiChakshu AI</span>
            </h1>

            <p className="text-lg md:text-xl text-white/90 max-w-3xl mx-auto leading-relaxed">
              Read, transcribe, transliterate, and understand ancient land deeds, handwritten court files, 
              and historical Indian scripts (Modi, Halegannada, Nastaliq). Empowering common citizens with 
              simple explanations and advocates with statutory precision.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/auth">
                <Button size="lg" className="bg-legal-gold hover:bg-legal-gold/90 text-legal-navy font-semibold">
                  Start Processing Documents
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Link to="/auth">
                <Button size="lg" variant="outline" className="bg-white/10 hover:bg-white/20 text-white border-white/30">
                  Explore Heritage Demo
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
              Comprehensive Heritage & Legal Document Intelligence
            </h2>
            <p className="text-lg text-muted-foreground">
              Bridging historical manuscripts and modern justice for citizens, advocates, and courts
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
              Unlock the Truth in Your Ancient Deeds & Court Records
            </h2>
            <p className="text-lg text-white/90">
              Join citizens, legal practitioners, and archivists across India using VidhiChakshu to decode legal history.
            </p>
            <Link to="/auth">
              <Button size="lg" className="bg-legal-gold hover:bg-legal-gold/90 text-legal-navy font-semibold">
                Launch VidhiChakshu Workspace
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-12 bg-muted/30">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>© 2026 VidhiChakshu (विधि-चक्षु). All rights reserved. Indian Legal & Heritage Document Intelligence.</p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
