/**
 * annotation_canvas.js
 *
 * The main annotation canvas component. Handles:
 *   - Rendering page text with annotation highlights
 *   - Mode switching (annotate, bulk tag, edit)
 *   - Text selection → entity picker popover
 *   - Creating and deleting annotations
 *   - Edit mode with smart diff-based annotation offset shifting
 *
 * Initialized via CANVAS_CONFIG object defined in page_detail.html.
 */

// ============================================================
// DATE PARSING & DATE FIELD WIDGET
// ============================================================

/**
 * Parses a free-text date string into a structured date object.
 *
 * Returns: { iso: "YYYY-MM-DD", precision: "day"|"month"|"year"|"decade"|"quarter_century"|"century", original: str }
 * Returns null if the string cannot be parsed.
 *
 * Supported input formats:
 *   Day:             "April 30 1900", "30 April 1900", "4/30/1900", "1900-04-30"
 *   Month:           "April 1900", "1900-04"
 *   Year:            "1900"
 *   Decade:          "1900s"
 *   Quarter century: "early 1800s", "mid 1800s", "late 1800s"
 *   Century:         "19th century", "18th century"
 */
function parseDateString(str) {
    if (!str || !str.trim()) return null;
    const s = str.trim();

    const MONTHS = {
        january: 1, february: 2, march: 3, april: 4, may: 5, june: 6,
        july: 7, august: 8, september: 9, october: 10, november: 11, december: 12,
        jan: 1, feb: 2, mar: 3, apr: 4, jun: 6, jul: 7, aug: 8,
        sep: 9, oct: 10, nov: 11, dec: 12,
    };

    const pad = (n, w = 2) => String(n).padStart(w, "0");
    const isoDate = (y, m = 1, d = 1) => `${pad(y, 4)}-${pad(m)}-${pad(d)}`;

    let m;

    // ---- Century: "19th century", "18th century" ----
    m = s.match(/^(\d{1,2})(?:st|nd|rd|th)\s+century$/i);
    if (m) {
        const century = parseInt(m[1]);
        return {iso: isoDate((century - 1) * 100), precision: "century", original: s};
    }

    // ---- Quarter century: "early 1800s", "mid 1800s", "late 1800s" ----
    m = s.match(/^(early|mid|late)\s+(\d{3,4})s$/i);
    if (m) {
        const qualifier = m[1].toLowerCase();
        const baseYear = parseInt(m[2]);
        const centuryBase = Math.floor(baseYear / 100) * 100;
        const offset = qualifier === "early" ? 0 : qualifier === "mid" ? 25 : 50;
        return {iso: isoDate(centuryBase + offset), precision: "quarter_century", original: s};
    }

    // ---- Decade: "1900s" ----
    m = s.match(/^(\d{3,4})s$/i);
    if (m) {
        return {iso: isoDate(parseInt(m[1])), precision: "decade", original: s};
    }

    // ---- ISO: "1900-04-30" ----
    m = s.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (m) {
        return {iso: isoDate(m[1], m[2], m[3]), precision: "day", original: s};
    }

    // ---- ISO month: "1900-04" ----
    m = s.match(/^(\d{4})-(\d{2})$/);
    if (m) {
        return {iso: isoDate(m[1], m[2]), precision: "month", original: s};
    }

    // ---- Numeric: "4/30/1900" (M/D/Y) ----
    m = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
    if (m) {
        return {iso: isoDate(m[3], m[1], m[2]), precision: "day", original: s};
    }

    // ---- "April 30 1900" or "30 April 1900" ----
    m = s.match(/^([A-Za-z]+)\s+(\d{1,2})\s+(\d{4})$/) ||
        s.match(/^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$/);
    if (m) {
        let monthName, day, year;
        if (isNaN(parseInt(m[1]))) {
            [, monthName, day, year] = m;
        } else {
            [, day, monthName, year] = m;
        }
        const monthNum = MONTHS[monthName.toLowerCase()];
        if (monthNum) return {iso: isoDate(year, monthNum, day), precision: "day", original: s};
    }

    // ---- "April 30" (no year) ----
    m = s.match(/^([A-Za-z]+)\s+(\d{1,2})$/) ||
        s.match(/^(\d{1,2})\s+([A-Za-z]+)$/);
    if (m) {
        let monthName, day;
        if (isNaN(parseInt(m[1]))) {
            [, monthName, day] = m;
        } else {
            [, day, monthName] = m;
        }
        const monthNum = MONTHS[monthName.toLowerCase()];
        if (monthNum) return {iso: isoDate("0000", monthNum, day), precision: "day", original: s};
    }

    // ---- "April 1900" ----
    m = s.match(/^([A-Za-z]+)\s+(\d{4})$/) ||
        s.match(/^(\d{4})\s+([A-Za-z]+)$/);
    if (m) {
        let monthName, year;
        if (isNaN(parseInt(m[1]))) {
            [, monthName, year] = m;
        } else {
            [, year, monthName] = m;
        }
        const monthNum = MONTHS[monthName.toLowerCase()];
        if (monthNum) return {iso: isoDate(year, monthNum), precision: "month", original: s};
    }

    // ---- "April" alone ----
    m = s.match(/^([A-Za-z]+)$/);
    if (m) {
        const monthNum = MONTHS[m[1].toLowerCase()];
        if (monthNum) return {iso: isoDate("0000", monthNum), precision: "month", original: s};
    }

    // ---- Bare year: "1900" ----
    m = s.match(/^(\d{4})$/);
    if (m) {
        return {iso: isoDate(m[1]), precision: "year", original: s};
    }

    return null;
}


