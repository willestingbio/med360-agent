#!/bin/bash
# Build standalone widget with embedded knowledge base
set -e

WIDGET_DIR="$(dirname "$0")/../widget"
KB_DIR="$(dirname "$0")/../knowledge-base"
OUTPUT="$WIDGET_DIR/dr-medici-standalone.html"
TEMPLATE="$WIDGET_DIR/dr-medici-demo.html"

echo "Building standalone widget..."

# Escape KB files for JS embedding
escape_for_js() {
    cat "$1" | sed 's/\\/\\\\/g' | sed 's/`/\\`/g' | sed 's/\$/\\$/g'
}

# Build the KB data
KB_DATA="const KB_FILES = {"
for f in "$KB_DIR"/*.md; do
    name=$(basename "$f" .md)
    content=$(escape_for_js "$f")
    KB_DATA+="\"$name\": \`$content\`,"
done
KB_DATA+="};"

echo "KB data generated ($(wc -c <<< "$KB_DATA") bytes)"

# Insert KB data into template
cp "$TEMPLATE" "$OUTPUT"

# Replace the loadKB() function with embedded version
python3 -c "
import re
with open('$OUTPUT', 'r') as f:
    html = f.read()

# Remove the fetch-based loadKB and replace with embedded
kb_data = '''$KB_DATA'''

# Find and replace loadKB function
old_load = 'async function loadKB() {'
new_load = f'''// ─── Embedded KB ───
{kb_data}

function initFromEmbedded() {{
  for (const [name, text] of Object.entries(KB_FILES)) {{
    const source = name;
    const paragraphs = text.split(/\\\\n\\\\n+/);
    for (const para of paragraphs) {{
      const clean = para.trim();
      if (clean.length < 50) continue;
      if (clean.length > 800) {{
        const sentences = clean.split(/(?<=[.!?])\\\\s+/);
        let chunk = '';
        for (const s of sentences) {{
          if ((chunk + s).length > 800 && chunk) {{
            KB_CHUNKS.push({{ content: chunk.trim(), source }});
            chunk = s;
          }} else {{
            chunk += (chunk ? ' ' : '') + s;
          }}
        }}
        if (chunk.trim()) KB_CHUNKS.push({{ content: chunk.trim(), source }});
      }} else {{
        KB_CHUNKS.push({{ content: clean, source }});
      }}
    }}
  }}

  document.getElementById('sourceCount').textContent = KB_CHUNKS.length + ' fragmentos';
  document.getElementById('status').textContent =
    'Modo: búsqueda local | ' + KB_CHUNKS.length + ' fragmentos incrustados';
  console.log('KB cargada: ' + KB_CHUNKS.length + ' fragmentos de ' + Object.keys(KB_FILES).length + ' documentos');
}}

// ─── Reemplazar loadKB original ───
initFromEmbedded();
// old: async function loadKB() {{'''

html = html.replace(old_load, new_load)

# Also comment out the fetch-based body
html = html.replace('loadKB();', '// loadKB replaced by initFromEmbedded()')
html = html.replace('document.getElementById(\"userInput\").focus();', 'initFromEmbedded();\ndocument.getElementById(\"userInput\").focus();')

with open('$OUTPUT', 'w') as f:
    f.write(html)
"

echo "✓ Standalone widget built: $OUTPUT"
wc -c "$OUTPUT"
