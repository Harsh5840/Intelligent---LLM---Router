import "./globals.css";

export const metadata = {
  title: "Intelligent LLM Router — Live System Demo",
  description:
    "Production-grade decision layer that sits in front of multiple foundation models and chooses the best model per request, optimizing quality, latency, and cost in real-time.",
  keywords: [
    "LLM Router",
    "AI Infrastructure",
    "Model Selection",
    "System Design",
    "FastAPI",
  ],
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
