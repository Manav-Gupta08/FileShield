# Performance Design

Efficiency comes after correctness/security. Hashing reads each file once for all requested algorithms. Uploads and GZIP counters use 64 KiB chunks. Signature detection reads a bounded prefix. Image operations decode bounded pixels and preserve aspect ratio. Reports, files, archive entries and PDFs have caps. Expensive parsers execute outside the request process.

These are resource-conscious choices, not benchmark proof of maximum performance. Encryption intentionally spends memory/CPU on Scrypt and holds a bounded file plus ciphertext in memory. Fresh-pixel image processing can hold several image copies. PDF traversal and metadata serialization can be expensive even within byte/page limits.

Production concurrency must be measured against worst-case parser memory, Scrypt memory, scanner time, worker RSS and storage I/O. Compose's worker concurrency is two, with a 2 GiB aggregate container limit and a 768 MiB address-space bound per parser child. Those example values need platform validation, not blind scaling.

Record p50/p95 completion time, rejection rate, queue depth, worker peak memory and cleanup latency using synthetic fixtures. Never benchmark with real private uploads or log metadata as labels. A load test must include simultaneous large multipart requests, slow senders, malformed documents, timeout jobs and antivirus outages. No numeric throughput claims have been verified yet.