/* Checks the player's ROM, converts its byte order, applies the patch and checks the result. Runs in the browser and in Node. */
(function (root) {
	'use strict';

	const SOURCE_MD5 = '5bd1fe107bf8106b2ab6650abecd54d6'; // USA 1.0 in .z64 byte order

	const InstallError = function (code, message) {
		this.code = code;
		this.message = message;
	};

	const detectByteOrder = function (u8) {
		if (u8.length < 4)
			return null;
		const first = ((u8[0] << 24) | (u8[1] << 16) | (u8[2] << 8) | u8[3]) >>> 0;
		if (first === 0x80371240)
			return 'z64';
		if (first === 0x37804012)
			return 'v64';
		if (first === 0x40123780)
			return 'n64';
		return null;
	};

	/* Returns a copy in .z64 byte order. The bytes passed in are not changed. */
	const toZ64 = function (u8, order) {
		const out = new Uint8Array(u8.length);
		let i;

		if (order === 'z64') {
			out.set(u8);
		} else if (order === 'v64') {
			for (i = 0; i + 1 < u8.length; i += 2) {
				out[i] = u8[i + 1];
				out[i + 1] = u8[i];
			}
		} else {
			for (i = 0; i + 3 < u8.length; i += 4) {
				out[i] = u8[i + 3];
				out[i + 1] = u8[i + 2];
				out[i + 2] = u8[i + 1];
				out[i + 3] = u8[i];
			}
		}
		return out;
	};

	/* tools: { BinFile, VCDIFF }. Returns { rom: Uint8Array, byteOrder }, or throws InstallError. */
	const install = function (romBytes, patchBytes, targetMd5, tools) {
		const order = detectByteOrder(romBytes);

		if (order === null)
			throw new InstallError('NOT_N64', 'This file is not an N64 ROM.');

		const z64 = toZ64(romBytes, order);
		const romFile = new tools.BinFile(z64.buffer);

		if (romFile.hashMD5() !== SOURCE_MD5)
			throw new InstallError('WRONG_ROM', 'This ROM is not the USA 1.0 version this patch needs. Your file was not changed.');

		const patched = new tools.VCDIFF(new tools.BinFile(patchBytes.buffer.slice(patchBytes.byteOffset, patchBytes.byteOffset + patchBytes.byteLength))).apply(romFile, false); // The MD5 check below covers the whole result

		if (patched.hashMD5() !== targetMd5)
			throw new InstallError('BAD_RESULT', 'The patched ROM failed its check, so it was not saved. Please report this.');
		return { rom: patched._u8array, byteOrder: order };
	};

	/* Writes one .hfro add-on into rom (Uint8Array, changed in place). Format, big endian:
	   "HFRO", u32 version 1, u32 run count, then per run u32 offset, u32 length, bytes. */
	const applyOption = function (rom, patchBytes) {
		const view = new DataView(patchBytes.buffer, patchBytes.byteOffset, patchBytes.byteLength);
		const bad = function () {
			return new InstallError('BAD_OPTION', 'An option patch file is damaged. Please try again.');
		};
		let p = 12;
		let i;

		if (patchBytes.length < 12 || String.fromCharCode(patchBytes[0], patchBytes[1], patchBytes[2], patchBytes[3]) !== 'HFRO' || view.getUint32(4) !== 1)
			throw bad();
		const count = view.getUint32(8);
		for (i = 0; i < count; i++) {
			if (p + 8 > patchBytes.length)
				throw bad();
			const offset = view.getUint32(p);
			const length = view.getUint32(p + 4);
			if (p + 8 + length > patchBytes.length || offset + length > rom.length)
				throw bad();
			rom.set(patchBytes.subarray(p + 8, p + 8 + length), offset);
			p += 8 + length;
		}
	};

	/* Runs install, then applies the chosen add-ons. options: [{ id, bytes }]. optionMd5 maps the
	   sorted ids joined with '+' to the expected MD5 of the result. */
	const installWithOptions = function (romBytes, patchBytes, targetMd5, options, optionMd5, tools) {
		const result = install(romBytes, patchBytes, targetMd5, tools);

		if (options.length === 0)
			return result;
		const key = options.map(function (o) { return o.id; }).sort().join('+');
		const expected = optionMd5[key];
		if (!expected)
			throw new InstallError('BAD_OPTION', 'This combination of options is not supported.');
		const rom = new Uint8Array(result.rom);
		options.forEach(function (o) { applyOption(rom, o.bytes); });
		if (new tools.BinFile(rom.buffer).hashMD5() !== expected)
			throw new InstallError('BAD_RESULT', 'The patched ROM failed its check, so it was not saved. Please report this.');
		return { rom: rom, byteOrder: result.byteOrder };
	};

	const api = { SOURCE_MD5, InstallError, detectByteOrder, toZ64, install, applyOption, installWithOptions };

	if (typeof module !== 'undefined' && module.exports)
		module.exports = api;
	else
		root.HfrInstall = api;
})(this);
