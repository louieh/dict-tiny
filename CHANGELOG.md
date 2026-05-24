# Change Log

## [2.0.0] - 2026-05-22

### Removed

- Remove Gemini and OpenAI support along with their dependencies.

### Changed

- Optimize Youdao translation result parsing for Chinese-English, Chinese-Japanese, Chinese-French, and Chinese-Korean.
- Improve auto-completion with explain content.

### Added

- Add `DICT_TINY_SOURCE_LAN` environment variable.
- Add `--sl` and `--tl` short aliases for source and target language.

## [1.3.1] - 2024-09-07

### Added

- Add Chinese-English, Chinese-Japanese, Chinese-French, Chinese-Korean translation to youdao translator.
- You can now list currently supported OpenAI or Gemini models.

### Changed

- Update the API used by youdao translator.
- Support the latest OpenAI and Gemini models.

### Fixed

- Fixed the markdown rendering issue when streaming large models.
