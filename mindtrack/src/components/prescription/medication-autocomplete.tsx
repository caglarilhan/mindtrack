"use client";

import * as React from "react";
import { useTranslations } from "next-intl";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Pill, Search, AlertTriangle, CheckCircle, X } from "lucide-react";
import { type PrescriptionRegion, getControlledSubstanceInfo } from "@/lib/prescription-region";
import { 
  searchMedication, 
  getMedicationName, 
  getMedicationDosages,
  getMedicationSideEffects,
  type Medication
} from "@/lib/medication-database";

interface Medication {
  id: string;
  name: string;
  genericName: string;
  brandName?: string;
  dosageForms: string[];
  strengths: string[];
  category: string;
  schedule?: string; // US: Schedule I-V, EU: Category
  requiresPrescription: boolean;
}

// Medication interface - Bölgeye özel ilaç veritabanından gelecek
interface MedicationAutocompleteItem {
  id: string;
  name: string;
  genericName: string;
  brandName?: string;
  dosageForms: string[];
  strengths: string[];
  category: string;
  schedule?: string;
  requiresPrescription: boolean;
}

interface MedicationAutocompleteProps {
  value: string;
  onChange: (medication: Medication | null) => void;
  region: PrescriptionRegion;
  placeholder?: string;
  className?: string;
}

export default function MedicationAutocomplete({
  value,
  onChange,
  region,
  placeholder = "İlaç adı, jenerik ad veya marka adı ile ara...",
  className
}: MedicationAutocompleteProps) {
  const t = useTranslations("prescription");
  const [searchTerm, setSearchTerm] = React.useState(value);
  const [suggestions, setSuggestions] = React.useState<Medication[]>([]);
  const [selectedMedication, setSelectedMedication] = React.useState<MedicationAutocompleteItem | null>(null);
  const [showSuggestions, setShowSuggestions] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(false);
  const inputRef = React.useRef<HTMLInputElement>(null);

  React.useEffect(() => {
    if (searchTerm.length >= 2) {
      setIsLoading(true);
      // Bölgeye özel ilaç arama
      const timer = setTimeout(() => {
        const foundMedications = searchMedication(searchTerm, region);
        const mapped: MedicationAutocompleteItem[] = foundMedications.map(med => ({
          id: med.id,
          name: getMedicationName(med, region),
          genericName: med.genericName,
          brandName: med.brandName,
          dosageForms: med.dosageForms,
          strengths: getMedicationDosages(med, region),
          category: med.category,
          schedule: med.schedule,
          requiresPrescription: med.requiresPrescription
        }));
        setSuggestions(mapped.slice(0, 5));
        setShowSuggestions(true);
        setIsLoading(false);
      }, 200);

      return () => clearTimeout(timer);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [searchTerm, region]);

  const handleSelect = (medication: MedicationAutocompleteItem) => {
    setSelectedMedication(medication);
    setSearchTerm(medication.name);
    setShowSuggestions(false);
    onChange(medication);
  };

  const handleClear = () => {
    setSearchTerm('');
    setSelectedMedication(null);
    setSuggestions([]);
    setShowSuggestions(false);
    onChange(null);
    inputRef.current?.focus();
  };

  const getScheduleBadge = (medication: Medication) => {
    if (!medication.schedule) return null;
    
    const substanceInfo = getControlledSubstanceInfo(region, medication.name);
    if (!substanceInfo) return null;

    if (region === 'us') {
      const scheduleColors: Record<string, string> = {
        'I': 'bg-red-100 text-red-800',
        'II': 'bg-orange-100 text-orange-800',
        'III': 'bg-yellow-100 text-yellow-800',
        'IV': 'bg-blue-100 text-blue-800',
        'V': 'bg-green-100 text-green-800'
      };
      return (
        <Badge className={scheduleColors[medication.schedule] || 'bg-gray-100 text-gray-800'}>
          Schedule {medication.schedule}
        </Badge>
      );
    } else {
      return (
        <Badge variant="outline" className="bg-purple-50 text-purple-800">
          Kontrollü İlaç
        </Badge>
      );
    }
  };

  return (
    <div className={`relative ${className}`}>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          ref={inputRef}
          type="text"
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            if (selectedMedication) {
              setSelectedMedication(null);
              onChange(null);
            }
          }}
          onFocus={() => {
            if (suggestions.length > 0) {
              setShowSuggestions(true);
            }
          }}
          placeholder={placeholder}
          className="pl-10 pr-10"
        />
        {searchTerm && (
          <button
            onClick={handleClear}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Öneriler */}
      {showSuggestions && suggestions.length > 0 && (
        <Card className="absolute z-50 w-full mt-1 max-h-80 overflow-y-auto shadow-lg">
          <div className="p-2">
            {suggestions.map((medication) => (
              <button
                key={medication.id}
                onClick={() => handleSelect(medication)}
                className="w-full text-left p-3 hover:bg-gray-50 rounded-lg transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <Pill className="h-4 w-4 text-blue-600" />
                      <span className="font-semibold text-sm">{medication.name}</span>
                      {medication.brandName && (
                        <span className="text-xs text-gray-500">({medication.brandName})</span>
                      )}
                    </div>
                    <div className="text-xs text-gray-600 mb-2">
                      {medication.genericName} • {medication.category}
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {medication.strengths.slice(0, 3).map((strength, idx) => (
                        <Badge key={idx} variant="outline" className="text-xs">
                          {strength}
                        </Badge>
                      ))}
                      {medication.strengths.length > 3 && (
                        <Badge variant="outline" className="text-xs">
                          +{medication.strengths.length - 3} daha
                        </Badge>
                      )}
                    </div>
                  </div>
                  <div className="ml-2">
                    {getScheduleBadge(medication)}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </Card>
      )}

      {/* Seçili İlaç Bilgisi */}
      {selectedMedication && (
        <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span className="font-semibold text-sm">{selectedMedication.name}</span>
                {selectedMedication.brandName && (
                  <span className="text-xs text-gray-600">({selectedMedication.brandName})</span>
                )}
              </div>
              <div className="text-xs text-gray-600">
                {selectedMedication.genericName} • {selectedMedication.category}
              </div>
            </div>
            {getScheduleBadge(selectedMedication)}
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="absolute z-50 w-full mt-1 p-3 bg-white border rounded-lg shadow-lg">
          <div className="text-sm text-gray-600">Aranıyor...</div>
        </div>
      )}

      {/* No Results */}
      {searchTerm.length >= 2 && !isLoading && suggestions.length === 0 && showSuggestions && (
        <Card className="absolute z-50 w-full mt-1 p-3 shadow-lg">
          <div className="text-sm text-gray-600 text-center">
            İlaç bulunamadı. Farklı bir arama terimi deneyin.
          </div>
        </Card>
      )}
    </div>
  );
}

