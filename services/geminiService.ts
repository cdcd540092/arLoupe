import { GoogleGenAI, Type } from "@google/genai";
import { Language } from "../types";

const getAiClient = () => {
  if (!process.env.API_KEY) {
    throw new Error("API_KEY not found in environment variables");
  }
  return new GoogleGenAI({ apiKey: process.env.API_KEY });
};

export const analyzeCompliance = async (systemConfig: string, language: Language = 'en') => {
  try {
    const ai = getAiClient();
    const langInstruction = language === 'zh-TW' 
      ? "Respond in Traditional Chinese (Taiwan). Ensure the fields 'item', 'details', 'recommendation', and 'summary' are in Traditional Chinese." 
      : "Respond in English.";

    const prompt = `
      You are a HIPAA Compliance Officer. Analyze the following system configuration or log summary and identify potential compliance violations or security risks.
      
      System Configuration/Context:
      ${systemConfig}

      ${langInstruction}
      Return a JSON response listing specific compliance checks.
    `;

    const response = await ai.models.generateContent({
      model: "gemini-3-flash-preview",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            checks: {
              type: Type.ARRAY,
              items: {
                type: Type.OBJECT,
                properties: {
                  item: { type: Type.STRING, description: "The specific compliance rule or area checked" },
                  status: { type: Type.STRING, enum: ["Pass", "Fail", "Warning"] },
                  details: { type: Type.STRING, description: "Explanation of findings" },
                  recommendation: { type: Type.STRING, description: "How to fix the issue if failed" }
                },
                required: ["item", "status", "details"]
              }
            },
            summary: { type: Type.STRING, description: "A high-level executive summary of the compliance status" }
          }
        }
      }
    });

    return JSON.parse(response.text || "{}");
  } catch (error) {
    console.error("Compliance check failed:", error);
    throw error;
  }
};