/**
 * DateField widget.
 *
 * Renders a text input + precision dropdown inside a given container element.
 * Call getValue() to get the structured date value for storage.
 *
 * Stored format: { iso: "YYYY-MM-DD", precision: "day"|..., original: "April 30 1900" }
 */
class DateField {

    constructor(container, placeholder = "Date") {
        this.container = container;
        this._parsed = null;
        this._userOverride = null;
        this._build(placeholder);
    }

    _build(placeholder) {
        this.input = document.createElement("input");
        this.input.type = "text";
        this.input.placeholder = placeholder;
        this.input.className = "input input-bordered input-sm w-full mb-1";

        // Status hint
        this.hint = document.createElement("p");
        this.hint.className = "text-xs mb-1 hidden";

        // Precision row (hidden until input has a parseable value)
        this.precisionRow = document.createElement("div");
        this.precisionRow.className = "flex items-center gap-2 mb-2 hidden";

        const precisionLabel = document.createElement("span");
        precisionLabel.className = "text-xs text-gray-500 whitespace-nowrap";
        precisionLabel.textContent = "Precision:";

        this.precisionSelect = document.createElement("select");
        this.precisionSelect.className = "select select-bordered select-xs flex-1";

        for (const [value, label] of [
            ["day", "Day"],
            ["month", "Month"],
            ["year", "Year"],
            ["decade", "Decade"],
            ["quarter_century", "Quarter century"],
            ["century", "Century"],
        ]) {
            const el = document.createElement("option");
            el.value = value;
            el.textContent = label;
            this.precisionSelect.appendChild(el);
        }

        this.precisionRow.appendChild(precisionLabel);
        this.precisionRow.appendChild(this.precisionSelect);

        this.container.appendChild(this.input);
        this.container.appendChild(this.hint);
        this.container.appendChild(this.precisionRow);

        this.input.addEventListener("input", () => this._onInput());
        this.precisionSelect.addEventListener("change", () => {
            this._userOverride = this.precisionSelect.value;
        });
        this.precisionSelect.addEventListener("click", (e) => {
            e.stopPropagation();
        });
        this.precisionRow.addEventListener("click", (e) => {
            e.stopPropagation();
        });
    }

    _onInput() {
        const val = this.input.value.trim();
        if (!val) {
            this._parsed = null;
            this._userOverride = null;
            this.hint.classList.add("hidden");
            this.precisionRow.classList.add("hidden");
            return;
        }

        const parsed = parseDateString(val);
        if (parsed) {
            this._parsed = parsed;
            if (!this._userOverride) this.precisionSelect.value = parsed.precision;
            this.hint.textContent = `→ ${parsed.iso}`;
            this.hint.className = "text-xs mb-1 text-success";
            this.precisionRow.classList.remove("hidden");
        } else {
            this._parsed = null;
            this.hint.textContent = "Unrecognised — will store as plain text";
            this.hint.className = "text-xs mb-1 text-warning";
            this.precisionRow.classList.add("hidden");
        }
    }

    getValue() {
        const val = this.input.value.trim();
        if (!val) return null;
        if (this._parsed) {
            return {
                iso: this._parsed.iso,
                precision: this._userOverride || this._parsed.precision,
                original: val,
            };
        }
        return val; // fallback: store as plain text
    }

    hasValue() {
        return !!this.input.value.trim();
    }

    setError() {
        this.input.classList.add("input-error");
    }

    focus() {
        this.input.focus();
    }

    /**
     * Pre-populates the DateField from a stored value.
     * Accepts a structured { iso, precision, original } object or a plain string.
     */
    setValue(storedValue) {
        if (!storedValue) return;
        const displayText = (typeof storedValue === "object" && storedValue.original)
            ? storedValue.original
            : String(storedValue);
        this.input.value = displayText;
        this._onInput(); // parse + update hint/precision row
        // If stored precision differs from parsed (user had overridden it), restore it
        if (typeof storedValue === "object" && storedValue.precision) {
            this._userOverride = storedValue.precision;
            this.precisionSelect.value = storedValue.precision;
        }
    }
}


// ============================================================
class AnnotationCanvas {

    constructor(config) {
        this.pageId = config.pageId;
        this.projectId = config.projectId;
        this.urls = config.urls;

        // Internal state
        this.annotations = [];          // loaded from API on init
        this.entityTypes = [];          // loaded from API on init
        this.mode = "annotate";         // "annotate" | "bulk_tag" | "edit"
        this.bulkTagType = null;        // active EntityType in bulk tag mode
        this._pendingSelection = null;  // {start, end} of current selection being annotated

        // DOM references
        this.container = document.getElementById("annotation-canvas");
        this.popover = null;

        // Bind event handlers so we can remove them later if needed
        this._onMouseUp = this._onMouseUp.bind(this);
        this._onAnnotationClick = this._onAnnotationClick.bind(this);

        this._init();
    }

    // ---- INITIALIZATION ----

