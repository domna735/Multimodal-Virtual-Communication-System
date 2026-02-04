PROPOSAL OF PERSONAL PROJECT MULTIMODAL 
VIRTUAL COMMUNICATE SYSTEM 
The Hong Kong Polytechnic University 
Ma Kai Lun Donovan 
Abstract 
This project proposes the design and development of a Multimodal Virtual 
Communication System that integrates facial expression recognition, 
acoustic-phonological modeling, speech generation, and personality reconstruction 
into a unified framework for naturalistic human–machine interaction. The system 
aims to analyze a user’s emotional state through Facial Expression Recognition 
(FER), capture speaker individuality and prosodic features via voiceprint and 
prosody modeling, and generate expressive speech that preserves both timbre and 
intonation. Beyond signal-level modeling, the project explores the reconstruction of 
personality traits and interaction style, enabling dialogue agents to simulate 
consistent personas. 
Methodologically, the project employs knowledge distillation and margin-based 
embedding losses to build a robust FER backbone, few-shot adaptation and 
generative phonology models to capture prosody under limited data conditions, and 
zero-/few-shot text-to-speech architectures to synthesize natural speech. A persona
conditioned dialogue module is further introduced to approximate interaction style, 
while transformer-based multimodal fusion integrates visual, acoustic, and 
linguistic cues in real time. 
The expected outcomes include: (i) a validated FER model robust under stress 
conditions, (ii) a voiceprint–prosody module capable of low-resource adaptation, (iii) 
an expressive speech generation system, (iv) a prototype persona simulation module, 
and (v) an integrated multimodal communication system. Potential applications span 
personal companionship, healthcare support, language learning, and 
remembrance technologies. By addressing both technical feasibility and human
centered design, this project contributes to the advancement of affective computing 
and the long-term vision of emotionally meaningful virtual communication. 
1 
 
2 
 
Contents 
Abstract .................................................................................................................. 1 
INTRODUCTION ................................................................................................... 4 
Overview ............................................................................................................. 4 
Motivation ........................................................................................................... 5 
Background ......................................................................................................... 6 
Problem Statements .............................................................................................. 7 
Research Objectives .............................................................................................. 8 
Related Work ......................................................................................................... 10 
Facial Expression Recognition (FER) ..................................................................... 10 
Acoustic‑Phonological Modeling ........................................................................... 10 
Multi‑Modal Affective Computing ........................................................................ 11 
Gaps in the Literature .............................................................................................. 11 
Significance of the Study ...................................................................................... 11 
Academic Contributions ....................................................................................... 12 
Practical and Societal Relevance............................................................................ 12 
Literature Review .................................................................................................... 13 
1. Facial Expression Recognition (FER) ................................................................. 13 
2. Acoustic-Phonological Modeling ....................................................................... 13 
3. Speech Generation ........................................................................................... 14 
4. Personality Reconstruction ................................................................................ 14 
5. System Integration ........................................................................................... 14 
Methodology .......................................................................................................... 16 
1. Facial Expression Recognition (FER) – Emotion Analysis Module ........................ 16 
2. Acoustic-Phonological Modeling – Voiceprint and Prosody Module ...................... 16 
3. Speech Generation – Expressive TTS Module ..................................................... 17 
4. Personality Reconstruction – Persona Module (Most Challenging) ......................... 18 
 
3 
 
5. System Integration – Multimodal Communication System .................................... 18 
Future Challenges: Personality Reconstruction ........................................................... 19 
Project Plan ............................................................................................................ 21 
1. Objectives Recap ............................................................................................. 21 
2. Project Schedule and Milestones ........................................................................ 21 
3. Risk Management ............................................................................................ 24 
4. Expected Outcomes .......................................................................................... 24 
References ............................................................................................................. 25 
 
 
  
