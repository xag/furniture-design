# MDN: Element: pointercancel event

https://developer.mozilla.org/en-US/docs/Web/API/Element/pointercancel_event

From the introduction, the event fires

> if after the pointerdown event is fired, the pointer is then used to manipulate the viewport by panning, zooming, or scrolling.

Among the listed situations:

> The touch-action CSS property prevents the input from continuing.

(No `pointerup` follows a `pointercancel` for that pointer.)
