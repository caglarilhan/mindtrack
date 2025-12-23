"use client";

import * as React from "react";
import { compareVersions, type SOAPVersion } from "@/lib/ai/soap-versioning";

interface VersionComparisonProps {
  version1: SOAPVersion;
  version2: SOAPVersion;
  onClose: () => void;
}

export function VersionComparison({ version1, version2, onClose }: VersionComparisonProps) {
  const comparison = compareVersions(version1, version2);

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">
            Versiyon Karşılaştırması: v{version1.version} vs v{version2.version}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>

        <div className="space-y-4">
          {/* Subjective */}
          <div className="border rounded p-4">
            <h4 className="font-semibold mb-2">
              Subjective (S)
              {comparison.subjective.changed && (
                <span className="ml-2 text-xs text-orange-600">● Değişti</span>
              )}
            </h4>
            {comparison.subjective.changed ? (
              <div className="space-y-2">
                <div className="p-2 bg-red-50 rounded">
                  <div className="text-xs text-red-600 mb-1">v{version1.version} (Eski):</div>
                  <div className="text-sm">{version1.soap_data.subjective}</div>
                </div>
                <div className="p-2 bg-green-50 rounded">
                  <div className="text-xs text-green-600 mb-1">v{version2.version} (Yeni):</div>
                  <div className="text-sm">{version2.soap_data.subjective}</div>
                </div>
                <div className="p-2 bg-gray-50 rounded text-xs">
                  <strong>Değişiklikler:</strong>
                  <pre className="mt-1 whitespace-pre-wrap">{comparison.subjective.diff}</pre>
                </div>
              </div>
            ) : (
              <div className="text-sm text-gray-600">Değişiklik yok</div>
            )}
          </div>

          {/* Objective */}
          <div className="border rounded p-4">
            <h4 className="font-semibold mb-2">
              Objective (O)
              {comparison.objective.changed && (
                <span className="ml-2 text-xs text-orange-600">● Değişti</span>
              )}
            </h4>
            {comparison.objective.changed ? (
              <div className="space-y-2">
                <div className="p-2 bg-red-50 rounded">
                  <div className="text-xs text-red-600 mb-1">v{version1.version} (Eski):</div>
                  <div className="text-sm">{version1.soap_data.objective}</div>
                </div>
                <div className="p-2 bg-green-50 rounded">
                  <div className="text-xs text-green-600 mb-1">v{version2.version} (Yeni):</div>
                  <div className="text-sm">{version2.soap_data.objective}</div>
                </div>
                <div className="p-2 bg-gray-50 rounded text-xs">
                  <strong>Değişiklikler:</strong>
                  <pre className="mt-1 whitespace-pre-wrap">{comparison.objective.diff}</pre>
                </div>
              </div>
            ) : (
              <div className="text-sm text-gray-600">Değişiklik yok</div>
            )}
          </div>

          {/* Assessment */}
          <div className="border rounded p-4">
            <h4 className="font-semibold mb-2">
              Assessment (A)
              {comparison.assessment.changed && (
                <span className="ml-2 text-xs text-orange-600">● Değişti</span>
              )}
            </h4>
            {comparison.assessment.changed ? (
              <div className="space-y-2">
                <div className="p-2 bg-red-50 rounded">
                  <div className="text-xs text-red-600 mb-1">v{version1.version} (Eski):</div>
                  <div className="text-sm">{version1.soap_data.assessment}</div>
                </div>
                <div className="p-2 bg-green-50 rounded">
                  <div className="text-xs text-green-600 mb-1">v{version2.version} (Yeni):</div>
                  <div className="text-sm">{version2.soap_data.assessment}</div>
                </div>
                <div className="p-2 bg-gray-50 rounded text-xs">
                  <strong>Değişiklikler:</strong>
                  <pre className="mt-1 whitespace-pre-wrap">{comparison.assessment.diff}</pre>
                </div>
              </div>
            ) : (
              <div className="text-sm text-gray-600">Değişiklik yok</div>
            )}
          </div>

          {/* Plan */}
          <div className="border rounded p-4">
            <h4 className="font-semibold mb-2">
              Plan (P)
              {comparison.plan.changed && (
                <span className="ml-2 text-xs text-orange-600">● Değişti</span>
              )}
            </h4>
            {comparison.plan.changed ? (
              <div className="space-y-2">
                <div className="p-2 bg-red-50 rounded">
                  <div className="text-xs text-red-600 mb-1">v{version1.version} (Eski):</div>
                  <div className="text-sm">{version1.soap_data.plan}</div>
                </div>
                <div className="p-2 bg-green-50 rounded">
                  <div className="text-xs text-green-600 mb-1">v{version2.version} (Yeni):</div>
                  <div className="text-sm">{version2.soap_data.plan}</div>
                </div>
                <div className="p-2 bg-gray-50 rounded text-xs">
                  <strong>Değişiklikler:</strong>
                  <pre className="mt-1 whitespace-pre-wrap">{comparison.plan.diff}</pre>
                </div>
              </div>
            ) : (
              <div className="text-sm text-gray-600">Değişiklik yok</div>
            )}
          </div>
        </div>

        <div className="mt-4 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Kapat
          </button>
        </div>
      </div>
    </div>
  );
}





