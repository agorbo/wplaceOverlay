# wplaceOverlay
- This is an overlay for [wplace](https://wplace.live/)
- It reads blueprint files and will display the difference if the canvas is out of sync
- I am not associated with wplace. If you use this code to violate the terms of use, do so at your own risk

# Usage
### Setup config.json
- The config.json defines which areas you want to include in the overlay
- To obtain the path of the wplace backend files, open the network tab of your browser (F12, Network), and navigate to the respective area on the map. It will show up as one of the .png files. Find yours, and look at the path.
- Add the last 2 numbers of the .png path **as one separate entry** to your config.json
- Example: `https://backend.wplace.live/files/s0/tiles/1100/670.png` => `[ ["1100","670"], ... ]`

### Run server
- Execute main.py in python
- It will calculate the overlay and start an http server, which serves it to your browser
- Keep this running while you want to use the overlay
 
### Adjust blueprints
- In the ./blueprints folder there will be a copy of the canvas, created when you initially added its path to the config
- Edit this (e.g. in GIMP) to only keep pixels you want to include in your overlay

### Patch browser
- The javascript browser patch is inspired by [cfp](https://github.com/cfpwastaken/wplace-overlay)
- **EITHER** paste the contents of `browserpatch.js` into your browser console every time you want to activate the overlay,
- **OR** add a bookmark to your browser, make it point to `javascript:` and paste the browserpatch.js file contents there. This only needs to be clicked then to activate the overlay.
