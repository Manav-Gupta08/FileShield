# PDF Toolkit Boundaries

pypdf opens signature-identified PDFs in strict mode with an existing valid password when required. A limit of 200 pages and 10,000 traversed object visits bounds ordinary analysis. Indirect references are tracked to avoid repeated cycles.

The reachable-object walker flags JavaScript, embedded files, forms/XFA, URI keys, launch/open/additional actions, annotations, signature fields and rich media. It reports encryption, standard metadata and root XMP presence. It detects evidence of signatures, not their cryptographic validity.

Rewriting rejects every PDF with these findings. For accepted PDFs it copies selected pages, removes page metadata, drops document metadata, and reparses the output. It refuses outputs with detected metadata, XMP or flagged structures. Merge accepts up to 10 inputs and 200 output pages. Page indices in API options are zero-based; repeated/out-of-order indices enable extraction and reordering. The UI converts human one-based indices to zero-based indices.

This is not general PDF content disarm. Image XMP/EXIF, visible text, inaccessible objects, unusual actions, revision artifacts, outlines and document-level features may survive or be lost. A rewrite can invalidate signatures. Nested image metadata and hidden data are not comprehensively sanitized.

PDF compression, PDF rasterization, image-to-PDF conversion and preserving complex interactive documents remain roadmap work. Known-password PDF removal uses the engine's password input but is not currently a dedicated UI workflow. Password cracking is not provided.