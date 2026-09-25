# Higgsfield — xưởng AI chính của studio

**Vai trò:** Higgsfield là **xương sống sản xuất**: từ ảnh nhân vật, storyboard, video, giọng đọc, sửa video, hậu kỳ tới phân tích. Studio gọi qua MCP "higgsfield" (tên công cụ có thể có tiền tố như `mcp__higgsfield__…` tuỳ máy — tìm theo tên chức năng bên dưới). Trả bằng credit Higgsfield.

**Danh mục tra ngày 25/09/2026. Model thay đổi thường xuyên** → trước khi chọn, luôn gọi `models_explore` (`action: "get"` với model_id, hoặc `recommend` kèm mô tả) để xác nhận thời lượng, tham số, vai trò ảnh (`medias[].roles`). Không đoán tham số.

## Luật dùng chung
- **Xem giá trước:** hầu hết lệnh tạo nhận `get_cost: true` → trả số credit mà không tạo. Dùng để báo người dùng trước. `balance` xem credit còn lại.
- **Không tự dùng lượt miễn phí:** chỉ đặt `use_unlim: true` khi người dùng yêu cầu. Nếu kết quả trả về `unlim_choice`, hỏi người dùng rồi gọi lại.
- **Timeout khi gửi lệnh:** không tự gửi lại (có thể bị tính tiền 2 lần). Giữ `job_id`, kiểm tra trạng thái trước.
- **Nhiều việc độc lập:** `generate_video_batch` / `generate_image_batch` / `generate_audio_batch` (≤12 mỗi lần) → `jobs_wait` (lặp tới khi xong) → tải file về bằng `curl -L -o`.
- **Đưa ảnh/video từ máy lên:** `media_upload` (nhận presigned URL) → `curl -X PUT --upload-file <file> "<upload_url>"` → `media_confirm` → dùng `media_id`. (Các "widget" upload chỉ dành cho giao diện claude.ai, không dùng trong Claude Code.)
- **Lưu mọi id** (`media_id`, `job_id`, `element_id`, `soul_id`) vào project.json để lần sau dùng lại, không upload/tạo lại.
- **Quy trình mẫu có sẵn:** `get_workflow_instructions` với tên workflow → nhận hướng dẫn chuyên sâu của Higgsfield. Dùng khi việc khớp tên workflow (bảng cuối file).

## 1. Nhân vật & đạo cụ nhất quán (khung 3) — quan trọng nhất cho phim dài
| Cách | Khi nào | Cách dùng |
|---|---|---|
| **Elements** (`show_reference_elements` action `create`) | Nhiều nhân vật trong một cảnh, bối cảnh, đạo cụ, sản phẩm; tạo ngay từ 1 ảnh | Đặt `<<<element_id>>>` ngay trong prompt `generate_image`/`generate_video`. Chạy với: Seedance 2.0, Kling 3.0, Cinema Studio Video 2/3, Nano Banana Pro/2, GPT Image 2, Seedream 4.5/5 lite, Cinema Studio Image 2.5 |
| **Soul** (`show_characters` action `train`) | "Bản sao số" của MỘT người thật (vd cô Ari), 5–20 ảnh, ~10 phút | Chỉ dùng với `soul_2` / `soul_cinematic` (ảnh). Một soul_id mỗi lần tạo |
| **Character sheet** (workflow `character-sheet`) | Cần bảng nhân vật nhiều góc/biểu cảm làm tham chiếu chuẩn | Tạo ảnh bảng → lưu thành Element |

Người thật (cô Ari, học viên): chỉ tạo khi người đó đồng ý. Hỏi người dùng chọn Soul hay Element nếu chưa rõ.

## 2. Storyboard & khung hình chính (khung 6)
- Ảnh chung: `gpt_image_2_5` (mặc định), `nano_banana_pro` (hỗ trợ Element), `cinematic_studio_2_5`, `soul_2`/`soul_cinematic` (người thật đã train).
- Sản phẩm/quảng cáo: `marketing_studio_image`; ảnh sản phẩm hàng loạt: workflow `product-photoshoot`.
- Ảnh storyboard tốt có thể dùng lại làm **khung đầu (`start_image`)** cho video → giữ bố cục đã duyệt.

## 3. Model video (khung 7)
| Model id | Thời lượng | Điểm mạnh | Chọn khi |
|---|---|---|---|
| `cinematic_studio_3_0` | 4–15s | Chất điện ảnh cao nhất, `genre`, tới 4K, âm thanh tuỳ chọn, khung đầu/cuối | Shot hero, cảnh cảm xúc chính |
| `cinematic_studio_video_v2` | 3–12s | `multi_shots` (nhiều shot/1 lần), `speedramp`, `genre` | Chuỗi shot ngắn cùng cảnh, cảnh hành động |
| `seedance_2_5` | 4–30s | Nhiều tham chiếu (`omni_reference`), **sửa video** (`video_edit`), **nối dài** (`video_extension` trước/sau), âm thanh | Clip dài nhiều shot, TVC sản phẩm, nối cảnh liền mạch |
| `seedance_2_0` | 4–15s | Hỗ trợ **Elements**, nhất quán danh tính, nhiều sản phẩm, 4K | Nhân vật/sản phẩm phải giống hệt giữa các cảnh |
| `kling3_0` | 3–15s | Nhiều shot, đồng bộ âm thanh, hỗ trợ Elements, 4K | Cảnh có thoại/âm thanh, nhiều shot |
| `gemini_omni_flash_1_1` | 3–10s (edit tới 30s) | Chữ/ảnh/video tham chiếu, **sửa video bằng lời** (`mode: edit`), tới 4K | Sửa lặp nhiều lần theo góp ý |
| `veo3_1` | 4/6/8s | Siêu thực, khớp môi thoại | Cận mặt nhân vật nói |
| `wan3_0` / `wan3_0_prime` | 2–30s | Khung đầu/cuối, tham chiếu âm thanh, `enable_thinking` | Clip dài theo khung đầu–cuối |
| `minimax_h3` | 4–15s | 2K, keyframe, tham chiếu hỗn hợp | Khung hình chính 2K |
| `flux_3_video` | 5–20s | Nối tiếp video, âm thanh | Kéo dài một cảnh |
| `marketing_studio_video` | 12–15s | Quảng cáo sản phẩm 1 chạm, UGC, hook | Video bán hàng ngắn |
| `veo3_1_lite`, `kling3_0_turbo` | ngắn | Rẻ, nhanh | **Bản nháp** để duyệt nhịp trước khi làm bản đẹp |

