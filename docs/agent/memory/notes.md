# Notes

Notes are lightweight files used for simple information storage.

The agent maintains both **short-term memory** and **long-term memory** for notes.  
To optimize memory usage, the agent automatically generates **summaries** from short-term notes and stores those summaries in long-term memory.

---

## Short-Term Memory

All newly created notes are stored in the agent’s **short-term memory**.

Short-term memory is **ephemeral** and lasts until the end of the current day.  
When the day ends, the agent automatically creates a summary of all short-term notes and transfers this summary into long-term memory.

> ⚠️ **Attention**  
> If you end, exit, or close the agent **before** a summary is created, **all information stored in short-term memory will be lost**.  
>
> To prevent data loss, manually trigger a summary using:
>
> ```
> memory notes summarize
> ```
>
> You can configure whether summarized notes are saved to or loaded from a **database** or **files** in `config.json`.

---

## Long-Term Memory

Long-term memory contains all **summarized notes** generated from short-term memory.

These summaries are persistent and can be accessed by the agent at any time, from anywhere.

Storage behavior is configurable via `config.json`, allowing you to choose whether long-term memory is persisted using:
- A database
- Files

Long-term memory serves as the agent’s durable knowledge base, optimized for recall and long-term context.
