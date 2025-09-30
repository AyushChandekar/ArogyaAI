interface ExampleQueriesProps {
  onSelectQuery: (query: string) => void;
}

const exampleQueries = [
  {
    icon: "📋",
    category: "General",
    query: "Tell me about asthma",
    description: "General information"
  },
  {
    icon: "🏠",
    category: "Home Treatment",
    query: "Home treatment for baldness",
    description: "Natural remedies"
  },
  {
    icon: "🔍",
    category: "Causes",
    query: "What causes acne?",
    description: "Understanding causes"
  },
  {
    icon: "⚠️",
    category: "Symptoms",
    query: "रेबीज़ के लक्षण क्या हैं?",
    description: "Symptom identification"
  },
  {
    icon: "🌍",
    category: "Spanish",
    query: "¿Cuáles son los síntomas de la diabetes?",
    description: "Multilingual support"
  },
  {
    icon: "🌏",
    category: "Odia",
    query: "ମୂତ୍ରନଳୀ ସଂକ୍ରମଣ (UTI) ର କାରଣ କଣ?",
    description: "what are the causes for Urinary Tract Infection (UTI)"
  }
];

export default function ExampleQueries({ onSelectQuery }: ExampleQueriesProps) {
  return (
    <div>
      <h3 className="text-lg font-medium text-gray-700 dark:text-gray-200 mb-4 text-center darkkk">
        💡 Try these examples:
      </h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {exampleQueries.map((example, index) => (
          <button
            key={index}
            onClick={() => onSelectQuery(example.query)}
            className="p-3 text-left bg-blue-50 dark:bg-gray-700 hover:bg-blue-100 dark:hover:bg-gray-600 rounded-lg border border-blue-200 dark:border-gray-600 transition-all duration-200 hover:shadow-md group clickable"
          >
            <div className="flex items-start gap-3">
              <span className="text-2xl group-hover:scale-110 transition-transform">
                {example.icon}
              </span>
              <div>
                <div className="text-sm font-medium text-blue-600 dark:text-blue-400 mb-1 colordark">
                  {example.query}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400 description">
                  {example.description}
                </div>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