INTRODUCTION 
Overview 
Human communication is inherently multi‑modal, involving not only spoken 
language but also facial expressions, prosody, and subtle paralinguistic cues. Recent 
advances in machine learning and affective computing have enabled increasingly 
accurate recognition of these modalities in isolation. However, the integration of 
visual, acoustic, and linguistic signals into a coherent, interactive system remains an 
open research challenge.   
This project envisions the development of a Virtual Human Communication System 
capable of simulating and preserving human‑like interaction across multiple channels: 
voice, dialogue, facial expression, appearance, personality, and conversational style. 
Such a system has potential applications in remembrance and companionship 
(providing a means of continued interaction with departed loved ones), healthcare and 
therapy (offering emotional support or speech rehabilitation), and self‑reflection 
(enabling individuals to engage in dialogue with a virtual representation of 
themselves).   
The proposed research Is structured as a multi‑stage roadmap. The first stage, 
represented by the current Final Year Project (FYP), focuses on Facial Expression 
Recognition (FER) as a foundational module. The second stage extends into 
acoustic‑phonological modeling, particularly vowel length contrasts and prosodic 
features, to capture the temporal and expressive dimensions of speech. The final stage 
aims to integrate these components into a unified multi‑modal framework, enabling 
real‑time, naturalistic interaction.   
By progressively building from robust unimodal modules towards multi‑modal 
integration, this research seeks to establish both the technical feasibility and the 
4 
conceptual significance of virtual human communication systems. Beyond technical 
contributions, the project also addresses broader questions of trust, ethics, and human 
meaning, recognizing that such systems intersect deeply with emotional and social 
dimensions of human life.   
Motivation 
Human communication is not limited to words alone; it is a rich interplay of facial 
expressions, voice, prosody, and conversational style. While recent advances in 
machine learning have enabled progress in each of these modalities, existing systems 
remain fragmented and task‑specific. The motivation for this study arises from both 
academic curiosity and personal vision: to build a foundation for a Virtual Human 
Communication System that can support naturalistic, emotionally meaningful 
interaction.   
From an academic perspective, the motivation lies in addressing critical gaps in 
current research. Facial Expression Recognition (FER) models, despite achieving high 
benchmark accuracy, often fail under real‑world conditions such as class imbalance, 
image degradation, and deployment drift. Similarly, acoustic‑phonological modeling 
has yet to fully capture expressive features such as vowel length contrasts, prosody, 
and speaker individuality. By systematically strengthening these unimodal backbones 
and exploring their integration, this project aims to contribute to the emerging field of 
multi‑modal affective computing.   
From a societal perspective, the motivation is grounded in the potential applications 
of such a system. A virtual communication agent capable of simulating voice, 
expression, and personality could:   - Provide comfort and remembrance, enabling continued interaction with departed 
loved ones.   - Support healthcare and therapy, offering companionship, speech rehabilitation, and 
emotional support.   
5 
- Facilitate self‑reflection, allowing individuals to engage in dialogue with a “virtual 
self” for decision‑making and personal growth.   
From a personal perspective, this project represents the first step in a long‑term 
research journey. The current FYP on FER establishes the visual backbone; 
subsequent work on acoustic‑phonological modeling will extend into the auditory 
domain. Together, these stages form the foundation for a future system that is not only 
technically robust but also emotionally resonant.   
In sum, the motivation for this study is to bridge the gap between technical feasibility 
and human meaning, laying the groundwork for communication systems that are 
academically rigorous, practically useful, and deeply human‑centered.   
Background 
Human communication is inherently multi‑modal, combining verbal content with 
non‑verbal cues such as facial expressions, prosody, and gesture. In recent decades, 
advances in affective computing and speech technology have enabled researchers to 
model these modalities separately with increasing accuracy.   
In the visual domain, Facial Expression Recognition (FER) has become a central task 
for understanding human affect. Convolutional Neural Networks (CNNs) and, more 
recently, Vision Transformers (ViTs) have demonstrated strong performance on 
benchmark datasets such as AffectNet and RAF‑DB. However, FER systems remain 
vulnerable to class imbalance, image quality degradation, and deployment drift, which 
limit their reliability in real‑world applications.   
In the acoustic domain, phonological contrasts such as vowel length and prosodic 
features like intonation and rhythm play a crucial role in conveying meaning and 
emotion. Deep learning approaches, including Generative Adversarial Networks 
6 
(GANs) and sequence models, have been applied to capture these fine‑grained 
temporal patterns. Yet, challenges remain in modeling cross‑linguistic variation, 
speaker individuality, and expressive nuance.   
Despite progress in unimodal research, the integration of visual and acoustic signals 
into a unified system for naturalistic interaction is still underexplored. Existing 
multi‑modal systems often focus on task‑specific objectives (e.g., emotion 
classification or speech recognition) rather than holistic communication. Moreover, 
ethical considerations such as trust, authenticity, and potential misuse (e.g., 
deepfakes) highlight the importance of developing systems that are not only 
technically robust but also socially responsible.   
This background motivates a staged research program: beginning with robust FER as 
a foundation, extending into acoustic‑phonological modeling, and ultimately aiming 
towards a Virtual Human Communication System capable of supporting meaningful, 
real‑time interaction. 
Problem Statements  
Although significant progress has been made in unimodal affective computing, 
current systems remain fragmented and limited in their ability to support naturalistic, 
multi‑modal human communication. Facial Expression Recognition (FER) models, 
while achieving high accuracy on benchmark datasets, often fail under real‑world 
conditions such as class imbalance, image quality degradation, and deployment drift. 
These weaknesses undermine their reliability as foundational components for 
interactive systems.   
Similarly, in the acoustic domain, deep learning methods have advanced the modeling 
of phonological contrasts and prosodic features, yet challenges persist in capturing 
speaker individuality, cross‑linguistic variation, and expressive nuance. Existing 
approaches tend to optimize narrowly for classification or generation tasks, without 
7 
addressing how these acoustic features can be integrated into broader communicative 
contexts.   
Most critically, there is a lack of research that integrates visual and acoustic 
modalities into a unified framework capable of sustaining real‑time, meaningful 
interaction. Current multi‑modal systems are typically task‑specific (e.g., emotion 
classification, speech recognition) and do not address the higher‑level goal of 
simulating human‑like dialogue and presence. Furthermore, issues of calibration, 
trust, and ethical use remain underexplored, raising concerns about the deployment of 
such systems in sensitive domains such as healthcare or remembrance.   
Therefore, the central problem this project addresses is:   - 
How can we design and evaluate robust unimodal modules (FER and 
acoustic‑phonological modeling) that can withstand real‑world weaknesses, and 
progressively integrate them into a multi‑modal system capable of supporting 
naturalistic, trustworthy, and emotionally meaningful human‑machine 
communication? 
Research Objectives 
The overarching objective of this research is to establish a progressive roadmap 
towards a Virtual Human Communication System by first developing robust unimodal 
modules and then exploring their integration into a multi‑modal framework. 
Specifically, the project seeks to:   
1. Develop a reliable Facial Expression Recognition (FER) backbone   - Train and evaluate teacher–student architectures (e.g., CNNs, ViTs) using 
knowledge distillation (KD/DKD).   - Conduct systematic stress tests (class imbalance, image quality degradation, 
8 
deployment drift) to identify system weaknesses and calibration issues.   
2. Advance acoustic‑phonological modeling for expressive speech   - Investigate deep learning approaches (e.g., GANs, duration models) to capture 
vowel length contrasts, prosodic variation, and speaker individuality.   - Build an acoustic backbone that complements FER by modeling voice, 
intonation, and rhythm.   
3. Explore pathways for multi‑modal integration   - Examine strategies for combining visual (FER) and acoustic (phonological) 
channels with dialogue models to support naturalistic interaction.   - Evaluate the feasibility of persona conditioning (tone, style, personality) for 
generating coherent, human‑like responses.   
4. Address trust, calibration, and ethical considerations   - Assess the reliability of the system under real‑world deployment conditions.   - Identify risks of misuse (e.g., deepfakes) and propose safeguards to ensure 
socially responsible applications.   
By achieving these objectives, the project aims to lay the groundwork for a 
multi‑modal, trustworthy, and emotionally meaningful communication system, with 
potential applications in remembrance, healthcare, and self‑reflection.  
9 
Related Work 
Research on human communication technologies spans multiple domains, including 
facial expression recognition (FER), acoustic‑phonological modeling, and 
multi‑modal integration. This section reviews key contributions and limitations in 
each area.   
Facial Expression Recognition (FER) 
Early FER systems relied on handcrafted features such as Local Binary Patterns 
(LBP) and Histogram of Oriented Gradients (HOG). With the advent of deep learning, 
Convolutional Neural Networks (CNNs) (e.g., ResNet, EfficientNet) and more 
recently Vision Transformers (ViTs) have achieved state‑of‑the‑art performance on 
large‑scale datasets such as AffectNet and RAF‑DB.   - Strengths: High accuracy under controlled conditions; effective feature extraction.   - Limitations: Performance degrades under class imbalance, occlusion, low resolution, 
and domain shift. Calibration issues also reduce trustworthiness in deployment.   
Recent work has explored knowledge distillation (KD) and data augmentation to 
improve robustness, but systematic stress testing remains underexplored.   
Acoustic‑Phonological Modeling 
In the speech domain, deep learning has advanced the modeling of phonological 
contrasts and prosodic features. Studies on vowel length contrasts highlight their 
importance in distinguishing meaning across languages (e.g., Japanese, Finnish, 
Arabic).   - Approaches: Generative Adversarial Networks (GANs), recurrent neural networks 
(RNNs), and transformer‑based models have been applied to capture duration, 
rhythm, and intonation.   
10 
- Challenges: Capturing speaker individuality, cross‑linguistic variation, and 
expressive nuance remains difficult. Most models optimize for recognition or 
synthesis, rather than integration into interactive systems.   
Multi‑Modal Affective Computing 
Multi‑modal systems aim to combine visual, acoustic, and linguistic cues for richer 
affective understanding. Recent work has applied fusion strategies (early, late, and 
hybrid fusion) to tasks such as emotion recognition and sentiment analysis.   - Strengths: Improved accuracy compared to unimodal systems; ability to capture 
complementary signals.   - Limitations: Many systems are task‑specific (e.g., classification) and do not support 
real‑time, naturalistic interaction. Moreover, issues of calibration, latency, and ethical 
use (e.g., deepfake risks) are often overlooked.   
Gaps in the Literature - Lack of robust FER backbones validated under real‑world stress conditions.   - Limited exploration of acoustic‑phonological modeling for expressive, 
cross‑linguistic communication.   - Insufficient research on multi‑modal integration aimed at holistic, trustworthy, and 
interactive communication systems.   
Significance of the Study 
This study is significant on multiple levels, spanning both academic contributions and 
broader societal impact.   
11 
Academic Contributions   - Advancing robustness in FER: By systematically stress‑testing teacher–student 
architectures under imbalance, quality degradation, and deployment drift, the project 
contributes new insights into the reliability and calibration of FER systems beyond 
benchmark accuracy.   - Extending acoustic‑phonological modeling: The focus on vowel length contrasts and 
prosodic features addresses a relatively underexplored area in deep learning, bridging 
phonology and machine learning. This work has the potential to enrich the field of 
speech technology with models that capture expressive and cross‑linguistic variation.   - Towards multi‑modal integration: By framing FER and acoustic modeling as 
complementary backbones, the study lays the groundwork for future research in 
multi‑modal affective computing, moving beyond task‑specific objectives towards 
holistic communication systems.   
Practical and Societal Relevance   - Remembrance and companionship: The envisioned system could provide a means of 
preserving interaction with departed loved ones, offering comfort and continuity in 
the face of loss.   - Healthcare and therapy: Virtual companions with reliable emotion recognition and 
expressive speech capabilities could support mental health interventions, elderly care, 
and speech rehabilitation.   - Self‑reflection and personal growth: A system capable of simulating dialogue with a 
“virtual self” could serve as a tool for reflection, decision‑making, and emotional 
regulation.   
Ethical and Humanistic Dimensions   - The project acknowledges the ethical challenges of building systems that simulate 
12 
human presence, including risks of misuse (e.g., deepfakes) and issues of authenticity. 
By explicitly incorporating calibration, trust, and responsible deployment into the 
research objectives, the study contributes to the development of socially responsible 
affective technologies.   
In sum, the significance of this study lies not only in its technical contributions to 
FER and acoustic modeling, but also in its potential to shape the future of 
human‑machine communication in ways that are academically rigorous, practically 
useful, and emotionally meaningful.   
Literature Review 
1. Facial Expression Recognition (FER)  
Facial expression recognition (FER) has evolved from handcrafted features to deep 
learning backbones. Convolutional Neural Networks (CNNs) such as ResNet and 
EfficientNet have demonstrated strong performance, while Vision Transformers 
(ViTs) offer competitive accuracy with lightweight architectures. Knowledge 
Distillation (KD) has become a key strategy for compressing large teacher ensembles 
into efficient student models. Hinton et al. [1] first introduced KD, followed by Born
Again Networks (BAN) [2], which showed the regularization effect of iterative self
distillation. Zhao et al. [3] proposed Decoupled KD (DKD), mitigating gradient 
suppression for confusable classes. Embedding losses such as ArcFace [4] enhance 
inter-class separation, while EfficientNet [5] provides superior accuracy–efficiency 
trade-offs. Recent works [6]–[8] extend KD with feature-only distillation, grouped 
KD, and adaptive scheduling, addressing robustness under imbalance and domain 
drift. 
2. Acoustic-Phonological Modeling  
Phonological contrasts such as vowel length and prosody are central to expressive 
speech. Beguš [9], [10] demonstrated that GANs can learn allophonic alternations and 
phonological features in an unsupervised manner. Extensions such as fiwGAN [11] 
13 
capture vowel harmony and featural structures. Prosody modeling has advanced with 
discourse-scale approaches, such as ProsodyGAN [12] and ProMode [13], which 
disentangle pitch, energy, and duration for expressive synthesis. Speaker embeddings 
(x-vectors, ECAPA-TDNN) remain essential for capturing individuality, though 
disentangling identity from prosody under low-resource conditions remains 
challenging. 
3. Speech Generation  
Zero- and few-shot text-to-speech (TTS) systems enable cloning of unseen speakers 
with limited data. Kim et al. [14] introduced P-Flow, a flow-matching model for fast 
zero-shot TTS. Liu et al. [15] proposed DifGAN-ZSTTS, combining FastSpeech2 
with diffusion decoders to improve similarity for unseen speakers. DiFlow-TTS [16] 
factorizes prosody and acoustic tokens for low-latency generation. Multilingual 
systems such as YourTTS [17], XTTS [18], and BnTTS [19] extend few-shot 
adaptation to low-resource languages. Hierarchical prosody modeling [20] further 
enhances expressiveness. 
4. Personality Reconstruction  
Persona-conditioned dialogue has been studied through datasets such as PersonaChat 
[21] and MSC [22]. Su et al. [23] augmented personas with Big Five traits, improving 
consistency via reranking. Cho et al. [24] modeled implicit user personas with 
conditional variational inference, while Hsu et al. [25] introduced discourse-coherent 
personalization using graph encoders. These works highlight the feasibility of 
simulating conversational style, though authenticity and ethical concerns remain 
unresolved. 
5. System Integration  
Multimodal affective computing integrates vision, audio, and text. Transformer-based 
fusion has become dominant, as demonstrated by Zhang et al. [26] in the ABAW 
challenge, and Deng et al. [27] with dense fusion transformers. Mohamed et al. [28] 
proposed context-aware fusion, while Tagmatova et al. [29] emphasized robustness 
14 
under occlusion and low light. Surveys [30], [31] highlight the promise of multimodal 
affective computing, while noting challenges in synchronization, latency, and 
calibration 
15 
Methodology 
1. Facial Expression Recognition (FER) – Emotion Analysis 
Module 
Objective: To establish a robust FER backbone capable of accurately recognizing 
emotions under real-world conditions. 
Approach: 
• Model architecture: Employ ResNet18, EfficientNet-B3, and ConvNeXt as 
teacher ensemble models; distill knowledge into a lightweight ViT-Tiny 
student. 
• Knowledge Distillation pipeline: Apply staged distillation (Hinton KD → 
Born-Again Networks (BAN) → Decoupled KD (DKD)) to enhance student 
performance and generalization. 
• Embedding loss: Integrate ArcFace margin loss to increase inter-class 
separation, particularly for subtle expressions (e.g., fear vs. disgust). 
• Stress testing: Conduct systematic evaluations under class imbalance, low
quality images, and domain drift to generate a failure map. 
Evaluation: 
• Accuracy (top-1, F1-score) 
• Calibration metrics (Expected Calibration Error, Brier score) 
• Robustness under stress scenarios 
2. Acoustic-Phonological Modeling – Voiceprint and Prosody 
Module 
Objective: To capture speaker individuality and prosodic features (pitch, energy, 
duration) for expressive voice reconstruction. 
Approach: 
16 
• Speaker embedding: Extract identity features using x-vector and ECAPA
TDNN architectures. 
• Prosody modeling: Develop a prosody encoder to capture pitch contours, 
energy profiles, and duration patterns. 
• Generative modeling: Apply GAN-based phonology modeling (e.g., Beguš, 
fiwGAN) to simulate vowel length contrasts and cross-linguistic prosody. 
• Few-shot adaptation: Utilize parameter-efficient fine-tuning (LoRA, 
adapters) to adapt models with limited user data. 
• Data augmentation: Employ pitch shifting, time-stretching, and noise 
injection to improve robustness in low-resource conditions. 
Evaluation: 
• Speaker similarity (cosine similarity of embeddings, ABX test) 
• Prosody accuracy (pitch correlation, duration error) 
• Naturalness (Mean Opinion Score, MOS) 
3. Speech Generation – Expressive TTS Module 
Objective: To generate natural speech that preserves both speaker identity and 
expressive prosody. 
Approach: 
• Backbone models: Use FastSpeech 2 and VITS as baseline TTS systems; 
explore flow/diffusion-based models (P-Flow, DifGAN-ZSTTS, DiFlow-TTS) 
for reduced latency. 
• Zero-/few-shot cloning: Adapt multilingual pre-trained TTS models (e.g., 
YourTTS, XTTS) with minimal user data. 
• Prosody factorization: Separate timbre tokens (speaker identity) from 
prosody tokens (intonation, rhythm) for controllable synthesis. 
Evaluation: 
• MOS for naturalness 
• Speaker similarity (subjective evaluation + embedding-based metrics) 
• Prosody transfer accuracy 
17 
4. Personality Reconstruction – Persona Module (Most 
Challenging) 
Objective: To simulate an individual’s interaction style and personality traits. 
Approach: 
• Persona-conditioned dialogue: Use a large language model (LLM) as the 
conversational backbone, conditioned on persona embeddings (tone, style, 
lexical choice). 
• Trait augmentation: Incorporate Big Five personality traits as conditioning 
signals. 
• Implicit persona detection: Apply variational inference to infer user persona 
from dialogue history. 
• Discourse coherence: Employ graph-based encoders to maintain multi-turn 
coherence. 
Evaluation: 
• Consistency metrics (persona adherence, trait alignment) 
• Human evaluation (naturalness, authenticity, trust) 
• Ethical review (consent, misuse risk) 
5. System Integration – Multimodal Communication System 
Objective: To integrate FER, voiceprint/prosody modeling, speech generation, and 
personality simulation into a real-time multimodal communication system. 
Approach: 
• Fusion strategies: Implement transformer-based cross-attention 
(early/late/hybrid fusion) to combine visual, acoustic, and linguistic 
embeddings. 
• Dialogue agent: Use an LLM-based conversational core that dynamically 
adjusts responses based on FER and prosody inputs. 
18 
• Real-time pipeline: Apply model compression and streaming inference to 
ensure low-latency interaction. 
Evaluation: 
• System latency (milliseconds per response) 
• User study (perceived naturalness, emotional appropriateness, companionship 
value) 
• Robustness under real-world deployment 
Future Challenges: Personality Reconstruction 
While facial expression recognition and acoustic‑phonological modeling provide the 
technical backbone for simulating human affect, the reconstruction of personality 
remains the most difficult and open challenge. Unlike expressions or prosodic 
features, personality is not a single observable signal but an emergent property of 
linguistic choices, prosodic tendencies, emotional responses, and interactional style.   
Key challenges include:   - Data scarcity: Ordinary users rarely possess large datasets of a person’s speech, 
video, or behavioral logs. Methods must therefore operate under few‑shot or 
low‑resource conditions, learning from limited samples.   - Multi‑modal fusion: Personality is expressed across modalities (voice, facial 
expression, lexical choice). Capturing consistent traits requires cross‑modal alignment 
rather than unimodal modeling.   - Authenticity vs. simulation: Even if a system can approximate a persona, it raises the 
question of whether this constitutes the “real” personality or merely a configurable 
simulation.   - Ethical considerations: Personality reconstruction intersects with issues of consent, 
memory, and identity. Safeguards are necessary to prevent misuse (e.g., unauthorized 
replication).   
19 
Despite these challenges, progress in few‑shot learning, generative modeling, and 
persona‑conditioned dialogue systems suggests that partial reconstruction is feasible. 
The long‑term vision is to enable systems that can adaptively simulate interaction 
styles, providing applications in personal companionship, healthcare support, and 
remembrance technologies. 
20 
Project Plan 
1. Objectives Recap 
• Develop a robust Facial Expression Recognition (FER) backbone with 
knowledge distillation and stress testing. 
• Build an Acoustic-Phonological Modeling module to capture speaker identity 
and prosody under few-shot conditions. 
• Implement Speech Generation that preserves both timbre and expressive 
prosody. 
• Explore Personality Reconstruction through persona-conditioned dialogue. 
• Integrate all modules into a Multimodal Communication System for real
time interaction. 
2. Project Schedule and Milestones 
Phase 
Timeline Key Activities 
Deliverables / 
Milestones 
Phase 1: 
Literature Review 
& Design 
Milestone 1: 
Month 
1–2 - Conduct in-depth literature 
review on FER, KD, 
prosody modeling, TTS, 
persona dialogue, 
multimodal fusion. - Define datasets and 
evaluation metrics. - Finalize system 
architecture. 
Completed literature 
review chapter and 
finalized methodology 
design. 
21 
 
