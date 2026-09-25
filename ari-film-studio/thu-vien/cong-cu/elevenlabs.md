# ElevenLabs (MCP)

- **Kết nối:** MCP chính thức do ElevenLabs host, đăng nhập bằng tài khoản ElevenLabs (OAuth — không phải nhập API key). Trong Claude Code:
  ```
  claude mcp add --transport http elevenlabs https://api.elevenlabs.io/v1/mcp
  ```
  rồi gõ `/mcp` trong Claude Code để đăng nhập. (Cách cũ chạy trên máy: `claude mcp add elevenlabs -- uvx elevenlabs-mcp` với biến môi trường `ELEVENLABS_API_KEY`.) Trên claude.ai có thể thêm ở mục Connectors.
- **Làm được:** giọng đọc (text-to-speech), nhân bản giọng, đổi giọng, lồng tiếng sang ngôn ngữ khác, **nhạc**, **hiệu ứng âm thanh**, chép lời (transcript). Tên công cụ cụ thể xem trong danh sách công cụ MCP sau khi kết nối — không đoán.
- **Chọn khi:** cần giọng tiếng Việt tự nhiên, giọng nhân bản chất lượng cao, hoặc **nhạc nền / hiệu ứng âm thanh** (Higgsfield không có model nhạc riêng).
- **Lưu ý:** tính phí theo gói ElevenLabs (ký tự / phút). Nhân bản giọng người thật chỉ khi người đó đồng ý. Kiểm tra giọng tiếng Việt bằng một câu thử trước khi làm hàng loạt.
- **Lưu file:** tải kết quả về `du-an/<id>/am-thanh/<ma-track>.mp3` và ghi vào cột File của track.

Nguồn: elevenlabs.io/blog/elevenlabs-mcp-in-claude · github.com/elevenlabs/elevenlabs-mcp — tra 09/2026.