    async _init() {
        try {
            // Read page text from the json_script tag embedded in the template
            const textEl = document.getElementById("page-text");
            this.container.dataset.text = textEl ? JSON.parse(textEl.textContent) : "";

            // Load entity types and existing annotations in parallel
            const [entityTypesData, annotationsData] = await Promise.all([
                this._fetch(this.urls.entityTypes),
                this._fetch(this.urls.annotations),
            ]);

            this.entityTypes = entityTypesData.entity_types;
            this.annotations = annotationsData.annotations;

            this._render();
            this.container.addEventListener("mouseup", this._onMouseUp);
            this._renderToolbar();

        } catch (err) {
            console.error("AnnotationCanvas init failed:", err);
            this.container.innerHTML = `<p class="text-red-500">Failed to load annotation canvas.</p>`;
        }
    }

    // ---- RENDERING ----

    /**
     * Re-renders the entire canvas content.
     * Splits the page text into segments at annotation and pending-selection boundaries,
     * wrapping each in appropriate <span> elements.
     */
    _render() {
        const text = this._getText();
        this.container.innerHTML = "";

        const segments = this._buildSegments(text);
        const fragment = document.createDocumentFragment();

        for (let i = 0; i < segments.length; i++) {
            const segment = segments[i];
            const hasAnnotations = segment.annotations.length > 0;
            const isPending = segment.isPending;

            if (!hasAnnotations && !isPending) {
                // Plain unannotated text outside any selection
                fragment.appendChild(document.createTextNode(segment.text));

            } else if (!hasAnnotations && isPending) {
                // Plain text inside the pending selection -- show as selected
                const span = document.createElement("span");
                span.textContent = segment.text;
                if (this._pendingSelection?.entityType) {
                    span.style.backgroundColor = this._pendingSelection.entityType.color + "40";
                    span.classList.add("rounded-sm", "px-0.5");
                } else {
                    span.className = "bg-blue-200 rounded-sm px-0.5";
                }
                fragment.appendChild(span);

            } else {
                // Annotated segment (may also be in pending selection)
                const span = document.createElement("span");
                span.textContent = segment.text;
                span.dataset.start = segment.start;
                span.dataset.end = segment.end;
                span.dataset.annotationIds = JSON.stringify(
                    segment.annotations.map(a => a.id)
                );

                span.style.cssText = this._buildHighlightStyle(segment.annotations);
                span.classList.add("annotation-span", "cursor-pointer");

                // Only round/pad the left edge if the previous segment shares none of our annotations
                const annIds = new Set(segment.annotations.map(a => a.id));
                const prevSeg = segments[i - 1];
                const nextSeg = segments[i + 1];
                const leftIsEdge = !prevSeg || !prevSeg.annotations.some(a => annIds.has(a.id));
                const rightIsEdge = !nextSeg || !nextSeg.annotations.some(a => annIds.has(a.id));

                if (leftIsEdge) span.classList.add("rounded-l-sm", "pl-0.5");
                if (rightIsEdge) span.classList.add("rounded-r-sm", "pr-0.5");

                // If also within pending selection, add a ring
                if (isPending) {
                    if (this._pendingSelection?.entityType) {
                        span.style.outline = `2px solid ${this._pendingSelection.entityType.color}`;
                        span.style.outlineOffset = "0px";
                    } else {
                        span.classList.add("ring-2", "ring-blue-400");
                    }
                }

                span.addEventListener("click", this._onAnnotationClick);
                fragment.appendChild(span);
            }
        }

        const textDiv = document.createElement("div");
        textDiv.style.whiteSpace = "pre-wrap";
        textDiv.appendChild(fragment);
        this.container.appendChild(textDiv);

        this.container.dataset.text = text;
    }

    /**
     * Splits text into segments at annotation and pending-selection boundaries.
     * Each segment knows which annotations cover it and whether it's within
     * the current pending selection.
     */
    _buildSegments(text) {
        const boundarySet = new Set([0, text.length]);

        for (const ann of this.annotations) {
            boundarySet.add(ann.start_offset);
            boundarySet.add(ann.end_offset);
        }

        // Add pending selection boundaries so it gets its own segments
        if (this._pendingSelection) {
            boundarySet.add(this._pendingSelection.start);
            boundarySet.add(this._pendingSelection.end);
        }

        const boundaries = Array.from(boundarySet).sort((a, b) => a - b);
        const segments = [];

        for (let i = 0; i < boundaries.length - 1; i++) {
            const start = boundaries[i];
            const end = boundaries[i + 1];
            const segmentText = text.slice(start, end);

            const covering = this.annotations.filter(
                ann => ann.start_offset <= start && ann.end_offset >= end
            );

            const isPending = this._pendingSelection &&
                start >= this._pendingSelection.start &&
                end <= this._pendingSelection.end;

            segments.push({start, end, text: segmentText, annotations: covering, isPending});
        }

        return segments;
    }

    /**
     * Builds an inline CSS style for an annotated span.
     * Single annotation: solid background color at low opacity.
     * Multiple overlapping annotations: striped gradient.
     */
    _buildHighlightStyle(annotations) {
        if (annotations.length === 1) {
            const color = annotations[0].entity_type_color;
            return `background-color: ${color}40;`;
        }

        const stripeSize = 100 / annotations.length;
        const stops = annotations.map((ann, i) => {
            const color = ann.entity_type_color;
            const start = i * stripeSize;
            const end = (i + 1) * stripeSize;
            return `${color}60 ${start}%, ${color}60 ${end}%`;
        });

        return `background: repeating-linear-gradient(45deg, ${stops.join(", ")});`;
    }