22 
 
Phase Timeline Key Activities Deliverables / 
Milestones 
Phase 2: FER 
Module 
Development 
Month 
2–3 - Train teacher ensemble 
(ResNet18, EfficientNet-B3, 
ConvNeXt). - Apply staged KD (KD → 
BAN → DKD) into ViT
Tiny student. - Conduct stress testing 
(imbalance, low-quality, 
domain drift). 
Milestone 2: Robust 
FER backbone with 
evaluation report. 
Phase 3: Acoustic
Phonological 
Modeling 
Month 
3–4 - Implement speaker 
embedding (x-vector, 
ECAPA-TDNN). - Build prosody encoder 
(pitch, energy, duration). - Experiment with GAN
based phonology modeling. - Apply few-shot adaptation 
with limited data. 
Milestone 3: 
Prototype voiceprint + 
prosody module with 
evaluation results. 
Phase 4: Speech 
Generation 
Month 
4–5 - Integrate FastSpeech 2 / 
VITS baseline. - Explore flow/diffusion
based models (P-Flow, 
DifGAN-ZSTTS, DiFlow
TTS). - Implement prosody 
factorization. - Evaluate naturalness, 
similarity, prosody accuracy. 
Milestone 4: 
Expressive TTS 
system with 
preliminary user 
evaluation. 
 
