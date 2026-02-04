# **Multimodal Virtual Communication System – Minimal Viable Prototype (MVP) Proposal**  
**Author:** Ma Kai Lun Donovan  
**Department of Computing / Information Security**  
**The Hong Kong Polytechnic University**

---

## **1. Project Overview**

This project aims to develop a **minimal viable prototype (MVP)** of a **Multimodal Virtual Communication System** that integrates **Facial Expression Recognition (FER)**, **persona‑aware dialogue generation**, and **expressive text‑to‑speech (TTS)** into a unified real‑time interaction pipeline.

Rather than building full-scale acoustic modeling or personality reconstruction, this MVP focuses on a **feasible, functional, and demonstrable prototype** that showcases:

- Real-time emotion detection from webcam input  
- Emotion‑aware and persona‑conditioned dialogue responses  
- Speech output generated through a lightweight TTS module  
- A simple user interface for multimodal interaction  

This prototype serves as a foundation for future expansion into full multimodal affective computing.

---

## **2. Motivation**

Human communication is inherently multimodal, involving facial expressions, tone, prosody, and conversational style. While many systems model these modalities separately, few demonstrate **real-time integration** in an accessible prototype.

This project addresses that gap by building a **lightweight, real-time multimodal demo** that:

- Reacts to user emotions  
- Adjusts dialogue tone based on persona  
- Produces expressive speech output  
- Runs on consumer hardware  

The goal is not to achieve state-of-the-art performance, but to demonstrate **technical feasibility**, **system integration**, and **human-centered interaction design**.

---

## **3. System Scope (MVP Version)**

This MVP intentionally limits scope to ensure feasibility within one semester.

### **Included in Scope**
1. **Real-Time Facial Expression Recognition (FER)**
   - Based on existing FYP model (MobileNetV3 / ViT student)
   - Outputs: emotion label + confidence
   - Includes temporal smoothing (EMA / voting)

2. **Persona‑Aware Dialogue Module**
   - Uses an LLM (API or local)  
   - Inputs: user text + emotion label + persona profile  
   - Outputs: short, tone-adjusted response  
   - Includes 2–3 predefined personas (e.g., “Supportive Mentor”, “Calm Companion”, “Technical Advisor”)

3. **Expressive Text-to-Speech (TTS)**
   - Uses an existing TTS model/API  
   - Converts generated text into speech  
   - Supports simple style tags (e.g., calm / energetic)

4. **Multimodal Integration Pipeline**
   - Webcam → FER → Dialogue → TTS → Audio playback  
   - Simple UI (OpenCV window / Streamlit / Tkinter)

### **Out of Scope (Future Work)**
- Full personality reconstruction  
- Custom TTS training  
- Voiceprint modeling  
- GAN-based prosody generation  
- Large-scale user studies  
- Ethical deployment frameworks  

---

## **4. System Architecture**

### **Pipeline Overview**

1. **Video Capture**  
   - Webcam stream → face detection (YuNet) → preprocessing (CLAHE)

2. **Emotion Recognition Module**  
   - FER model outputs:  
     - `emotion_label ∈ {happy, sad, neutral, fear, disgust, anger, surprise}`  
     - `confidence score`  
   - Temporal smoothing to reduce flicker

3. **Dialogue Generation Module**  
   - Inputs:  
     - User text  
     - Emotion label  
     - Persona profile  
   - LLM generates a short, contextually appropriate response

4. **Text-to-Speech Module**  
   - Converts LLM output into speech  
   - Optional style conditioning

5. **User Interface**  
   - Left: webcam + emotion label  
   - Right: chat log + audio playback button  

---

## **5. Implementation Plan**

### **Phase 1 – FER Integration (Week 1–2)**
- Refactor existing FYP FER code into a callable module  
- Implement real-time inference loop  
- Add temporal smoothing  
- Build basic UI for emotion display  

### **Phase 2 – TTS Integration (Week 3–4)**
- Select TTS model/API  
- Implement wrapper function:  
  `generate_speech(text, style_tag)`  
- Add audio playback to UI  

### **Phase 3 – Persona & Dialogue Module (Week 5–7)**
- Define 2–3 persona profiles  
- Implement emotion → response strategy mapping  
- Integrate LLM for text generation  
- Combine FER + persona + LLM into unified logic  

### **Phase 4 – System Integration & UI (Week 8–10)**
- Build full pipeline  
- Add chat log + simple controls  
- Test latency and stability  

### **Phase 5 – Evaluation & Documentation (Week 11–12)**
- Record demo video  
- Evaluate:  
  - Latency  
  - Response appropriateness  
  - User-perceived naturalness  
- Write final report  

---

## **6. Expected Deliverables**

1. **A working multimodal prototype** capable of:
   - Real-time emotion detection  
   - Emotion-aware dialogue generation  
   - Persona-conditioned responses  
   - Speech output  

2. **Demo video** showing the system in action

3. **Technical documentation**, including:
   - System architecture  
   - Implementation details  
   - Limitations  
   - Future work  

4. **GitHub repository** with:
   - Source code  
   - Instructions for running the demo  

---

## **7. Significance**

This MVP demonstrates:

- Practical integration of ML, HCI, and real-time systems  
- A foundation for future research in affective computing  
- A portfolio-ready project showcasing multimodal engineering  
- A human-centered approach to AI interaction design  

It also provides a scalable base for future work in:

- Healthcare support  
- Companionship technologies  
- XR-based communication  
- Personalized virtual agents  

---

## **8. Conclusion**

This project delivers a **feasible, technically grounded, and meaningful** multimodal communication prototype. By combining FER, persona-aware dialogue, and expressive TTS, it demonstrates the core principles of affective computing in a compact, real-time system.

The MVP is intentionally scoped to ensure successful completion while laying the groundwork for future expansion into full multimodal virtual communication systems.