    // ---- TOOLBAR ----

    _renderToolbar() {
        const existing = document.getElementById("bulk-tag-toolbar");
        if (existing) existing.remove();

        const toolbar = document.createElement("div");
        toolbar.id = "bulk-tag-toolbar";
        toolbar.className = "flex flex-wrap gap-2 mb-2 hidden";

        const setActive = (activeBtn, et) => {
            toolbar.querySelectorAll("button").forEach(b => {
                const color = this.entityTypes.find(t => t.id === b.dataset.typeId)?.color;
                b.style.backgroundColor = color + "40";
                b.style.borderColor = color;
                b.style.outline = "";
                b.style.color = "";
            });
            activeBtn.style.backgroundColor = et.color;
            activeBtn.style.borderColor = et.color;
            activeBtn.style.outline = `3px solid ${et.color}`;
            activeBtn.style.outlineOffset = "2px";
            activeBtn.style.color = "white";
        };

        for (const et of this.entityTypes) {
            const btn = document.createElement("button");
            btn.textContent = et.name;
            btn.dataset.typeId = et.id;
            btn.className = "btn btn-sm";
            btn.style.backgroundColor = et.color + "40";
            btn.style.borderColor = et.color;

            btn.addEventListener("click", (e) => {
                e.stopPropagation();
                this.bulkTagType = et;
                setActive(btn, et);
            });

            toolbar.appendChild(btn);
        }

        this.container.parentNode.insertBefore(toolbar, this.container);
    }

    // ---- MODE SWITCHING ----

    setMode(mode) {
        this.mode = mode;

        const annotateBtn = document.getElementById("btn-annotate");
        const editBtn = document.getElementById("btn-edit");
        const bulkTagBtn = document.getElementById("btn-bulk-tag");
        const toolbar = document.getElementById("bulk-tag-toolbar");

        [annotateBtn, editBtn, bulkTagBtn].forEach(btn => {
            if (btn) {
                btn.classList.remove("btn-primary");
                btn.classList.add("btn-outline");
            }
        });

        if (mode === "annotate") {
            annotateBtn.classList.replace("btn-outline", "btn-primary");
            if (toolbar) toolbar.classList.add("hidden");
            this.bulkTagType = null;
            this._disableEditing();

        } else if (mode === "bulk_tag") {
            if (bulkTagBtn) bulkTagBtn.classList.replace("btn-outline", "btn-primary");
            if (toolbar) toolbar.classList.remove("hidden");
            this.bulkTagType = null;
            this._disableEditing();

        } else if (mode === "edit") {
            editBtn.classList.replace("btn-outline", "btn-primary");
            if (toolbar) toolbar.classList.add("hidden");
            this.bulkTagType = null;
            this._enableEditing();
        }
    }

    _enableEditing() {
        const text = this._getText();

        const textarea = document.createElement("textarea");
        textarea.id = "edit-textarea";
        textarea.value = text;
        textarea.className = "textarea w-full min-h-96 font-mono text-sm";

        const saveBtn = document.createElement("button");
        saveBtn.textContent = "Save";
        saveBtn.className = "btn btn-primary btn-sm mt-2";
        saveBtn.addEventListener("click", () => this._saveEditedText(textarea.value));

        const cancelBtn = document.createElement("button");
        cancelBtn.textContent = "Cancel";
        cancelBtn.className = "btn btn-outline btn-sm mt-2 ml-2";
        cancelBtn.addEventListener("click", () => {
            this.setMode("annotate");
            this._render();
        });

        this.container.innerHTML = "";
        this.container.appendChild(textarea);
        this.container.appendChild(saveBtn);
        this.container.appendChild(cancelBtn);
    }

    _disableEditing() {
        const editTextarea = document.getElementById("edit-textarea");
        if (editTextarea) {
            this._render();
        }
    }

    /**
     * Saves edited text to the backend using a diff-based approach.
     *
     * Instead of checking whether annotation text still matches at its old offsets
     * (which breaks on any edit before the annotation), we compute a character-level
     * diff between old and new text and shift annotation offsets accordingly.
     *
     * An annotation is only truly invalidated if the text it was covering was itself
     * changed -- not just moved. Edits within annotated text (e.g. typo corrections)
     * update the annotated_text snapshot rather than invalidating.
     */
    async _saveEditedText(newText) {
        const oldText = this._getText();

        // Compute diff and figure out what happened to each annotation
        const {updatedAnnotations, invalidated} = this._reconcileAnnotations(
            oldText, newText, this.annotations
        );

        if (invalidated.length > 0) {
            const names = invalidated
                .map(a => `"${a.annotated_text}" → ${a.entity_display_name}`)
                .join("\n");

            const confirmed = confirm(
                `The following annotations cover text that was deleted and will be removed:\n\n${names}\n\nContinue?`
            );

            if (!confirmed) return;
        }

        try {
            // Save the new text to the backend
            await this._fetch(this.urls.pageText, {
                method: "PUT",
                body: JSON.stringify({text: newText}),
            });

            // Delete invalidated annotations from the backend
            for (const a of invalidated) {
                await this._fetch(this._annotationDetailUrl(a.id), {method: "DELETE"});
            }

            // Persist shifted offsets and updated text snapshots for surviving annotations
            const invalidatedIds = new Set(invalidated.map(a => a.id));
            const surviving = updatedAnnotations.filter(a => !invalidatedIds.has(a.id));

            if (surviving.length > 0) {
                await this._fetch(this.urls.annotationsBulkUpdate, {
                    method: "PATCH",
                    body: JSON.stringify({
                        annotations: surviving.map(a => ({
                            id: a.id,
                            start_offset: a.start_offset,
                            end_offset: a.end_offset,
                            annotated_text: a.annotated_text,
                        })),
                    }),
                });
            }

            // Update local state
            this.annotations = surviving;

            this.container.dataset.text = newText;
            this.setMode("annotate");
            this._render();

        } catch (err) {
            console.error("Failed to save text:", err);
            alert("Failed to save. Please try again.");
        }
    }

