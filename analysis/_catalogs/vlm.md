# Open-weight VLM 후보 카탈로그 (D19b)

> PROBE D19b "VLM backbone lineage choice" 의 후보 풀.
> *lineage 2-tuple = (initial weights) × (further-pretrain corpus)* 중
> **첫 번째 항** 의 enumeration. 두 번째 항(누가 이 VLM 위에 어떤 corpus 를
> 적층했는가) 은 `analysis/_catalogs/vla.md` 와 cross-reference.
> 데이터셋 적층은 `analysis/_catalogs/dataset.md`.
>
> v0.5 (2026-05). 공통 컬럼 표준은 `analysis/_catalogs/README.md` §2 참고.
> HuggingFace 공식 model card / 공식 블로그 / arXiv 1차 출처.
> **Human verified** — 인간이 셀 내용을 직접 검수했으면 ✅, 아니면 ⬜ (기본값).

## 카탈로그 표

| 모델 | 출시 | 파라미터 (variants) | License | Vision encoder | LLM backbone | Instruction-tuning corpus (핵심) | Human verified | Access | PROBE D19b 후보 메모 |
|---|---|---|---|---|---|---|---|---|---|
| **PaliGemma** | 2024.05 | 3B / 10B / 28B | Gemma ✅ | SigLIP-So400m | Gemma 2B/9B/27B | 다중 task (caption, OCR, VQA, detection, segmentation) | ⬜ | 🟢 [hf:google/paligemma](https://huggingface.co/google) | π0 default 가족 — 안전한 비교 baseline |
| **PaliGemma 2** | 2024.12 | 3B / 10B / 28B | Gemma ✅ | SigLIP-So400m | Gemma 2 2B/9B/27B | task-specific fine-tuning (pt / mix) | ⬜ | 🟢 [hf:google/paligemma2](https://huggingface.co/google) | π0 lineage 연장; π0.7 가 채택 가능성 |
| **Qwen-VL** | 2023.08 | 7B | Tongyi ✅¹ | OpenCLIP ViT-bigG | Qwen-7B | 1.4B 이미지-텍스트 쌍 | ⬜ | 🟢 [hf:Qwen/Qwen-VL-Chat](https://huggingface.co/Qwen) | 1세대 — 역사적 baseline; 현재는 후속 선호 |
| **Qwen2-VL** | 2024.08 | 2B / 7B / 72B | Tongyi ✅¹ | SigLIP | Qwen2 2B/7B/72B | dynamic resolution + 800B 이미지-텍스트 토큰 | ⬜ | 🟢 [hf:Qwen/Qwen2-VL-Instruct](https://huggingface.co/Qwen) | 검증된 high-quality lineage; 7B 최적 |
| **Qwen2.5-VL** | 2025.03 | 3B / 7B / 32B / 72B | Tongyi ✅¹ | SigLIP + window attention | Qwen2.5 3B/7B/32B/72B | 4.1T tokens 사전학습 + 다중 task 지시 | ⬜ | 🟢 [hf:Qwen/Qwen2.5-VL-Instruct](https://huggingface.co/Qwen) | 최신 Qwen 가족; 3B 미니, 32B 중간; D19b 핵심 후보 |
| **Qwen3-VL** | 2025.10 | 4B / 8B (Instruct/Thinking) | Tongyi ✅¹ | TBD (Qwen3 family) | Qwen3 4B/8B | 256K native context (1M expandable) | ⬜ | 🟢 [hf:Qwen/Qwen3-VL-Instruct](https://huggingface.co/Qwen) | **Xiaomi-Robotics-0 init** — 이미 VLA 적층 검증된 lineage |
| **InternVL3** | 2025.04 | 1B / 2B / 8B / 38B / 78B | Apache-2.0 ✅ | InternViT | Qwen2.5 1B/2B/8B/38B/78B | native multimodal pre-training + instruction-tuning | ⬜ | 🟢 [hf:OpenGVLab/InternVL3](https://huggingface.co/OpenGVLab) | **Apache-2.0 라이선스 강자**; 1B~2B 미니 backbone; compute 친화적 |
| **InternVL3.5** | 2025.08 | TBD (1B~240B 추정) ❓ | Apache-2.0 ✅ | TBD | Qwen3 backbone | TBD ❓ | ⬜ | 🟢 [hf:OpenGVLab/InternVL3.5](https://huggingface.co/OpenGVLab) | 매우 신규; 아직 stable 정보 부재 |
| **LLaVA-OneVision** | 2024.08 | 0.5B / 7B / 72B | Apache-2.0 ✅ | SigLIP | Qwen2 0.5B/7B/72B | 85M image-text + 22M instruction | ⬜ | 🟢 [hf:llava-hf/llava-onevision](https://huggingface.co/llava-hf) | 0.5B 극소형 — adapter-only 실험 후보; single/multi/video 통합 |
| **Eagle-2** | 2025.01 | 8B | NVIDIA Research ❌ | SigLIP-2 + ConvNeXt (MoVE) | SmolLM2 8B | 21.6M 데이터 + 4.6M high-quality instruction | ⬜ | 🟢 [hf:nvidia/Eagle2.5-8B](https://huggingface.co/nvidia) | **GR00T N1 init** — humanoid lineage 검증; ⚠ 비상용 |
| **Molmo** | 2024.09 | 7B-D / 7B-O / 72B | Apache-2.0 ✅ | OpenAI CLIP | Qwen2 7B / OLMo-7B-1024 / Qwen2 72B | PixMo (1M curated) + PixMo-AskModelAnything | ⬜ | 🟢 [hf:allenai/Molmo](https://huggingface.co/allenai) | **MolmoAct/MolmoAct2/MolmoBot init**; PixMo 완전 공개 |
| **Phi-3-Vision** | 2024.05 | 4.2B | MIT ✅ | TBD | Phi-3 Mini 3.8B | 500B tokens (textbook-like + filtered) | ⬜ | 🟢 [hf:microsoft/Phi-3-vision-128k-instruct](https://huggingface.co/microsoft) | 가벼운 4.2B; long context 128K; OCR/chart 강점 |
| **Phi-3.5-Vision** | 2024.08 | 4.2B | MIT ✅ | TBD | Phi-3 Mini 3.8B | 500B tokens (synthetic structured 포함) | ⬜ | 🟢 [hf:microsoft/Phi-3.5-vision-instruct](https://huggingface.co/microsoft) | compact SLM 검증; Microsoft toolchain |
| **Florence-2** | 2024.06 | 0.23B / 0.77B | MIT ✅ | Microsoft Vision Backbone | seq2seq encoder-decoder | FLD-5B (126M 이미지, 5.4B 주석) | ⬜ | 🟢 [hf:microsoft/Florence-2-base](https://huggingface.co/microsoft) | 극소형 0.23B; encoder-decoder 아키텍처 특이 |
| **SmolVLM** | 2024.11 | 256M / 500M / 2.2B | Apache-2.0 ✅ | SigLIP (shape-optimized) | SmolLM 256M/500M/2.2B | Cauldron + Docmatix (문서 25%, 캡션 18%) | ⬜ | 🟢 [hf:HuggingFaceTB/SmolVLM-Instruct](https://huggingface.co/HuggingFaceTB) | 최소 VLM (256M); resource-constrained 극한 후보 |
| **SmolVLM2** | 2025.01 | 256M / 500M / 2.2B | Apache-2.0 ✅ | SigLIP (shape-optimized) | SmolLM2 256M/500M/2.2B | Cauldron + Docmatix (video understanding 향상) | ⬜ | 🟢 [hf:HuggingFaceTB/SmolVLM2-Instruct](https://huggingface.co/HuggingFaceTB) | 256M 비디오 VLM; HF ecosystem best-in-class |
| **DeepSeek-VL2** | 2024.12 | 1.0B / 2.8B / 4.5B (activated MoE) | DeepSeek ✅¹ | SigLIP-SO400M-384 | DeepSeek MoE | 800B 이미지-텍스트 토큰 + ShareGPT4V 1.2M | ⬜ | 🟢 [hf:deepseek-ai/deepseek-vl2](https://huggingface.co/deepseek-ai) | MoE 아키텍처; Tiny (1.0B 활성) 매우 가벼움 |

¹ 700M MAU 미만 등 일반 연구·소규모 상용 조건부 허용. 자세한 조건은 각 라이선스 원문 참고.

## Cross-reference 규칙

- 각 행의 **"PROBE D19b 후보 메모"** 열에서 *"X init"* 라고 적힌 항목은
  `analysis/_catalogs/vla.md` 의 해당 VLA 행과 연결됨 (예: "Xiaomi-Robotics-0
  init" → `vla.md` 의 Xiaomi-Robotics-0 행의 "VLM init" 열).
- 같은 VLM 이 여러 VLA 의 init 으로 쓰인 경우 (예: PaliGemma → π0, π0.5),
  메모 열에 모두 표기.
- `Access` 열의 URL 은 공식 organization 페이지만 가리킴 (특정 모델
  variant 의 정확한 repo 명은 클릭 후 확인 필요).

## 출처 정책

- HuggingFace 공식 model card 또는 organization 페이지가 1차 출처.
- 학술 세부 (instruction-tuning corpus 등) 는 해당 모델의 공식 arXiv 논문
  참조 — 예: PaliGemma 2 [arXiv:2412.03555], Qwen2-VL [arXiv:2409.12191],
  InternVL3 [arXiv:2504.10479], LLaVA-OneVision [arXiv:2408.03326],
  Molmo [arXiv:2409.17146], DeepSeek-VL2 [arXiv:2412.10302].
- 라이선스는 각 모델 HF model card "License" 섹션에서 직접 확인. 신뢰도
  낮은 항목은 `TBD (이유)` 로 표기.
- 2026-05 기준; 신규 VLM 출시 시 quarterly rebalance.
