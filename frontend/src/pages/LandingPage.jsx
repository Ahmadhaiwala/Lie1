import Hero from "../sections/Hero";
import Services from "../sections/Services";
import HowItWorks from "../sections/HowItWorks";
import Stats from "../sections/Stats";
import Contact from "../sections/Contact";

export default function LandingPage() {
  return (
    <>
      <Hero />
      <Stats />
      <Services />
      <HowItWorks />
      <Contact />
    </>
  );
}
