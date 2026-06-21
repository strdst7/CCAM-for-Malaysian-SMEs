/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { GoogleGenAI } from "@google/genai";

const client = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

export async function parseWhatsAppMessage(message: string) {
  const prompt = `
    You are a parsing engine for a Malaysian F&B order automation system called CCAM.
    Extract order details from the following WhatsApp message. 
    The output must be JSON.
    If details are missing, provide best guesses or null.
     Malaysian context: Nasi Lemak, Teh Tarik, RM, etc. are common.
    
    Message: "${message}"

    JSON Schema:
    {
      "customer_name": string | null,
      "items": [{ "name": string, "qty": number }],
      "delivery_address": string | null,
      "pickup_time": string | null (ISO 8601),
      "payment_method": "COD" | "DuitNow" | null,
      "confidence": number (0.0 to 1.0)
    }
  `;

  try {
    const response = await client.models.generateContent({
      model: "gemini-1.5-flash",
      contents: [{ role: "user", parts: [{ text: prompt }] }],
    });
    
    const text = response.text || "";
    // Extract JSON from potential markdown markers
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }
    throw new Error("Failed to parse AI response as JSON");
  } catch (error) {
    console.error("Gemini Parsing Error:", error);
    return {
      customer_name: null,
      items: [],
      delivery_address: null,
      pickup_time: null,
      payment_method: null,
      confidence: 0
    };
  }
}
