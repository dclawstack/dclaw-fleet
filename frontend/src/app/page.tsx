import { CopilotSection } from "@/components/landing/copilot-section";
import { CtaSection, LandingFooter } from "@/components/landing/cta-section";
import { DemoSection } from "@/components/landing/demo-section";
import { FeaturesSection } from "@/components/landing/features-section";
import { HeroSection } from "@/components/landing/hero-section";
import { StackSection } from "@/components/landing/stack-section";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-white text-slate-900">
      <HeroSection />
      <FeaturesSection />
      <CopilotSection />
      <StackSection />
      <DemoSection />
      <CtaSection />
      <LandingFooter />
    </main>
  );
}
