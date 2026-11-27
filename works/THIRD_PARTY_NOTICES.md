# Third-party notices

The event and provenance structure in `src/git_harness/history.py` adapts
`src/session_migrate/model.py` from xhluca/session-migrate, revision
`fefb719088dc0157b16f071065daa30434a0b980`:
https://github.com/xhluca/session-migrate/tree/fefb719088dc0157b16f071065daa30434a0b980

Modifications: explicit canonical/source identity, typed allowed content,
cursor/projection values, and omission of raw reasoning/context/opaque payloads.
The native converters and offline provider have not yet been copied into the
runtime package. The upstream license for the adapted model follows.

Repository-only `tests/support/offline_provider.py`, native provisioning pin/path
choices and the synthetic fixtures also adapt reviewed session-migrate test
material at that revision. Their complete license is retained in
`tests/support/LICENSE.session-migrate`; these test artifacts are excluded from
both product distributions. Provider changes include strict bounded requests,
Messages query handling, scripted tool/error responses and removal of Gemini.

MIT License

Copyright (c) 2026 xhluca

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