**Nối cảnh liền mạch:** dùng ảnh khung cuối shot trước làm `start_image` shot sau, hoặc `seedance_2_5` `video_extension`.

## 4. Sửa video đã tạo (khung 7, khi Kiểm Định báo lỗi)
- Sửa bằng lời: `gemini_omni_flash_1_1` (mode `edit`), `kling_video_edit` (kèm ảnh tham chiếu), `seedance_2_5` (mode `video_edit`), `flux_3_video_edit`.
- **Genjutsu:** `hf_mult_replace_object` (thay đồ vật/trang phục/sản phẩm trong video bằng ảnh), `hf_mult_motion_control` (chép chuyển động từ video mẫu sang nhân vật — vd lấy clip cô Ari tập thật → nhân vật AI tập y hệt, đúng giải phẫu).
- `motion_control` (Kling 3.0): nhân vật trong ảnh làm theo chuyển động + máy quay của video mẫu.
- Ưu tiên sửa hơn tạo lại từ đầu khi chỉ sai một chi tiết.

## 5. Âm thanh (khung 8)
- **Giọng đọc / lời thoại:** `generate_audio` model `seed_audio` (mặc định) hoặc `text2speech_v2` (variant elevenlabs/minimax…). Chọn giọng bằng `list_voices`.
- **Nhân bản giọng** (vd giọng thật của cô Ari, có đồng ý): `create_voice` → dùng như voice `element`.
- **Đổi giọng trong video:** `voice_change`. **Khớp môi** audio vào video: model `sync_so`. **Lồng tiếng sang ngôn ngữ khác:** `dubbing` (có tiếng Anh, Trung, Hàn, Nhật… — **không có tiếng Việt** làm ngôn ngữ đích).
- ⚠️ **Không có model nhạc nền/hiệu ứng âm thanh độc lập** cho video thường. Nhạc/tiếng động lấy từ: âm thanh gốc của model video (`generate_audio: true`), hoặc file nhạc người dùng cung cấp. Không dùng các model chỉ dành cho game.
- Workflow `narrator`: giọng dẫn chuyện khớp khung thời gian, hoặc đưa người dẫn lên hình.

## 6. Hậu kỳ (khung 8)
- **Upscale:** `upscale_video` (topaz 1080p/2160p hoặc bytedance 1080p/2K/4K, preset `aigc` cho video AI); `video_deflicker` chống nháy.
- **Đổi tỉ lệ cho từng nền tảng:** `reframe` (16:9 ↔ 9:16 ↔ 1:1…, video ≤60s).
- **Tách nền:** `video_background_remover`, `sam_3_video`.
- **Phụ đề cháy vào hình:** workflow `subtitles`.
- **Dựng bằng AI (Higgsedit):** workflow `video-editing` — cắt, ghép, đổi nhạc, **chữ động, tiêu đề, overlay**. Dùng cho bản hoàn chỉnh có chữ; `tools/ghep_phim.py` (ffmpeg) cho bản nháp nhanh miễn phí.
- **Ảnh bìa/thumbnail:** workflow `thumbnail-generation`.

## 7. Phân tích & kiểm định (khung 9, Thủ Thư)
- `video_analysis_create` (video đã upload hoặc link YouTube) → `video_analysis_status`: phân tích **từng cảnh** của phim mẫu (3–5 phút; video càng dài càng kém chính xác). Thủ Thư dùng để học phong cách.
- `virality_predictor`: dự đoán độ viral, sức hút 3 giây đầu, rủi ro người xem bỏ đi — Kiểm Định dùng cho video mạng xã hội.

## 8. Công cụ marketing (khi phim là quảng cáo)
- `show_marketing_studio_v2` / `get_presets` (source `marketing_studio`): mẫu UGC, product shot, motion, poster. `ad_reference_id` tái tạo kịch bản một quảng cáo có sẵn.
- `get_presets` (source `viral`) + `execute_preset`: hiệu ứng viral. Chỉ chạy preset khi người dùng yêu cầu rõ.
- Workflow `ad-multiplier`: nhân một video quảng cáo 4–30s thành nhiều phiên bản (đổi người, sản phẩm, bối cảnh).

## Workflow Higgsfield nên nạp theo việc
| Việc | Workflow |
|---|---|
| Bảng nhân vật nhiều góc | `character-sheet` |
| Ảnh sản phẩm, packshot | `product-photoshoot` |
| Giọng dẫn chuyện khớp thời gian | `narrator` |
| Phim kể chuyện có người dẫn, không lộ mặt | `faceless-video` |
| Video UGC (review, unboxing, try-on, tutorial, sản phẩm) | `ugc-*` tương ứng |
| Nhiều phiên bản một quảng cáo | `ad-multiplier` |
| Phụ đề cháy vào hình | `subtitles` |
| Dựng, chữ động, tiêu đề | `video-editing` |
| Thumbnail | `thumbnail-generation` |
