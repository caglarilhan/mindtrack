"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";

const MOCK_CONTACTS = [
  {
    id: "1",
    name: "Dr. Jane Smith",
    specialty: "Child & Adolescent Psychiatry",
    region: "us" as const,
    country: "US",
    city: "New York",
    acceptsInsurance: true,
  },
  {
    id: "2",
    name: "Dr. Anna Müller",
    specialty: "Trauma-focused CBT",
    region: "eu" as const,
    country: "DE",
    city: "Berlin",
    acceptsInsurance: false,
  },
];

export default function ReferralClient() {
  const [region, setRegion] = useState<string>("us");
  const [search, setSearch] = useState("");
  const [open, setOpen] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const filtered = MOCK_CONTACTS.filter(
    (c) => c.region === region && (!search || c.name.toLowerCase().includes(search.toLowerCase()) || c.specialty.toLowerCase().includes(search.toLowerCase())),
  );

  const openReferral = (id: string) => {
    setSelectedId(id);
    setOpen(true);
  };

  const selected = MOCK_CONTACTS.find((c) => c.id === selectedId) || null;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-3 items-center">
        <Input
          placeholder="Provider ara (isim / uzmanlık)"
          className="w-full md:w-64"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <Select value={region} onValueChange={setRegion}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Region" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="us">US</SelectItem>
            <SelectItem value="eu">EU</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filtered.map((c) => (
          <Card key={c.id} className="flex flex-col justify-between">
            <CardHeader>
              <CardTitle className="flex items-center justify-between gap-2 text-base">
                <span>{c.name}</span>
                <Badge variant="outline">{c.region.toUpperCase()}</Badge>
              </CardTitle>
              <CardDescription>{c.specialty}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="text-xs text-muted-foreground">
                {c.city}, {c.country}
              </p>
              <Badge variant={c.acceptsInsurance ? "default" : "secondary"} className="text-xs">
                {c.acceptsInsurance ? "Accepts insurance" : "Private pay"}
              </Badge>
              <div className="pt-3">
                <Button size="sm" className="w-full" onClick={() => openReferral(c.id)}>
                  Create referral
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
        {filtered.length === 0 && <p className="text-sm text-muted-foreground">Seçilen bölge için provider bulunamadı.</p>}
      </div>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>New Referral</DialogTitle>
            <DialogDescription>
              Bu form demo amaçlıdır, gerçek referral API'si sonraki sprinte bırakılmıştır.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3 text-sm">
            <p>To: {selected?.name}</p>
            <Textarea placeholder="Reason / clinical question (min necessary)" rows={4} />
            <Button className="w-full" disabled>
              Save (mock)
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