    /**
     * Reconciles annotation offsets after a text edit using a character-level diff.
     *
     * For each annotation we walk the diff and:
     *   - Shift start/end offsets by net insertions/deletions before the annotation
     *   - If text within the annotated range was deleted, mark as invalidated
     *   - If text within the annotated range was changed (delete+insert), update
     *     the annotated_text snapshot (handles typo corrections inside annotations)
     *
     * Returns { updatedAnnotations, invalidated }
     */
    _reconcileAnnotations(oldText, newText, annotations) {
        const ops = this._computeDiff(oldText, newText);

        const updatedAnnotations = [];
        const invalidated = [];

        for (const ann of annotations) {
            let oldPos = 0;
            let newPos = 0;
            let newStart = null;
            let newEnd = null;
            let deletedWithinAnnotation = false;

            for (const op of ops) {
                if (op.type === "equal") {
                    const opOldEnd = oldPos + op.count;
                    const opNewEnd = newPos + op.count;

                    // Map start offset if it falls within this equal block
                    if (newStart === null && ann.start_offset >= oldPos && ann.start_offset <= opOldEnd) {
                        newStart = newPos + (ann.start_offset - oldPos);
                    }
                    // Map end offset if it falls within this equal block
                    if (newEnd === null && ann.end_offset >= oldPos && ann.end_offset <= opOldEnd) {
                        newEnd = newPos + (ann.end_offset - oldPos);
                    }

                    oldPos += op.count;
                    newPos += op.count;

                } else if (op.type === "insert") {
                    // Insertion -- doesn't affect old offsets, just shifts new position
                    newPos += op.count;

                } else if (op.type === "delete") {
                    const deleteEnd = oldPos + op.count;

                    // Check if deletion overlaps with annotation's span
                    const overlapStart = Math.max(oldPos, ann.start_offset);
                    const overlapEnd = Math.min(deleteEnd, ann.end_offset);

                    if (overlapStart < overlapEnd) {
                        // Deletion overlaps with annotation content
                        // Check if the deletion is immediately followed by an insertion
                        // (i.e. a replacement, like a typo correction)
                        // We'll handle this below after processing all ops
                        deletedWithinAnnotation = true;
                    }

                    oldPos += op.count;
                }

                if (newStart !== null && newEnd !== null && oldPos > ann.end_offset) break;
            }

            // If text within annotation was deleted with no replacement, invalidate
            if (deletedWithinAnnotation) {
                // Check if the new text at the shifted position is a reasonable update
                // (i.e. the annotation was partially edited, not fully deleted)
                if (newStart !== null && newEnd !== null && newEnd > newStart) {
                    const newAnnotatedText = newText.slice(newStart, newEnd);
                    // Accept the edit -- update the snapshot
                    updatedAnnotations.push({
                        ...ann,
                        start_offset: newStart,
                        end_offset: newEnd,
                        annotated_text: newAnnotatedText,
                    });
                } else {
                    // Annotation was fully deleted
                    invalidated.push(ann);
                }
                continue;
            }

            // Couldn't map offsets -- annotation was in a deleted region
            if (newStart === null || newEnd === null) {
                invalidated.push(ann);
                continue;
            }

            updatedAnnotations.push({
                ...ann,
                start_offset: newStart,
                end_offset: newEnd,
                annotated_text: newText.slice(newStart, newEnd),
            });
        }

        return {updatedAnnotations, invalidated};
    }

    /**
     * Computes a character-level diff between two strings.
     * Returns an array of operations: {type: "equal"|"insert"|"delete", count: n}
     *
     * Uses LCS (Longest Common Subsequence) via dynamic programming.
     * O(n*m) -- suitable for page-sized texts (typically a few KB).
     */
    _computeDiff(oldText, newText) {
        const m = oldText.length;
        const n = newText.length;

        // Build LCS table
        const dp = Array.from({length: m + 1}, () => new Int32Array(n + 1));

        for (let i = 1; i <= m; i++) {
            for (let j = 1; j <= n; j++) {
                if (oldText[i - 1] === newText[j - 1]) {
                    dp[i][j] = dp[i - 1][j - 1] + 1;
                } else {
                    dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
                }
            }
        }

        // Traceback
        const ops = [];
        let i = m, j = n;

        while (i > 0 || j > 0) {
            if (i > 0 && j > 0 && oldText[i - 1] === newText[j - 1]) {
                ops.push({type: "equal", count: 1});
                i--;
                j--;
            } else if (j > 0 && (i === 0 || dp[i][j - 1] >= dp[i - 1][j])) {
                ops.push({type: "insert", count: 1});
                j--;
            } else {
                ops.push({type: "delete", count: 1});
                i--;
            }
        }

        ops.reverse();

        // Merge consecutive ops of the same type
        const merged = [];
        for (const op of ops) {
            const last = merged[merged.length - 1];
            if (last && last.type === op.type) {
                last.count += op.count;
            } else {
                merged.push({...op});
            }
        }

        return merged;
    }

