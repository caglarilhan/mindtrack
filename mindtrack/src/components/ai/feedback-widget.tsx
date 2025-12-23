"use client";

import * as React from "react";
import { ThumbsUp, ThumbsDown, MessageSquare, Send, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/components/ui/toast";

interface FeedbackWidgetProps {
  soapId?: string;
  sessionId?: string;
  onFeedbackSubmitted?: () => void;
}

export const FeedbackWidget = React.memo(function FeedbackWidget({ soapId, sessionId, onFeedbackSubmitted }: FeedbackWidgetProps) {
  const [rating, setRating] = React.useState<number | null>(null);
  const [feedback, setFeedback] = React.useState("");
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [showFeedbackForm, setShowFeedbackForm] = React.useState(false);
  const { toast } = useToast();

  const handleRating = async (value: number) => {
    setRating(value);
    setShowFeedbackForm(true);

    // Auto-submit if rating is high (4-5)
    if (value >= 4) {
      try {
        setIsSubmitting(true);
        await submitFeedback(value, "");
        toast({
          title: "Teşekkürler!",
          description: "Geri bildiriminiz kaydedildi.",
          variant: "success",
        });
        setShowFeedbackForm(false);
        onFeedbackSubmitted?.();
      } catch (error) {
        console.error("Feedback submission error:", error);
      } finally {
        setIsSubmitting(false);
      }
    }
  };

  const submitFeedback = async (ratingValue: number, feedbackText: string) => {
    const response = await fetch("/api/ai/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        soapId,
        sessionId,
        rating: ratingValue,
        feedback: feedbackText,
        timestamp: new Date().toISOString(),
      }),
    });

    if (!response.ok) {
      throw new Error("Feedback submission failed");
    }

    return response.json();
  };

  const handleSubmit = async () => {
    if (!rating) return;

    try {
      setIsSubmitting(true);
      await submitFeedback(rating, feedback);
      toast({
        title: "Teşekkürler!",
        description: "Geri bildiriminiz kaydedildi.",
        variant: "success",
      });
      setRating(null);
      setFeedback("");
      setShowFeedbackForm(false);
      onFeedbackSubmitted?.();
    } catch (error) {
      console.error("Feedback submission error:", error);
      toast({
        title: "Hata",
        description: "Geri bildirim gönderilemedi. Lütfen tekrar deneyin.",
        variant: "error",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!showFeedbackForm && rating === null) {
    return (
      <Card className="border-dashed">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm">Bu SOAP notu size yardımcı oldu mu?</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleRating(5)}
              className="flex-1"
            >
              <ThumbsUp className="h-4 w-4 mr-1" />
              Evet
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleRating(1)}
              className="flex-1"
            >
              <ThumbsDown className="h-4 w-4 mr-1" />
              Hayır
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (showFeedbackForm) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-sm flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            Geri Bildirim
          </CardTitle>
          <CardDescription>
            {rating !== null && (
              <div className="flex items-center gap-1 mt-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Star
                    key={star}
                    className={`h-4 w-4 ${
                      star <= (rating || 0)
                        ? "fill-yellow-400 text-yellow-400"
                        : "text-gray-300"
                    }`}
                  />
                ))}
              </div>
            )}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="Görüşlerinizi paylaşın... (Opsiyonel)"
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            rows={3}
          />
          <div className="flex gap-2">
            <Button
              onClick={handleSubmit}
              disabled={isSubmitting || !rating}
              className="flex-1"
            >
              <Send className="h-4 w-4 mr-2" />
              Gönder
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setShowFeedbackForm(false);
                setRating(null);
                setFeedback("");
              }}
            >
              İptal
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return null;
});

