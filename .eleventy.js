export default async function(config) {

  config.addFilter("stringify", data => JSON.stringify(data, null, 2));

  return {
    dir: {
      input: "src",
      output: "public",
    }
  };
}