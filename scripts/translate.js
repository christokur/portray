const YAML = require('yamljs');
const fs = require('fs');
const _ = require('lodash');

const args = require('./args');

const languageNames = {
	en: 'English',
	es: 'Spanish',
	de: 'German',
	nl: 'Dutch',
	da: 'Danish',
	sv: 'Swedish',
	fi: 'Finnish',
	no: 'Norwegian',
	fr: 'French',
	pl: 'Polish',
	cs: 'Czech',
	it: 'Italian',
	pt: 'Portuguese',
	tr: 'Turkish',
	zh: 'Chinese',
	th: 'Thai',
	vi: 'Vietnamese',
	ko: 'Korean',
	ja: 'Japanese',
	tl: 'Tagalog',
	ar: 'Arabic',
	fa: 'Farsi',
	sk: 'Slovakian',
	ro: 'Romanian',
	el: 'Greek',
	hi: 'Hindi',
	ur: 'Pakistani',
	ru: 'Russian',
};

const languages = Object.keys(languageNames);
const DEFAULT_JSON_PATH = './public/locales';
const DEFAULT_YAML_PATH = './translate';

const main = () => {
	const jsonPath = args.json_path || DEFAULT_JSON_PATH;
	const jsonFilePrefix = args.json_file_prefix || '';

	const yamlPath = args.yaml_path || DEFAULT_YAML_PATH;
	const yamlFilePrefix = args.yaml_file_prefix || '';
	const isImport = !!(args.import ?? false);
	let isExport = !!(args.export ?? false);

	if (isImport) {
		isExport = false;
	}

	console.log('Options:', {
		jsonPath,
		jsonFilePrefix,
		yamlPath,
		yamlFilePrefix,
		isExport,
	});

	if (isExport) {
		exportJsonToYaml(jsonPath, jsonFilePrefix, yamlPath, yamlFilePrefix);
		process.exit(0);
	}

	importYamlToJson(jsonPath, jsonFilePrefix, yamlPath, yamlFilePrefix);
};

const exportJsonToYaml = (jsonPath, jsonFilePrefix, yamlPath, yamlFilePrefix) => {
	jsonPath = jsonPath || DEFAULT_JSON_PATH;
	jsonFilePrefix = jsonFilePrefix || '';
	yamlPath = yamlPath || DEFAULT_YAML_PATH;
	yamlFilePrefix = yamlFilePrefix || '';

	console.log('Translating JSON to YAML...');

	const baseFile = fs.readFileSync(`${jsonPath}/${jsonFilePrefix}en.json`);
	const baseLang = JSON.parse(baseFile);

	languages.forEach((l) => {
		let output = '';
		let lang = {};

		const jsonFilePath = `${jsonPath}/${jsonFilePrefix}${l}.json`;
		const yamlFilePath = `${yamlPath}/${yamlFilePrefix}${l}.yaml`;

		// Load the existing JSON file contents into output
		if (fs.existsSync(jsonFilePath)) {
			const langFile = fs.readFileSync(jsonFilePath);
			lang = JSON.parse(langFile);
		}

		output += '# ' + languageNames[l] + '\n\n';

		_.forEach(baseLang, function (val, key) {
			if (typeof val === 'string') {
				val = val.replace('\n', '\\n');
				output += `# ${val}\n`;
				output += `${key}: >-\n  ${lang[key] ? lang[key].replace('\n', '\\n') : ''}\n\n`;
			} else if (val.length > 0) {
				_.forEach(val, (v, k) => {
					output += `# ${v}\n`;
				});
				output += `${key}:\n  - ${lang[key] ? lang[key].join('\n  - ') : ''}\n\n`;
			}
		});

		fs.writeFileSync(yamlFilePath, output + '\n', (err) => {
			if (err) throw err;
		});
	});
};

const importYamlToJson = (jsonPath, jsonFilePrefix, yamlPath, yamlFilePrefix) => {
	jsonPath = jsonPath || DEFAULT_JSON_PATH;
	jsonFilePrefix = jsonFilePrefix || '';
	yamlPath = yamlPath || DEFAULT_YAML_PATH;
	yamlFilePrefix = yamlFilePrefix || '';

	console.log('Translating YAML to JSON...');

	languages.forEach((l) => {
		let output = {
			LanguageName: `${languageNames[l] ?? ''}`,
		};

		const jsonFilePath = `${jsonPath}/${jsonFilePrefix}${l}.json`;
		const yamlFilePath = `${yamlPath}/${yamlFilePrefix}${l}.yaml`;
		const doesJsonFileExist = fs.existsSync(jsonFilePath);
		const doesYamlFileExist = fs.existsSync(yamlFilePath);

		console.log(`Generating JSON file for... '${l}' (${doesJsonFileExist ? 'Previous data found' : 'New language'})`);

		// Load the existing JSON file contents into output
		if (doesJsonFileExist) {
			const langFile = fs.readFileSync(jsonFilePath);
			const parsed = JSON.parse(langFile) ?? {};
			output = { ...output, parsed };
		}

		if (doesYamlFileExist) {
			const input = YAML.load(yamlFilePath);

			_.forEach(input, (val, key) => {
				val && (output[key] = val);
			});

			fs.writeFileSync(jsonFilePath, JSON.stringify(output, null, 2) + '\n', (err) => {
				if (err) throw err;
			});
		}
	});
};

// Run the script
main();