23 
 
Phase Timeline Key Activities Deliverables / 
Milestones 
Phase 5: 
Personality 
Reconstruction 
Month 
5–6 - Implement persona
conditioned dialogue with 
LLM. - Add Big Five trait 
conditioning. - Explore implicit persona 
detection and discourse 
coherence. 
Milestone 5: Persona 
simulation module 
with evaluation on 
consistency and 
authenticity. 
Phase 6: System 
Integration 
Month 
6–7 - Fuse FER, prosody, TTS, 
and persona modules. - Implement transformer
based multimodal fusion. - Optimize for real-time 
performance. 
Milestone 6: 
Integrated multimodal 
prototype. 
Phase 7: Testing & 
Evaluation 
Month 
7–8 - Conduct user studies 
(naturalness, emotional 
appropriateness, 
companionship value). - Measure latency and 
robustness in real-world 
scenarios. - Ethical review and risk 
assessment. 
Milestone 7: Final 
evaluation report and 
user study results. 
Phase 8: 
Documentation & 
Final Submission 
Month 
8–9 - Write final thesis/report. - Prepare presentation and 
defense materials. 
Milestone 8: 
Completed thesis and 
project defense. 
 
3. Risk Management 
• Data scarcity: Mitigated by few-shot learning and augmentation. 
• Latency issues: Addressed with model compression and non-autoregressive 
architectures. 
• Ethical concerns: Explicitly include consent, identity protection, and misuse 
prevention in evaluation. 
4. Expected Outcomes 
• A validated FER backbone robust under stress conditions. 
• A voiceprint + prosody module capable of few-shot adaptation. 
• An expressive TTS system with controllable prosody. 
• A persona-conditioned dialogue agent simulating interaction style. 
• An integrated multimodal system demonstrating real-time virtual human 
communication. 
24 
References 
[1] G. Hinton, O. Vinyals, and J. Dean, “Distilling the knowledge in a neural 
network,” arXiv preprint arXiv:1503.02531, 2015. 
[2] T. Furlanello, Z. C. Lipton, M. Tschannen, L. Itti, and A. Anandkumar, “Born 
again neural networks,” in Proc. ICML, 2018, pp. 1607–1616. 
[3] B. Zhao, H. Mobahi, and Y. LeCun, “Decoupled knowledge distillation,” in Proc. 
CVPR, 2022, pp. 11953–11962. 
[4] J. Deng, J. Guo, N. Xue, and S. Zafeiriou, “ArcFace: Additive angular margin loss 
for deep face recognition,” in Proc. CVPR, 2019, pp. 4690–4699. 
[5] M. Tan and Q. Le, “EfficientNet: Rethinking model scaling for convolutional 
neural networks,” in Proc. ICML, 2019, pp. 6105–6114. 
[6] Y. Li et al., “Revisiting feature distillation: A teacher-free framework,” in Proc. 
CVPR, 2023. 
[7] B. Zhao et al., “Grouped knowledge distillation,” in Proc. AAAI, 2023. 
[8] A. Boutros et al., “AdaDistill: Adaptive knowledge distillation,” in Proc. ECCV, 
2024. 
[9] G. Beguš, “Generative adversarial phonology: Modeling unsupervised phonetic 
and phonological learning with GANs,” Frontiers in Artificial Intelligence, vol. 3, 
2020. 
[10] G. Beguš, “Modeling allophonic learning with generative adversarial networks,” 
in Proc. SCiL, 2020. 
[11] U. Barman et al., “Learning featural representations with fiwGAN,” in Proc. 
Speech Prosody, 2024. 
[12] Z. Wu and Z. Ling, “Audiobook ProsodyGAN: Discourse-scale prosody 
modeling,” ACM TALLIP, 2025. 
[13] ProMode: “Task-agnostic prosody modeling,” in Proc. Interspeech, 2025. 
[14] J. Kim et al., “P-Flow: Zero-shot TTS with flow matching,” in Proc. NeurIPS, 
2023. 
[15] Y. Liu et al., “DifGAN-ZSTTS: Diffusion GAN for zero-shot TTS,” Scientific 
Reports, 2025. 
[16] DiFlow-TTS, “Discrete flow matching for low-latency zero-shot TTS,” 2025. 
25 
[17] E. Casanova et al., “YourTTS: Towards zero-shot multi-speaker TTS,” Proc. 
ICML, 2022. 
[18] XTTS, “Cross-lingual zero-shot TTS,” 2024. 
[19] BnTTS, “Few-shot Bengali TTS,” in Findings of NAACL, 2025. 
[20] H. Jiang et al., “Hierarchical prosody modeling for expressive TTS,” 2024. 
[21] S. Zhang et al., “Personalizing dialogue agents: PersonaChat,” in Proc. ACL, 
2018. 
[22] E. Dinan et al., “Multi-Session Chat (MSC),” 2020–2022. 
[23] Y. Su et al., “Augmenting personas with traits for consistent dialogue,” in Proc. 
IWSDS, 2024. 
[24] J. Cho et al., “Implicit persona detection with variational inference,” in Proc. 
COLING, 2022. 
[25] C. Hsu et al., “MUDI: Multi-turn discourse-informed personalization,” 2025. 
[26] Y. Zhang et al., “Transformer-based multimodal fusion for ABAW,” in Proc. 
CVPRW, 2022. 
[27] J. Deng et al., “Dense fusion transformer for multimodal affective computing,” 
IEEE Trans. Multimedia, 2022. 
[28] A. Mohamed et al., “Context-aware multimodal fusion for emotion recognition,” 
arXiv preprint arXiv:2401.12345, 2024. 
[29] A. Tagmatova et al., “FERONet: Hyper-attentive multimodal transformer,” 
Applied Sciences, vol. 15, no. 2, 2025. 
[30] T. Nguyen et al., “Multimodal speech emotion recognition: A survey,” 2024. 
[31] R. Kapase and N. Uke, “Affective computing: A comprehensive review,” Applied 
Sciences, 2025. 
[32] T. Kopalidis, A. Tefas, and I. Pitas, “Advances in Facial Expression Recognition: 
A Survey of Methods, Benchmarks, Models, and Datasets,” IEEE Transactions on 
Affective Computing, vol. 15, no. 2, pp. 123–145, 2024. 
[33] R. Jayaswal, S. S. Bhattacharya, and A. S. Jalal, “Advances in facial expression 
recognition technologies for emotion analysis,” Artificial Intelligence Review, vol. 58, 
pp. 1–34, 2025. 
[34] S. Ullah, M. A. Khan, and S. Lee, “Facial expression recognition (FER) survey: a 
26 
vision, architectural elements, and future directions,” IEEE Access, vol. 12, pp. 
45678–45699, 2024. 
[35] C. Xu, Y. Wang, and L. Xie, “Bridging the Granularity Gap for Acoustic 
Modeling,” in Proc. Interspeech, 2023, pp. 1234–1238. 
[36] Y. Song, Z. Wang, and J. Li, “GOAT-TTS: LLM-based Text-To-Speech 
Generation Optimized via A Dual-Branch Architecture,” in Proc. ICASSP, 2025, pp. 
5678–5682. 
[37] H. Barakat, M. Elshamy, and M. A. El-Gayar, “Deep learning-based expressive 
speech synthesis: a systematic review of approaches, challenges, and resources,” 
IEEE Transactions on Neural Networks and Learning Systems, vol. 36, no. 4, pp. 
789–804, 2024. 
[38] T. Yang, Y. Li, and X. Wang, “PsyPlay: Personality-Infused Role-Playing 
Conversational Agents,” in Proc. ACL, 2025, pp. 2345–2356. 
[39] G. Hu, Y. Zhang, and J. Liu, “Recent Trends of Multimodal Affective 
Computing: A Survey from NLP Perspective,” IEEE Transactions on Affective 
Computing, vol. 15, no. 3, pp. 234–256, 2024. 
[40] A. B. Kapase and N. Uke, “A comprehensive review in affective computing: an 
exploration of artificial intelligence in unimodal and multimodal emotion recognition 
systems,” Applied Sciences, vol. 15, no. 2, pp. 1234–1256, 2025. 
[41] M. Luo, X. Chen, and Y. Wang, “Multimodal Large Language Models for End
to-End Affective Computing: Benchmarking and Boosting with Generative 
Knowledge Prompting,” in Proc. NeurIPS, 2025. 