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
				var menu_list = keys.map(key => {
					var subentries = [...new Set(
						entries
						.filter(entry => entry[key])
						.flatMap(entry => entry[key])
					)].sort().map(entry => ({title: entry, url: `${key}/${entry}/`, }));

					return {title: capitalize(key), entries: subentries};
				});
				
				menu_list.unshift({title: "All", url: "all/"});

				return menu_list;
			},
		}
	}
}
