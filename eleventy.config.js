const { DateTime } = require("luxon");
const markdownIt = require("markdown-it");
const YAML = require("yaml");


function filterEntries(entries, key, value) {
	return entries
		.filter(entry => entry[key])
		.filter(entry => entry[key] === value || (Array.isArray(entry[key]) && entry[key].includes(value)));
}

module.exports = function(eleventyConfig) {
    eleventyConfig.setInputDirectory("src");
    eleventyConfig.setOutputDirectory("docs");

    eleventyConfig.addPassthroughCopy("src/**/*.css");
    eleventyConfig.addPassthroughCopy("src/**/*.pdf");
    eleventyConfig.addPassthroughCopy("src/CNAME"); // Github Pages Domain

    eleventyConfig.addFilter("formatDate", (dateObj) => {
        return DateTime.fromJSDate(dateObj).toISODate();
    });     

    eleventyConfig.addFilter("debug", (obj) => JSON.stringify(obj));

		eleventyConfig.addFilter("filterEntries", filterEntries);
		eleventyConfig.addNunjucksGlobal("filterEntries", filterEntries);
	
    let markdownOptions = {
        html: true,
        breaks: true,
        linkify: true
    };
    let markdownLib = new markdownIt(markdownOptions);

    markdownLib.renderer.rules.table_open = () => '<div class="table-wrapper">\n<table>\n',
    markdownLib.renderer.rules.table_close = () => '</table>\n</div>',

    eleventyConfig.setLibrary("md", markdownLib);
	
		// YAML Data Sources
		eleventyConfig.addDataExtension("yml,yaml", (contents) => YAML.parse(contents));
};
