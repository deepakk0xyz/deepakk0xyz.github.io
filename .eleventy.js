import eleventyNavigationPlugin from "@11ty/eleventy-navigation";

export default async function(config) {

  config.addFilter("stringify", data => JSON.stringify(data, null, 2));

	config.addPlugin(eleventyNavigationPlugin);

  return {
    dir: {
      input: "src",
      output: "public",
    }
  };
}