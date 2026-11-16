# Google model-viewer examples: Annotations, "Show Dimensions"

https://modelviewer.dev/examples/annotations/index.html (page source, lines 305–359 and 393–412)

> Here we demonstrate using hotspots to show a model's dimensions, entirely styled with CSS. A JavaScript function is used to automatically set the dimension values by querying the <model-viewer> element.

> by using an SVG canvas and updating the line nodes we can draw rudimentary dimension lines. Note that this kind of extended functionality cannot support occlusion in the 3D scene, as it always draws on top of the model.

> Note that because the text is not part of the 3D rendering it is easier to read and more accessible.

The control that shows them:

```html
<label for="show-dimensions">Show Dimensions:</label>
<input id="show-dimensions" type="checkbox" checked="true">
```

What it measures: the model's bounding box only (`modelViewer.getDimensions()`), one number per axis, on five candidate box edges; each line is hidden when its hotspot is not facing the camera:

```js
if (dimensionHotspot && !dimensionHotspot.facingCamera) {
  svgLine.classList.add('hide');
}
```
