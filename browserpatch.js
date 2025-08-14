(async () => {
	let tilesconfig = await (await fetch("http://localhost:8000/wplace/config.json", {cache: 'reload'})).json();
	console.log(tilesconfig);
	fetch = new Proxy(fetch, {
		apply: (target, thisArg, argList) => {
			console.log(target, thisArg, argList);
			if (!argList[0]) {
				throw new Error("No URL provided to fetch");
			}

			const urlString = typeof argList[0] === "object" ? argList[0].url : argList[0];
			let url;

			try {
				url = new URL(urlString);
			} catch (e) {
				throw new Error("Invalid URL provided to fetch");
			}
			if (url.pathname !== "/wplace/config.json") {
				var match = false;
				for (const configentry of tilesconfig) {
					if (url.pathname === "/files/s0/tiles/" + configentry[0] + "/" + configentry[1] + ".png") {
						match = true;
						break;
					}
				}

				if (url.hostname === "backend.wplace.live" && match) {
					url.host = "localhost:8000";
					url.protocol = "http";
                    url.pathname = "/wplace" + url.pathname;
					console.log("Modified URL:", url);

					if (typeof argList[0] === "object") {
						argList[0] = new Request(url, argList[0]);
					} else {
						argList[0] = url.toString();
					}
				}
			}
			return target.apply(thisArg, argList);
		}
	});
})();