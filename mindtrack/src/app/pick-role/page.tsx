"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Brain, Heart, Users, Settings } from "lucide-react";

const specialties = [
  {
    id: "psychiatrist",
    name: "Psikiyatrist",
    description: "Tıp doktoru - ilaç tedavisi ve tanı",
    icon: Brain,
    color: "text-purple-600",
    bgColor: "bg-purple-50",
    borderColor: "border-purple-200"
  },
  {
    id: "psychologist",
    name: "Psikolog",
    description: "Psikoterapi ve danışmanlık",
    icon: Heart,
    color: "text-blue-600",
    bgColor: "bg-blue-50",
    borderColor: "border-blue-200"
  },
  {
    id: "client",
    name: "Danışan",
    description: "Tedavi alan hasta/danışan",
    icon: Users,
    color: "text-green-600",
    bgColor: "bg-green-50",
    borderColor: "border-green-200"
  },
  {
    id: "social-worker",
    name: "Sosyal Hizmet Uzmanı",
    description: "Sosyal destek, vaka yönetimi ve koordinasyon",
    icon: Users,
    color: "text-orange-600",
    bgColor: "bg-orange-50",
    borderColor: "border-orange-200"
  },
  {
    id: "admin",
    name: "Yönetici",
    description: "Klinik yönetimi ve koordinasyon",
    icon: Settings,
    color: "text-indigo-600",
    bgColor: "bg-indigo-50",
    borderColor: "border-indigo-200"
  }
];

export default function RoleSelectionPage() {
  const [selectedSpecialty, setSelectedSpecialty] = useState<string | null>(null);
  const router = useRouter();

  const handleSpecialtySelect = (specialtyId: string) => {
    setSelectedSpecialty(specialtyId);
    // 2 saniye sonra dashboard'a yönlendir
    setTimeout(() => {
      router.push(`/dashboard?role=${specialtyId}`);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-2">
              <Brain className="h-8 w-8 text-blue-600" />
              <span className="text-2xl font-bold text-gray-900">MindTrack</span>
            </div>
            <Button onClick={() => router.push('/auth/login')} variant="outline" size="sm">
              Geri Dön
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Rolünüzü Seçin</h1>
          <p className="text-gray-600 text-lg">Hangi rol ile sisteme giriş yapıyorsunuz? Size özel dashboard'u görüntülemek için seçin.</p>
        </div>

        {/* Specialty Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {specialties.map((specialty) => {
            const IconComponent = specialty.icon;
            return (
              <Card
                key={specialty.id}
                className={`cursor-pointer hover:shadow-lg transition-shadow ${selectedSpecialty === specialty.id ? specialty.borderColor + ' border-2' : ''}`}
                onClick={() => handleSpecialtySelect(specialty.id)}
              >
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-lg font-semibold">{specialty.name}</CardTitle>
                  <IconComponent className={`h-6 w-6 ${specialty.color}`} />
                </CardHeader>
                <CardContent>
                  <CardDescription>{specialty.description}</CardDescription>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Info */}
        <div className="mt-12 text-center">
          <p className="text-gray-500 text-sm">
            Her rol için özelleştirilmiş dashboard ve araçlar mevcuttur.
          </p>
        </div>
      </main>
    </div>
  );
}