    // ---- SELECTION & POPOVER ----

    _onMouseUp(e) {
        if (this.mode === "edit") return;

        setTimeout(() => {
            const selection = window.getSelection();
            if (!selection || selection.isCollapsed) return;

            const range = selection.getRangeAt(0);
            const offsets = this._getOffsets(range);
            if (!offsets) return;

            let {start, end} = offsets;
            if (start === end) return;

            // Trim leading and trailing spaces
            const text = this._getText();
            while (start < end && text[start] === ' ') start++;
            while (end > start && text[end - 1] === ' ') end--;

            if (start === end) return;

            const rect = range.getBoundingClientRect();
            selection.removeAllRanges();

            if (this.mode === "bulk_tag" && this.bulkTagType) {
                this._pendingSelection = {start, end};
                this._render();
                this._createAnnotationForType(start, end, this.bulkTagType, rect);
            } else if (this.mode === "annotate") {
                // Set pending selection and re-render to show highlight before popover opens
                this._pendingSelection = {start, end};
                this._render();
                this._showTypePicker(start, end, rect);
            }
        }, 10);
    }

    _getOffsets(range) {
        const textDiv = this.container.querySelector("div");
        if (!textDiv || !textDiv.contains(range.commonAncestorContainer)) return null;

        let charCount = 0;
        let start = null;
        let end = null;

        const walker = document.createTreeWalker(textDiv, NodeFilter.SHOW_TEXT);
        let node;

        while ((node = walker.nextNode())) {
            const nodeLength = node.textContent.length;

            if (node === range.startContainer) {
                start = charCount + range.startOffset;
            }
            if (node === range.endContainer) {
                end = charCount + range.endOffset;
                break;
            }

            charCount += nodeLength;
        }

        if (start === null || end === null) return null;
        return {start, end};
    }

    // ---- TYPE PICKER POPOVER ----

    _showTypePicker(start, end, rect) {
        this._closePopover(false); // false = don't clear pending selection highlight

        const popover = this._createPopover(rect);

        const title = document.createElement("p");
        title.className = "text-sm font-semibold mb-2";
        title.textContent = "Tag as:";
        popover.appendChild(title);

        for (const et of this.entityTypes) {
            const btn = document.createElement("button");
            btn.textContent = et.name;
            btn.className = "btn btn-sm w-full mb-1";
            btn.style.backgroundColor = et.color + "40";
            btn.style.borderColor = et.color;

            btn.addEventListener("click", () => {
                this._pendingSelection = {start, end, entityType: et};
                this._render();
                this._showEntitySearch(start, end, et, rect);
            });

            popover.appendChild(btn);
        }

        document.body.appendChild(popover);
        this.popover = popover;
    }

