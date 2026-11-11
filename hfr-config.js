const HFR_CONFIG = {
	targetMd5: 'a7a3528afce3d04a36534a9854ae343e',
	outputName: 'OoT HFR.z64',
	// Optional add-ons applied on top of the HFR ROM, built by tools/build_options.py
	options: [
		{ id: 'normal-aim', file: 'options/normal-aim.hfro', label: 'Normal aim', info: 'Pushing the stick up aims up in first person, C-up view and ranged aiming. Off keeps the original inverted aim.', checked: true },
		{ id: 'fast-text', file: 'options/fast-text.hfro', label: 'Faster text', info: 'Text appears twice as fast.', checked: true }
	],
	// MD5 of the result for each combination: chosen option ids, sorted and joined with '+'
	optionMd5: {
		'': 'a7a3528afce3d04a36534a9854ae343e',
		'fast-text': '70f4182dbcc0779b4e8ddd7a1fb259d1',
		'normal-aim': '240cc199490674141626911c31eba87f',
		'fast-text+normal-aim': 'f300d71debbfc0e67aff45c34aa7bd05'
	}
};
