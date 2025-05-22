function capitalize(string) {
	return string.charAt(0).toUpperCase() + string.slice(1);
}

export default {
	eleventyComputed: {
		media: {
			categoriesMenuList: ({ entries, keys }) => {
				if(entries == null || keys == null) {
					return null;
				}
				return keys.map(key => {
					var subentries = [...new Set(
						entries
						.filter(entry => entry[key])
						.flatMap(entry => entry[key])
					)].map(entry => ({title: entry, url: `${key}/${entry}/`, }));

					return {title: capitalize(key), entries: subentries};
				});
			},
		}
	}
}
