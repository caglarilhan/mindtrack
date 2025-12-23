"use client";

import * as React from "react";
import { ChevronDown, ChevronUp, Copy, Edit2 } from "lucide-react";

// Memoized component for better performance

interface SOAPDisplayProps {
  soap: {
    subjective: string;
    objective: string;
    assessment: string;
    plan: string;
  };
  onEdit?: (section: 'subjective' | 'objective' | 'assessment' | 'plan') => void;
  onCopy?: (section: string, content: string) => void;
  collapsible?: boolean;
}

export const SOAPDisplay = React.memo(function SOAPDisplay({ soap, onEdit, onCopy, collapsible = true }: SOAPDisplayProps) {
  const [expandedSections, setExpandedSections] = React.useState<Set<string>>(
    new Set(['subjective', 'objective', 'assessment', 'plan'])
  );

  const toggleSection = (section: string) => {
    if (!collapsible) return;
    
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const SectionCard = ({
    title,
    icon,
    content,
    sectionKey,
    bgColor,
    borderColor,
  }: {
    title: string;
    icon: string;
    content: string;
    sectionKey: string;
    bgColor: string;
    borderColor: string;
  }) => {
    const isExpanded = expandedSections.has(sectionKey);
    const section = sectionKey as 'subjective' | 'objective' | 'assessment' | 'plan';

    return (
      <div className={`rounded-lg border-2 ${borderColor} ${bgColor} overflow-hidden transition-all duration-200`}>
        <div
          className={`flex items-center justify-between p-4 cursor-pointer ${collapsible ? 'hover:bg-opacity-80' : ''}`}
          onClick={() => toggleSection(sectionKey)}
        >
          <div className="flex items-center gap-3">
            <span className="text-2xl">{icon}</span>
            <h3 className="font-semibold text-lg">{title}</h3>
          </div>
          <div className="flex items-center gap-2">
            {onCopy && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  navigator.clipboard.writeText(content);
                  onCopy(section, content);
                }}
                className="p-1 hover:bg-white/20 rounded transition-colors"
                title="Kopyala"
              >
                <Copy className="h-4 w-4" />
              </button>
            )}
            {onEdit && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onEdit(section);
                }}
                className="p-1 hover:bg-white/20 rounded transition-colors"
                title="Düzenle"
              >
                <Edit2 className="h-4 w-4" />
              </button>
            )}
            {collapsible && (
              <button className="p-1 hover:bg-white/20 rounded transition-colors">
                {isExpanded ? (
                  <ChevronUp className="h-5 w-5" />
                ) : (
                  <ChevronDown className="h-5 w-5" />
                )}
              </button>
            )}
          </div>
        </div>
        {isExpanded && (
          <div className="px-4 pb-4">
            <div className="bg-white/50 rounded p-3 text-sm whitespace-pre-wrap">
              {content || '(Boş)'}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-4">
      <SectionCard
        title="Subjective (Öznel)"
        icon="📝"
        content={soap.subjective}
        sectionKey="subjective"
        bgColor="bg-blue-50"
        borderColor="border-blue-300"
      />
      <SectionCard
        title="Objective (Nesnel)"
        icon="👁️"
        content={soap.objective}
        sectionKey="objective"
        bgColor="bg-green-50"
        borderColor="border-green-300"
      />
      <SectionCard
        title="Assessment (Değerlendirme)"
        icon="🔍"
        content={soap.assessment}
        sectionKey="assessment"
        bgColor="bg-yellow-50"
        borderColor="border-yellow-300"
      />
      <SectionCard
        title="Plan (Plan)"
        icon="📋"
        content={soap.plan}
        sectionKey="plan"
        bgColor="bg-purple-50"
        borderColor="border-purple-300"
      />
    </div>
  );
}, (prevProps, nextProps) => {
  // Custom comparison for memo
  return (
    prevProps.soap.subjective === nextProps.soap.subjective &&
    prevProps.soap.objective === nextProps.soap.objective &&
    prevProps.soap.assessment === nextProps.soap.assessment &&
    prevProps.soap.plan === nextProps.soap.plan &&
    prevProps.collapsible === nextProps.collapsible
  );
});

