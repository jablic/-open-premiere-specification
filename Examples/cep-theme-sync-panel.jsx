// CEP Panel Host Script (ExtendScript)
// Runs in the Premiere Pro host process to support the CEP panel's theme-sync requests
// Called from the CEP client HTML/JS via CSInterface.evalScript()

function getPanelThemeInfo() {
  // Retrieve the current host environment's theme/skin information.
  // This is called by the CEP panel when it loads or detects a theme change event.
  // Returns a JSON string with color/font info the panel can apply to its own DOM.

  try {
    var hostEnv = (new CSInterface()).getHostEnvironment();
    var skinInfo = hostEnv.appSkinInfo;

    // panelBackgroundColor is an object: {red: 0-255, green: 0-255, blue: 0-255, alpha: 0-255}
    // Convert to RGB or hex string for the panel to use.
    var bgColor = rgbToHex(skinInfo.panelBackgroundColor);
    var fontSize = skinInfo.baseFontSize || 12;
    var fontFamily = skinInfo.baseFontFamily || 'Segoe UI, Arial, sans-serif';

    return JSON.stringify({
      success: true,
      panelBackgroundColor: bgColor,
      fontSize: fontSize,
      fontFamily: fontFamily,
      appSkinInfo: skinInfo  // return raw for advanced use
    });
  } catch (e) {
    return JSON.stringify({
      success: false,
      error: e.toString()
    });
  }
}

function rgbToHex(colorObj) {
  // Convert Adobe's color object {red, green, blue, alpha} to #RRGGBB hex string
  if (!colorObj) return '#FFFFFF';
  var r = Math.round(colorObj.red || 0).toString(16).padStart(2, '0');
  var g = Math.round(colorObj.green || 0).toString(16).padStart(2, '0');
  var b = Math.round(colorObj.blue || 0).toString(16).padStart(2, '0');
  return '#' + r.toUpperCase() + g.toUpperCase() + b.toUpperCase();
}

// When called from the panel via evalScript, return the JSON result
getPanelThemeInfo();