    _showEntitySearch(start, end, entityType, rect) {
        this._closePopover(false);

        const popover = this._createPopover(rect);

        const back = document.createElement("button");
        back.textContent = "← Back";
        back.className = "btn btn-ghost btn-xs mb-2";
        back.addEventListener("click", () => this._showTypePicker(start, end, rect));
        popover.appendChild(back);

        const label = document.createElement("p");
        label.className = "text-sm font-semibold mb-2";
        label.textContent = entityType.name;
        label.style.color = entityType.color;
        popover.appendChild(label);

        const input = document.createElement("input");
        input.type = "text";
        input.placeholder = "Search...";
        input.className = "input input-bordered input-sm w-full mb-2";
        popover.appendChild(input);

        const results = document.createElement("div");
        results.className = "max-h-48 overflow-y-auto";
        popover.appendChild(results);

        const newBtn = document.createElement("button");
        newBtn.textContent = "+ New " + entityType.name;
        newBtn.className = "btn btn-outline btn-sm w-full mt-2";
        newBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            this._showEntityForm(start, end, entityType, rect);
        });
        popover.appendChild(newBtn);

        let searchTimeout;
        const doSearch = async (q) => {
            if (!q) {
                results.innerHTML = "";
                return;
            }

            try {
                const url = `${this.urls.entitySearch}?q=${encodeURIComponent(q)}&type_id=${entityType.id}`;
                const data = await this._fetch(url);
                results.innerHTML = "";

                if (data.entities.length === 0) {
                    results.innerHTML = `<p class="text-sm text-gray-400 px-1">No results</p>`;
                    return;
                }

                for (const entity of data.entities) {
                    const item = document.createElement("button");
                    item.className = "btn btn-ghost btn-sm w-full text-left justify-start";
                    item.textContent = entity.display_name;
                    item.addEventListener("click", () => {
                        this._createAnnotation(start, end, entity);
                    });
                    results.appendChild(item);
                }
            } catch (err) {
                console.error("Entity search failed:", err);
            }
        };

        input.addEventListener("input", (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => doSearch(e.target.value), 200);
        });

        document.body.appendChild(popover);
        this.popover = popover;
        input.focus();
    }

    _showEntityForm(start, end, entityType, rect, existingEntity = null) {
        const schema = this.entityTypes.find(et => et.id === entityType.id)?.schema || [];
        const otherFields = schema.filter(f => f.name !== "display_name");

        if (otherFields.length > 2) {
            alert("Complex entity creation not yet supported inline. Coming soon.");
            return;
        }

        this._closePopover(false);
        const popover = this._createPopover(rect);

        const back = document.createElement("button");
        back.textContent = "← Back";
        back.className = "btn btn-ghost btn-xs mb-2";
        back.addEventListener("click", (e) => {
            e.stopPropagation();
            this._showEntitySearch(start, end, entityType, rect);
        });
        popover.appendChild(back);

        const label = document.createElement("p");
        label.className = "text-sm font-semibold mb-2";
        label.textContent = existingEntity ? "Edit " + entityType.name : "New " + entityType.name;
        label.style.color = entityType.color;
        popover.appendChild(label);

        const fieldInputs = {};
        const dateFields = {}; // DateField instances keyed by field name

        const dnInput = document.createElement("input");
        dnInput.type = "text";
        dnInput.placeholder = "Display name";
        dnInput.className = "input input-bordered input-sm w-full mb-2";
        // Pre-populate from existing entity, or default to selected text for new
        dnInput.value = existingEntity
            ? (existingEntity.metadata?.display_name ?? "")
            : this._getText().slice(start, end);
        fieldInputs["display_name"] = dnInput;
        popover.appendChild(dnInput);

        for (const field of otherFields) {
            if (field.type === "date") {
                const wrapper = document.createElement("div");
                popover.appendChild(wrapper);
                const df = new DateField(wrapper, field.label || field.name);
                if (existingEntity) df.setValue(existingEntity.metadata?.[field.name]);
                dateFields[field.name] = df;
            } else {
                const fieldInput = document.createElement("input");
                fieldInput.type = field.type === "number" ? "number" : "text";
                fieldInput.placeholder = field.label || field.name;
                fieldInput.className = "input input-bordered input-sm w-full mb-2";
                if (existingEntity) fieldInput.value = existingEntity.metadata?.[field.name] ?? "";
                fieldInputs[field.name] = fieldInput;
                popover.appendChild(fieldInput);
            }
        }

        const saveBtn = document.createElement("button");
        saveBtn.textContent = existingEntity ? "Save Changes" : "Create & Tag";
        saveBtn.className = "btn btn-primary btn-sm w-full";
        saveBtn.addEventListener("click", async (e) => {
            e.stopPropagation();

            const metadata = {};

            for (const [name, input] of Object.entries(fieldInputs)) {
                metadata[name] = input.value.trim();
            }

            for (const [name, df] of Object.entries(dateFields)) {
                metadata[name] = df.getValue();
            }

            if (!metadata.display_name) {
                dnInput.classList.add("input-error");
                return;
            }

            try {
                if (existingEntity) {
                    // PATCH existing entity
                    const url = this.urls.entityUpdate.replace("__id__", existingEntity.id);
                    const updated = await this._fetch(url, {
                        method: "PATCH",
                        body: JSON.stringify({metadata}),
                    });
                    // Update display name in all local annotations referencing this entity
                    this.annotations = this.annotations.map(a =>
                        a.entity_id === updated.id
                            ? {...a, entity_display_name: updated.display_name}
                            : a
                    );
                    this._closePopover();
                    this._render();
                } else {
                    // POST new entity, then create annotation
                    const entity = await this._fetch(this.urls.entityCreate, {
                        method: "POST",
                        body: JSON.stringify({entity_type_id: entityType.id, metadata}),
                    });
                    this._createAnnotation(start, end, entity);
                }
            } catch (err) {
                console.error(existingEntity ? "Failed to update entity:" : "Failed to create entity:", err);
                alert(existingEntity ? "Failed to save changes. Please try again." : "Failed to create entity. Please try again.");
            }
        });

        popover.appendChild(saveBtn);
        document.body.appendChild(popover);
        this.popover = popover;

        if (otherFields.length > 0) {
            const firstField = otherFields[0];
            if (dateFields[firstField.name]) {
                dateFields[firstField.name].focus();
            } else {
                fieldInputs[firstField.name].focus();
            }
        } else {
            dnInput.focus();
        }
    }

    // ---- ANNOTATION CLICK ----

    _onAnnotationClick(e) {
        if (this.mode === "edit") return;
        e.stopPropagation();

        const span = e.currentTarget;
        const annotationIds = JSON.parse(span.dataset.annotationIds);
        const annotations = this.annotations.filter(a => annotationIds.includes(a.id));

        const rect = span.getBoundingClientRect();
        this._closePopover();
        const popover = this._createPopover(rect);

        for (const annotation of annotations) {
            const item = document.createElement("div");
            item.className = "mb-3 pb-3 border-b last:border-0 last:mb-0 last:pb-0";

            const badge = document.createElement("span");
            badge.className = "badge badge-sm mb-1";
            badge.style.backgroundColor = annotation.entity_type_color + "40";
            badge.style.borderColor = annotation.entity_type_color;
            badge.textContent = annotation.entity_type_name;
            item.appendChild(badge);

            const name = document.createElement("p");
            name.className = "font-semibold text-sm";
            name.textContent = annotation.entity_display_name;
            item.appendChild(name);

            const text = document.createElement("p");
            text.className = "text-xs text-gray-400 mb-2";
            text.textContent = `"${annotation.annotated_text}"`;
            item.appendChild(text);

            const actions = document.createElement("div");
            actions.className = "flex gap-2";

            const removeBtn = document.createElement("button");
            removeBtn.className = "btn btn-ghost btn-xs text-error";
            removeBtn.textContent = "Remove";
            removeBtn.addEventListener("click", async () => {
                await this._deleteAnnotation(annotation.id);
            });
            actions.appendChild(removeBtn);

            const entityType = this.entityTypes.find(et => et.id === annotation.entity_type_id);
            if (entityType) {
                const editBtn = document.createElement("button");
                editBtn.className = "btn btn-ghost btn-xs";
                editBtn.textContent = "Edit";
                editBtn.addEventListener("click", (e) => {
                    e.stopPropagation();
                    const entity = {
                        id: annotation.entity_id,
                        metadata: annotation.entity_metadata,
                    };
                    this._showEntityForm(annotation.start_offset, annotation.end_offset, entityType, rect, entity);
                });
                actions.appendChild(editBtn);
            }

            item.appendChild(actions);
            popover.appendChild(item);
        }

        document.body.appendChild(popover);
        this.popover = popover;
    }

    // ---- ANNOTATION CRUD ----

    async _createAnnotationForType(start, end, entityType, rect) {
        this._showEntitySearch(start, end, entityType, rect);
    }

    async _createAnnotation(start, end, entity) {
        this._closePopover();

        try {
            const annotation = await this._fetch(this.urls.annotations, {
                method: "POST",
                body: JSON.stringify({
                    entity_id: entity.id,
                    start_offset: start,
                    end_offset: end,
                }),
            });

            this.annotations.push(annotation);
            this._render();

        } catch (err) {
            console.error("Failed to create annotation:", err);
            alert("Failed to save annotation. Please try again.");
        }
    }

    async _deleteAnnotation(annotationId) {
        this._closePopover();

        try {
            await this._fetch(this._annotationDetailUrl(annotationId), {method: "DELETE"});
            this.annotations = this.annotations.filter(a => a.id !== annotationId);
            this._render();

        } catch (err) {
            console.error("Failed to delete annotation:", err);
            alert("Failed to remove annotation. Please try again.");
        }
    }

    // ---- POPOVER HELPERS ----

    _createPopover(rect) {
        const popover = document.createElement("div");
        popover.id = "annotation-popover";
        popover.className = "fixed z-50 bg-base-100 border rounded-lg shadow-lg p-3 w-64";

        const top = rect.bottom + 8;
        const left = Math.min(rect.left, window.innerWidth - 280);

        popover.style.top = `${top}px`;
        popover.style.left = `${left}px`;

        // Remove any existing click-outside listener before registering a new one
        if (this._onClickOutside) {
            document.removeEventListener("click", this._onClickOutside);
            this._onClickOutside = null;
        }

        this._onClickOutside = (e) => {
            if (!popover.contains(e.target)) {
                this._closePopover();
            }
        };
        setTimeout(() => document.addEventListener("click", this._onClickOutside), 200);

        return popover;
    }

    /**
     * Closes the popover.
     * @param {boolean} clearPending - whether to also clear the pending selection highlight.
     *   Pass false when transitioning between popover steps (back button, type picker → search).
     *   Defaults to true -- clears selection when popover is fully dismissed.
     */
    _closePopover(clearPending = true) {
        if (this._onClickOutside) {
            document.removeEventListener("click", this._onClickOutside);
            this._onClickOutside = null;
        }

        if (this.popover) {
            this.popover.remove();
            this.popover = null;
        }
        const existing = document.getElementById("annotation-popover");
        if (existing) existing.remove();

        if (clearPending && this._pendingSelection) {
            this._pendingSelection = null;
            this._render();
        }
    }

    // ---- UTILITIES ----

    _getText() {
        return this.container.dataset.text || "";
    }

    _annotationDetailUrl(annotationId) {
        return this.urls.annotations.replace(
            /\/api\/pages\/[^/]+\/annotations\//,
            `/api/annotations/${annotationId}/`
        );
    }

    async _fetch(url, options = {}) {
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value;

        const response = await fetch(url, {
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken || "",
                ...options.headers,
            },
            ...options,
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.error || `Request failed: ${response.status}`);
        }

        const text = await response.text();
        return text ? JSON.parse(text) : {};
    }
}

// ---- BOOTSTRAP ----

document.addEventListener("DOMContentLoaded", () => {
    if (typeof CANVAS_CONFIG === "undefined") {
        console.error("CANVAS_CONFIG not defined -- canvas cannot initialize.");
        return;
    }
    window.canvas = new AnnotationCanvas(CANVAS_CONFIG);
});