// QR Model 2, version 6-L, byte mode. Two blocks of 68 data and 18 parity
// codewords give short public form URLs up to 134 bytes with no QR service.
function encodeQr(value) {
  const bytes = new TextEncoder().encode(value);
  if (bytes.length > 134) return null;
  const bits = [];
  function append(number, width) {
    for (let bit = width - 1; bit >= 0; bit--) bits.push((number >>> bit) & 1);
  }
  append(4, 4);
  append(bytes.length, 8);
  for (const byte of bytes) append(byte, 8);
  append(0, 4);
  while (bits.length % 8) bits.push(0);
  for (let pad = 0; bits.length < 1088; pad++) append(pad % 2 ? 0x11 : 0xec, 8);
  const data = [];
  for (let i = 0; i < bits.length; i += 8) {
    data.push(bits.slice(i, i + 8).reduce((byte, bit) => (byte << 1) | bit, 0));
  }

  // QR Reed–Solomon arithmetic over GF(256), with reduction polynomial 0x11d.
  function multiply(a, b) {
    let product = 0;
    while (b) {
      if (b & 1) product ^= a;
      a <<= 1;
      if (a & 256) a ^= 0x11d;
      b >>>= 1;
    }
    return product;
  }
  let generator = [1];
  for (let root = 1; generator.length <= 18; root = multiply(root, 2)) {
    const next = Array(generator.length + 1).fill(0);
    generator.forEach((term, index) => {
      next[index] ^= term;
      next[index + 1] ^= multiply(term, root);
    });
    generator = next;
  }
  const blocks = [data.slice(0, 68), data.slice(68)];
  const parity = blocks.map((block) => {
    const remainder = [...block, ...Array(18).fill(0)];
    for (let i = 0; i < block.length; i++) {
      const factor = remainder[i];
      generator.forEach((term, index) => { remainder[i + index] ^= multiply(term, factor); });
    }
    return remainder.slice(block.length);
  });
  const codewords = [];
  for (let i = 0; i < 68; i++) codewords.push(blocks[0][i], blocks[1][i]);
  for (let i = 0; i < 18; i++) codewords.push(parity[0][i], parity[1][i]);

  const size = 41;
  const modules = Array.from({ length: size }, () => Array(size).fill(null));
  function pattern(x, y, radius, darkAt) {
    for (let dy = -radius; dy <= radius; dy++) {
      for (let dx = -radius; dx <= radius; dx++) {
        if (modules[y + dy]?.[x + dx] !== undefined) {
          modules[y + dy][x + dx] = darkAt(Math.max(Math.abs(dx), Math.abs(dy)));
        }
      }
    }
  }
  for (const [x, y] of [[3, 3], [size - 4, 3], [3, size - 4]]) {
    pattern(x, y, 4, (distance) => distance !== 2 && distance !== 4);
  }
  pattern(34, 34, 2, (distance) => distance !== 1);
  for (let i = 8; i < size - 8; i++) {
    modules[6][i] = i % 2 === 0;
    modules[i][6] = i % 2 === 0;
  }
  // Precomputed BCH format string for error level L, mask 0 (even row + column).
  const format = 0x77c4;
  for (let i = 0; i < 15; i++) {
    const dark = Boolean((format >>> i) & 1);
    if (i < 6) modules[i][8] = dark;
    else if (i < 8) modules[i + 1][8] = dark;
    else if (i === 8) modules[8][7] = dark;
    else modules[8][14 - i] = dark;
    if (i < 8) modules[8][size - 1 - i] = dark;
    else modules[size - 15 + i][8] = dark;
  }
  modules[size - 8][8] = true;
  let cursor = 0;
  let upward = true;
  for (let right = size - 1; right > 0; right -= 2) {
    if (right === 6) right--;
    for (let offset = 0; offset < size; offset++) {
      const y = upward ? size - 1 - offset : offset;
      for (const x of [right, right - 1]) {
        if (modules[y][x] !== null) continue;
        const dataBit = (codewords[cursor >>> 3] ?? 0) >>> (7 - (cursor & 7)) & 1;
        modules[y][x] = Boolean(dataBit ^ ((x + y) % 2 === 0));
        cursor++;
      }
    }
    upward = !upward;
  }
  return modules;
}


export function drawQr(canvas, url) {
  const modules = encodeQr(url);
  if (!modules) return false;
  const quiet = 4;
  const cell = 10;
  canvas.width = canvas.height = (modules.length + quiet * 2) * cell;
  const context = canvas.getContext("2d");
  context.fillStyle = "#fff";
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = "#06283f";
  modules.forEach((row, y) => row.forEach((dark, x) => {
    if (dark) context.fillRect((x + quiet) * cell, (y + quiet) * cell, cell, cell);
  }));
  return true;
}
