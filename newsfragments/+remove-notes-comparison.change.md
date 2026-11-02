Always write requested notes in synchronous and asynchronous `questions.update_internal_notes()` calls, including identical or empty notes.
Remove the `notes_equal` callback and equivalent-notes skip path while retaining exact read-back verification and preservation of other question fields.
