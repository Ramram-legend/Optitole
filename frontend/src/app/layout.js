import "./globals.css";

export const metadata = {
  title: "SNETH — Module Nesting | Optimisation Découpe Laser & Plasma",
  description:
    "Application d'imbrication optimale pour la découpe laser et plasma de tôles métalliques. Maximisez le taux d'utilisation matière et générez des fichiers DXF pour machines CNC.",
  keywords: [
    "nesting",
    "imbrication",
    "découpe laser",
    "découpe plasma",
    "tôle",
    "DXF",
    "CNC",
    "SNETH",
    "optimisation",
  ],
};

export default function RootLayout({ children }) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  );
}
