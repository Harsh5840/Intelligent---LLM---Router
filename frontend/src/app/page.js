import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import Architecture from "@/components/Architecture";
import Playground from "@/components/Playground";
import Models from "@/components/Models";
import Metrics from "@/components/Metrics";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <Architecture />
        <Playground />
        <Models />
        <Metrics />
      </main>
      <Footer />
    </>
  );
}
