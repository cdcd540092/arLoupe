import { GoogleGenerativeAI } from "@google/generative-ai";

// Use the environment variable set in vite.config.js (define: 'process.env.GEMINI_API_KEY')
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

export const verifyHIPAACompliance = async (imageData) => {
    const prompt = "Please check if the following medical image data or metadata contains any PHI (Protected Health Information) that violates HIPAA compliance rules. Return a clear assessment of compliance.";
    try {
        const result = await model.generateContent([prompt, imageData]);
        const response = await result.response;
        return response.text();
    } catch (error) {
        console.error("AI Compliance Check Error:", error);
        return "Error performing compliance check.";
    }
};

export const getImages = () => {
    return Promise.resolve({
        data: [
            { id: 1, name: 'CT_Scan_A_Head.dicom', status: 'Verified', time: '2026-04-07 10:00' },
            { id: 2, name: 'MRI_Scan_Spine.dicom', status: 'Pending', time: '2026-04-07 11:15' },
            { id: 3, name: 'XRAY_Chest_Normal.dicom', status: 'Verified', time: '2026-04-07 12:30' }
        ]
    });
};

export default {
    verifyHIPAACompliance,
    getImages
};
