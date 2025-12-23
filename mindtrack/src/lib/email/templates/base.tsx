/**
 * Base email template component
 * Provides consistent styling and layout
 */

import React from "react";

export interface BaseEmailTemplateProps {
  title: string;
  content: React.ReactNode;
  footer?: React.ReactNode;
  buttonText?: string;
  buttonLink?: string;
}

export function BaseEmailTemplate({
  title,
  content,
  footer,
  buttonText,
  buttonLink,
}: BaseEmailTemplateProps): string {
  return `
<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title}</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      line-height: 1.6;
      color: #333;
      max-width: 600px;
      margin: 0 auto;
      padding: 20px;
      background-color: #f5f5f5;
    }
    .container {
      background-color: #ffffff;
      border-radius: 8px;
      padding: 30px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .header {
      text-align: center;
      margin-bottom: 30px;
      padding-bottom: 20px;
      border-bottom: 2px solid #e0e0e0;
    }
    .logo {
      font-size: 24px;
      font-weight: bold;
      color: #4f46e5;
      margin-bottom: 10px;
    }
    .title {
      font-size: 20px;
      font-weight: 600;
      color: #1f2937;
      margin: 0;
    }
    .content {
      margin-bottom: 30px;
    }
    .button {
      display: inline-block;
      padding: 12px 24px;
      background-color: #4f46e5;
      color: #ffffff;
      text-decoration: none;
      border-radius: 6px;
      font-weight: 500;
      margin: 20px 0;
    }
    .button:hover {
      background-color: #4338ca;
    }
    .footer {
      margin-top: 30px;
      padding-top: 20px;
      border-top: 1px solid #e0e0e0;
      font-size: 12px;
      color: #6b7280;
      text-align: center;
    }
    .footer a {
      color: #4f46e5;
      text-decoration: none;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="logo">🧠 MindTrack</div>
      <h1 class="title">${title}</h1>
    </div>
    
    <div class="content">
      ${typeof content === "string" ? content : ""}
    </div>
    
    ${buttonText && buttonLink ? `
      <div style="text-align: center;">
        <a href="${buttonLink}" class="button">${buttonText}</a>
      </div>
    ` : ""}
    
    <div class="footer">
      ${footer || `
        <p>Bu email MindTrack tarafından gönderilmiştir.</p>
        <p>
          <a href="https://mindtrack.app">MindTrack</a> | 
          <a href="https://mindtrack.app/privacy">Gizlilik Politikası</a>
        </p>
      `}
    </div>
  </div>
</body>
</html>
  `.trim();
}





