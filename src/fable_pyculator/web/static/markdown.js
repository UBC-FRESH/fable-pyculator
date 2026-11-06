function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function safeMarkdownHref(href) {
  const raw = String(href ?? "").replaceAll("&amp;", "&");
  if (!/^(https?:\/\/|\/|#)/i.test(raw)) return null;
  return escapeHtml(raw);
}

function inlineMarkdown(text) {
  const tokens = [];
  const protect = (html) => {
    tokens.push(html);
    return `\u0000${tokens.length - 1}\u0000`;
  };
  let escaped = escapeHtml(text);
  escaped = escaped.replace(/`([^`\n]+)`/g, (_match, code) => protect(`<code>${code}</code>`));
  escaped = escaped.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_match, label, href) => {
    const safe = safeMarkdownHref(href);
    return safe ? protect(`<a href="${safe}" target="_blank" rel="noreferrer">${label}</a>`) : label;
  });
  escaped = escaped.replace(/(^|[\s(])(https?:\/\/[^\s<)]+)/g, (match, prefix, url) => {
    const safe = safeMarkdownHref(url);
    return safe ? `${prefix}${protect(`<a href="${safe}" target="_blank" rel="noreferrer">${url}</a>`)}` : match;
  });
  escaped = escaped.replace(/\*\*([^*\n]+)\*\*/g, "<strong>$1</strong>");
  escaped = escaped.replace(/(^|[^*])\*([^*\n]+)\*/g, "$1<em>$2</em>");
  escaped = escaped.replace(/~~([^~\n]+)~~/g, "<del>$1</del>");
  return escaped.replace(/\u0000(\d+)\u0000/g, (_match, index) => tokens[Number(index)] ?? "");
}

function splitTableRow(line) {
  return line
    .trim()
    .replace(/^\|/, "")
    .replace(/\|$/, "")
    .split("|")
    .map((cell) => cell.trim());
}

function renderMarkdown(text) {
  const lines = String(text ?? "").replace(/\r\n?/g, "\n").split("\n");
  const output = [];
  let paragraph = [];
  let list = null;
  let code = null;

  const flushParagraph = () => {
    if (!paragraph.length) return;
    output.push(`<p>${paragraph.map(inlineMarkdown).join("<br>")}</p>`);
    paragraph = [];
  };
  const flushList = () => {
    if (!list) return;
    output.push(`<${list.type}>${list.items.map((item) => `<li>${inlineMarkdown(item)}</li>`).join("")}</${list.type}>`);
    list = null;
  };
  const flushCode = () => {
    if (code === null) return;
    output.push(`<pre><code>${escapeHtml(code.join("\n"))}</code></pre>`);
    code = null;
  };

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    if (line.trim().startsWith("```")) {
      if (code === null) {
        flushParagraph();
        flushList();
        code = [];
      } else {
        flushCode();
      }
      continue;
    }
    if (code !== null) {
      code.push(line);
      continue;
    }
    if (!line.trim()) {
      flushParagraph();
      flushList();
      continue;
    }
    if (/^\s*---+\s*$/.test(line)) {
      flushParagraph();
      flushList();
      output.push("<hr>");
      continue;
    }
    const heading = line.match(/^(#{1,6})\s+(.*)$/);
    if (heading) {
      flushParagraph();
      flushList();
      const level = Math.min(heading[1].length + 2, 5);
      output.push(`<h${level}>${inlineMarkdown(heading[2])}</h${level}>`);
      continue;
    }
    const unordered = line.match(/^\s*[-*+]\s+(.*)$/);
    const ordered = line.match(/^\s*\d+[.)]\s+(.*)$/);
    if (unordered || ordered) {
      flushParagraph();
      const type = unordered ? "ul" : "ol";
      if (!list || list.type !== type) {
        flushList();
        list = { type, items: [] };
      }
      list.items.push((unordered || ordered)[1]);
      continue;
    }
    const quote = line.match(/^\s*>\s?(.*)$/);
    if (quote) {
      flushParagraph();
      flushList();
      output.push(`<blockquote>${inlineMarkdown(quote[1])}</blockquote>`);
      continue;
    }
    if (line.includes("|") && index + 1 < lines.length && /^\s*\|?[\s:|-]+\|?\s*$/.test(lines[index + 1])) {
      flushParagraph();
      flushList();
      const header = splitTableRow(line);
      const rows = [];
      index += 2;
      while (index < lines.length && lines[index].includes("|") && lines[index].trim()) {
        rows.push(splitTableRow(lines[index]));
        index += 1;
      }
      index -= 1;
      output.push(
        `<div class="md-table-wrap"><table class="md-table"><thead><tr>${header
          .map((cell) => `<th>${inlineMarkdown(cell)}</th>`)
          .join("")}</tr></thead><tbody>${rows
          .map(
            (row) =>
              `<tr>${header.map((_, cellIndex) => `<td>${inlineMarkdown(row[cellIndex] ?? "")}</td>`).join("")}</tr>`,
          )
          .join("")}</tbody></table></div>`,
      );
      continue;
    }
    paragraph.push(line);
  }
  flushParagraph();
  flushList();
  flushCode();
  return output.join("");
}

export { escapeHtml, inlineMarkdown, renderMarkdown, safeMarkdownHref };
