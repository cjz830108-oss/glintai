/* Glint Fiction Studio — client-side export: TXT / DOCX(Word HTML) / EPUB (minimal stored-zip) */
const Exporter = (() => {
  // ---- CRC32 ----
  const CRC_TABLE = (() => {
    const t = new Uint32Array(256);
    for (let n = 0; n < 256; n++) {
      let c = n;
      for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
      t[n] = c >>> 0;
    }
    return t;
  })();
  const crc32 = (bytes) => {
    let c = 0xffffffff;
    for (let i = 0; i < bytes.length; i++) c = CRC_TABLE[(c ^ bytes[i]) & 0xff] ^ (c >>> 8);
    return (c ^ 0xffffffff) >>> 0;
  };

  // ---- minimal STORED zip writer ----
  function makeZip(files) {
    const enc = new TextEncoder();
    const chunks = []; const central = []; let offset = 0;
    const u16 = (v) => [v & 0xff, (v >> 8) & 0xff];
    const u32 = (v) => [v & 0xff, (v >> 8) & 0xff, (v >> 16) & 0xff, (v >>> 24) & 0xff];
    for (const f of files) {
      const nameBytes = enc.encode(f.name);
      const data = typeof f.data === 'string' ? enc.encode(f.data) : f.data;
      const crc = crc32(data);
      const local = [
        ...u32(0x04034b50), ...u16(20), ...u16(0), ...u16(0), ...u16(0), ...u16(0),
        ...u32(crc), ...u32(data.length), ...u32(data.length),
        ...u16(nameBytes.length), ...u16(0), ...nameBytes,
      ];
      chunks.push(new Uint8Array(local), data);
      central.push({
        name: nameBytes, crc, size: data.length, offset,
      });
      offset += local.length + data.length;
    }
    let cdSize = 0; const cdChunks = [];
    for (const e of central) {
      const rec = [
        ...u32(0x02014b50), ...u16(20), ...u16(20), ...u16(0), ...u16(0), ...u16(0), ...u16(0),
        ...u32(e.crc), ...u32(e.size), ...u32(e.size), ...u16(e.name.length), ...u16(0), ...u16(0),
        ...u16(0), ...u16(0), ...u32(0), ...u32(e.offset), ...e.name,
      ];
      cdChunks.push(new Uint8Array(rec)); cdSize += rec.length;
    }
    const end = new Uint8Array([
      ...u32(0x06054b50), ...u16(0), ...u16(0), ...u16(central.length), ...u16(central.length),
      ...u32(cdSize), ...u32(offset), ...u16(0),
    ]);
    return new Blob([...chunks, ...cdChunks, end], { type: 'application/epub+zip' });
  }

  const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  function download(blob, filename) {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 4000);
  }

  const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '').slice(0, 60) || 'novel';

  // ---- TXT ----
  function txt(novel, chapters) {
    const parts = [`${novel.title}\nby Glint Fiction Studio\n\n`];
    for (const c of chapters.sort((a, b) => a.chapter_no - b.chapter_no)) {
      parts.push(`\n\n${c.title || 'Chapter ' + c.chapter_no}\n\n${c.content || ''}`);
    }
    download(new Blob([parts.join('')], { type: 'text/plain;charset=utf-8' }), `${slug(novel.title)}.txt`);
  }

  // ---- DOCX via Word-compatible HTML (.doc opens natively in Word) ----
  function doc(novel, chapters) {
    const body = chapters.sort((a, b) => a.chapter_no - b.chapter_no)
      .map((c) => `<h1 style="page-break-before:always">${esc(c.title || 'Chapter ' + c.chapter_no)}</h1>${(c.content || '').split(/\n\n+/).map((p) => `<p>${esc(p)}</p>`).join('')}`)
      .join('');
    const html = `<html xmlns:w="urn:schemas-microsoft-com:office:word"><head><meta charset="utf-8"><title>${esc(novel.title)}</title></head><body><h1>${esc(novel.title)}</h1>${body}</body></html>`;
    download(new Blob(['\ufeff', html], { type: 'application/msword' }), `${slug(novel.title)}.doc`);
  }

  // ---- EPUB ----
  function epub(novel, chapters) {
    const uuid = `urn:uuid:${(crypto.randomUUID ? crypto.randomUUID() : String(Date.now()))}`;
    const s = slug(novel.title);
    const list = chapters.sort((a, b) => a.chapter_no - b.chapter_no);
    const files = [{ name: 'mimetype', data: 'application/epub+zip' }];
    files.push({
      name: 'META-INF/container.xml',
      data: `<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>`,
    });
    files.push({
      name: 'OEBPS/content.opf',
      data: `<?xml version="1.0" encoding="utf-8"?><package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="bookid"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>${esc(novel.title)}</dc:title><dc:creator>Glint Fiction Studio</dc:creator><dc:language>en</dc:language><dc:identifier id="bookid">${uuid}</dc:identifier></metadata><manifest>${list.map((c) => `<item id="c${c.chapter_no}" href="c${c.chapter_no}.xhtml" media-type="application/xhtml+xml"/>`).join('')}<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/></manifest><spine toc="ncx">${list.map((c) => `<itemref idref="c${c.chapter_no}"/>`).join('')}</spine></package>`,
    });
    files.push({
      name: 'OEBPS/toc.ncx',
      data: `<?xml version="1.0" encoding="utf-8"?><ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1"><head><meta name="dtb:uid" content="${uuid}"/></head><docTitle><text>${esc(novel.title)}</text></docTitle><navMap>${list.map((c) => `<navPoint id="n${c.chapter_no}" playOrder="${c.chapter_no}"><navLabel><text>${esc(c.title || 'Chapter ' + c.chapter_no)}</text></navLabel><content src="c${c.chapter_no}.xhtml"/></navPoint>`).join('')}</navMap></ncx>`,
    });
    for (const c of list) {
      const paras = (c.content || '').split(/\n\n+/).map((p) => `<p>${esc(p)}</p>`).join('\n');
      files.push({
        name: `OEBPS/c${c.chapter_no}.xhtml`,
        data: `<?xml version="1.0" encoding="utf-8"?><!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml"><head><meta charset="utf-8"/><title>${esc(c.title || 'Chapter ' + c.chapter_no)}</title></head><body><h2>${esc(c.title || 'Chapter ' + c.chapter_no)}</h2>${paras}</body></html>`,
      });
    }
    download(makeZip(files), `${s}.epub`);
  }

  return { txt, doc, epub };
})();
window.Exporter = Exporter;
