import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/ui/card';
import { Scale, FileText, Briefcase, HelpCircle } from 'lucide-react';

const infoCards = [
  {
    title: 'Document Types',
    icon: FileText,
    items: [
      'Non-Disclosure Agreements (NDA)',
      'Employment Contracts',
      'Customizable clauses',
      'Legal compliance',
    ],
  },
  {
    title: 'How It Works',
    icon: HelpCircle,
    items: [
      'Answer a few questions',
      'AI collects requirements',
      'Document is generated',
      'Review and revise',
    ],
  },
  {
    title: 'What You\'ll Need',
    icon: Briefcase,
    items: [
      'Party names and details',
      'Specific terms required',
      'Duration preferences',
      'Special clauses (optional)',
    ],
  },
];

export function WelcomeScreen() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8">
      {/* Logo and Header */}
      <div className="text-center mb-8">
        <div className="inline-flex p-4 bg-gradient-to-br from-purple-700 to-indigo-800 rounded-2xl mb-4">
          <Scale className="h-12 w-12 text-white" />
        </div>
        <h1 className="text-3xl font-bold text-foreground mb-2">
          Legal Document Generator
        </h1>
        <p className="text-muted-foreground max-w-md mx-auto">
          Get instant, professionally drafted legal documents through a simple conversation with our AI-powered assistant.
        </p>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-4xl">
        {infoCards.map((card) => (
          <Card key={card.title} className="bg-card hover:shadow-md transition-shadow">
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2">
                <card.icon className="h-5 w-5 text-purple-700" />
                {card.title}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {card.items.map((item) => (
                  <li key={item} className="text-sm text-muted-foreground flex items-start gap-2">
                    <span className="text-purple-700 mt-1">•</span>
                    {item}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Example Prompts */}
      <div className="mt-8 text-center">
        <p className="text-sm text-muted-foreground mb-3">Try saying:</p>
        <div className="flex flex-wrap justify-center gap-2">
          {[
            'I need an NDA for my startup',
            'Create an employment contract',
            'Help me draft a confidentiality agreement',
          ].map((prompt) => (
            <span
              key={prompt}
              className="px-3 py-1.5 text-sm bg-muted rounded-full text-muted-foreground"
            >
              "{prompt}"
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
