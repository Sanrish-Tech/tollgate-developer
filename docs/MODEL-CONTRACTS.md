# Model contract review — October 6, 2026

The community contract renews the existing 21-profile set through October 14, 2026 inclusive UTC. Rates, token envelopes, endpoints and admitted features are unchanged; this is not authorization for new hosted tools or provider tiers. No paid provider calls were made for this renewal. Qualification consists of official-document review plus local accounting and adapter regressions, separately from the earlier commercial pilot's live checks.

Official sources checked:

- [OpenAI pricing](https://developers.openai.com/api/docs/pricing)
- [GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol)
- [GPT-6 Sol](https://developers.openai.com/api/docs/models/gpt-6-sol)
- [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna)
- [GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra)
- [GPT-5.6 Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol)
- [GPT-5.6 Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra)
- [GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
- [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- [Anthropic models and retirement dates](https://platform.claude.com/docs/en/models/overview)

OpenAI contracts use the documented full context/output envelopes and conservative long-context input/output maxima, including the existing cache-write reserve margin. Standard/global processing only. Anthropic's existing standard and five-minute-cache contracts retain their rate and context bounds. The Haiku review stops before its earliest listed retirement date. Price changes or unsupported usage dimensions can invalidate the bound; retain uncertain holds and update the reviewed release rather than editing expiry values locally.

The machine-readable contract is `distribution/direct-profiles.json`. Its exact SHA-256 is compiled in `proxy/direct_bounded.py`. Startup refuses an unknown profile digest; expiry is checked before admission. Candidate and historical fixtures included for regression tests are not additional production approvals.
